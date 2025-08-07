"""
安全相关工具模块

包含密码哈希处理和 JWT 令牌的生成与验证功能。
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings
from .logger import log

# 创建一个 CryptContext 实例，用于密码哈希
# "bcrypt" 是推荐的算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配。

    Args:
        plain_password: 用户输入的明文密码。
        hashed_password: 数据库中存储的哈希密码。

    Returns:
        bool: 如果密码匹配则返回 True，否则返回 False。
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    对明文密码进行哈希处理。

    Args:
        password: 用户输入的明文密码。

    Returns:
        str: 哈希后的密码字符串。
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌。

    Args:
        data: 要编码到令牌中的数据 (payload)。
        expires_delta: 令牌的有效期。如果未提供，将使用默认值。

    Returns:
        str: 生成的 JWT 令牌字符串。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码并验证 JWT 访问令牌。

    Args:
        token: JWT 令牌字符串。

    Returns:
        Optional[dict]: 如果令牌有效，则返回 payload；否则返回 None。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        log.warning(f"JWT 解码失败: {e}")
        return None
