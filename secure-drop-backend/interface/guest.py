"""
访客文件操作 API 端点

包括使用令牌登录、获取文件列表、上传和下载文件。
"""
import json
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from sqlalchemy.orm import Session
from typing import Optional, List

from application import schemas
from application.services.token_service import token_service
from application.services.file_service import file_service
from domain.database import get_db
from domain.models import Token
from utils.security import create_access_token, decode_access_token
from fastapi.responses import FileResponse
from domain.storage import storage_service
from utils.logger import log

router = APIRouter(
    prefix="/api/guest",
    tags=["Guest - File Exchange"],
)

def validate_token_string(db: Session, token_string: str) -> Token:
    """
    验证令牌字符串的有效性（存在、状态、有效期、使用次数）。
    这是一个通用的验证函数，可以在多个地方复用。
    """
    # 这里可以应用责任链模式来重构
    token = db.query(Token).filter(Token.token_string == token_string).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="令牌无效")
    if token.status != 'unused' and token.status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"令牌状态为 {token.status}")
    # ... 其他验证逻辑，如有效期、使用次数等
    return token

@router.post("/login", response_model=schemas.GuestSession)
def guest_login(
    login_data: schemas.GuestLoginRequest,
    db: Session = Depends(get_db)
):
    """
    访客使用令牌登录，获取一个临时的会话 JWT 和权限策略。
    """
    token = validate_token_string(db, login_data.token_string)
    
    # 创建一个临时的会话 JWT，有效期较短
    session_jwt = create_access_token(
        data={"sub": token.token_string, "type": "session"},
        expires_delta=timedelta(hours=1) # 例如，会话有效期为1小时
    )
    
    log.info(f"访客使用令牌 '{login_data.token_string}' 成功登录。")
    
    # 返回会话令牌和该令牌的策略
    return {
        "session_token": session_jwt,
        "policy": token
    }

async def get_current_guest_token(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> Token:
    """
    依赖项：验证访客的会话 JWT，并返回其对应的数据库令牌对象。
    """
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="需要认证")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证头部")

    payload = decode_access_token(parts[1])
    if payload is None or payload.get("type") != "session":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的会话令牌")
    
    token_string = payload.get("sub")
    token = validate_token_string(db, token_string)
    return token

import os

@router.get("/files", response_model=List[str])
def get_downloadable_files(
    token: Token = Depends(get_current_guest_token)
):
    """
    获取当前令牌策略下可供下载的文件列表。
    """
    if not token.allow_download or not token.downloadable_path:
        return []
    
    try:
        # 获取文件夹的物理路径
        dir_path = storage_service.get_file_path(token.downloadable_path)
        if not os.path.isdir(dir_path):
            log.warning(f"令牌 {token.token_string} 的下载路径不是一个有效的目录: {dir_path}")
            return []
        
        # 列出目录下的所有文件（非文件夹）
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        return files
    except Exception as e:
        log.error(f"获取文件列表时出错: {e}")
        return []

@router.post("/upload", response_model=schemas.MessageResponse)
async def upload_file(
    file: UploadFile = File(...),
    token: Token = Depends(get_current_guest_token)
):
    """
    上传文件。
    """
    if not token.allow_upload:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此令牌不允许上传")
    
    log.info(f"令牌 '{token.token_string}' 正在上传文件: {file.filename}")
    
    final_filename = file_service.upload_file(file, token)
    
    return {"message": "文件上传成功", "filename": final_filename}

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    token: Token = Depends(get_current_guest_token)
):
    """
    下载指定的文件。
    """
    if not token.allow_download:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此令牌不允许下载")

    # 现在我们不再检查 JSON 列表，而是检查文件是否在指定的目录中
    if not token.downloadable_path:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此令牌未配置下载路径")

    # 安全地构建文件路径，防止路径遍历攻击
    full_path = storage_service.get_file_path(os.path.join(token.downloadable_path, filename))
    
    # 再次检查路径是否在预期的目录下
    base_dir = storage_service.get_file_path(token.downloadable_path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_dir)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="禁止访问")

    if not os.path.isfile(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件未找到")

    log.info(f"令牌 '{token.token_string}' 正在下载文件: {filename}")
    return FileResponse(path=full_path, filename=filename, media_type='application/octet-stream')
