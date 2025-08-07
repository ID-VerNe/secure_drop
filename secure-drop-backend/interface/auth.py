"""
认证相关 API 端点

包括管理员登录和访客使用令牌登录的接口。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from application import schemas
from application.services.user_service import user_service
from utils.security import create_access_token, verify_password
from domain.database import get_db
from utils.logger import log

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

@router.post("/admin/login", response_model=schemas.JwtToken)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    管理员登录接口，使用 OAuth2PasswordRequestForm。

    通过用户名和密码进行验证，成功后返回 JWT 令牌。
    """
    log.info(f"管理员登录尝试: username='{form_data.username}'")
    user = user_service.get_user_by_username(db, username=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        log.warning(f"管理员登录失败: username='{form_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户名或密码",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    log.info(f"管理员 '{form_data.username}' 登录成功")
    return {"access_token": access_token, "token_type": "bearer"}
