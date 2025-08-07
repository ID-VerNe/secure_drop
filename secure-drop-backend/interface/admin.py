"""
管理员后台相关 API 端点

提供对访问令牌的增删改查（CRUD）功能。
所有接口都需要管理员 JWT 认证。
"""
from typing import List
import os
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from application import schemas
from application.services.token_service import token_service
from domain.storage import storage_service
from domain.database import get_db
from utils.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from utils.logger import log

router = APIRouter(
    prefix="/api/admin/tokens",
    tags=["Admin - Token Management"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/admin/login")

async def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    """
    依赖项：验证 JWT 令牌并返回当前登录的管理员用户信息。
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 在实际应用中，可能还需要从数据库验证用户是否存在或是否被禁用
    return {"username": username}

@router.get("/downloadable-dirs", response_model=List[str])
def get_downloadable_dirs(current_user: dict = Depends(get_current_admin_user)):
    """
    获取 uploads 目录下的所有子文件夹列表。
    """
    try:
        base_path = storage_service.base_path
        dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        return dirs
    except Exception as e:
        log.error(f"获取可下载目录列表时出错: {e}")
        raise HTTPException(status_code=500, detail="无法获取目录列表")

@router.post("", response_model=schemas.TokenInDB, status_code=status.HTTP_201_CREATED)
def create_token(
    token_in: schemas.TokenCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    创建一个新的访问令牌。
    """
    log.info(f"管理员 '{current_user['username']}' 正在创建新令牌。")
    return token_service.create_token(db=db, token_in=token_in)

@router.get("", response_model=schemas.PaginatedResponse)
def read_tokens(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    获取所有令牌列表，支持分页。
    """
    skip = (page - 1) * limit
    tokens = token_service.get_all_tokens(db, skip=skip, limit=limit)
    total = token_service.get_tokens_count(db)
    return {"total": total, "items": tokens}

@router.get("/{token_id}", response_model=schemas.TokenInDB)
def read_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    获取单个令牌的详细信息。
    """
    db_token = token_service.get_token_by_id(db, token_id=token_id)
    if db_token is None:
        raise HTTPException(status_code=404, detail="令牌未找到")
    return db_token

@router.put("/{token_id}", response_model=schemas.TokenInDB)
def update_token(
    token_id: int,
    token_in: schemas.TokenUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    更新一个未使用令牌的策略。
    """
    log.info(f"管理员 '{current_user['username']}' 正在更新令牌 ID: {token_id}。")
    updated_token = token_service.update_token(db, token_id=token_id, token_in=token_in)
    if updated_token is None:
        raise HTTPException(status_code=404, detail="令牌未找到")
    return updated_token

@router.post("/{token_id}/revoke", response_model=schemas.MessageResponse)
def revoke_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    手动撤销一个令牌。
    """
    log.info(f"管理员 '{current_user['username']}' 正在撤销令牌 ID: {token_id}。")
    revoked_token = token_service.revoke_token(db, token_id=token_id)
    if revoked_token is None:
        raise HTTPException(status_code=404, detail="令牌未找到")
    return {"message": "令牌已成功撤销"}

@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    删除一个令牌记录。
    """
    log.info(f"管理员 '{current_user['username']}' 正在删除令牌 ID: {token_id}。")
    success = token_service.delete_token(db, token_id=token_id)
    if not success:
        raise HTTPException(status_code=404, detail="令牌未找到")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
