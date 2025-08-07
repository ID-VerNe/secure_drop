"""
数据库 ORM 模型定义模块

定义了 `admins`, `tokens`, `access_logs` 三张表对应的 SQLAlchemy 模型。
"""
import datetime
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from .database import Base

class Admin(Base):
    """
    管理员账户模型
    """
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

class Token(Base):
    """
    访问令牌模型，包含完整的策略定义。
    """
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_string = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    status = Column(String, default='unused', nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    max_usage_count = Column(Integer, default=1)
    current_usage_count = Column(Integer, default=0)
    
    delete_on_exhaust = Column(Boolean, default=False)
    
    page_title = Column(Text, nullable=True)
    welcome_message = Column(Text, nullable=True)
    
    allow_upload = Column(Boolean, default=False)
    upload_path = Column(Text, nullable=True)
    allowed_file_types = Column(Text, nullable=True)
    max_file_size_mb = Column(Integer, nullable=True)
    max_total_upload_gb = Column(Integer, nullable=True)
    upload_bandwidth_limit_kbps = Column(Integer, default=0)
    filename_conflict_strategy = Column(String, default='rename')
    
    allow_download = Column(Boolean, default=False)
    downloadable_path = Column(Text, nullable=True) # 重命名字段
    download_bandwidth_limit_kbps = Column(Integer, default=0)
    allow_resumable_download = Column(Boolean, default=True)

    access_logs = relationship("AccessLog", back_populates="token")

class AccessLog(Base):
    """
    访问日志模型，记录所有通过令牌进行的操作。
    """
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"))
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(String)
    details = Column(Text, nullable=True)

    token = relationship("Token", back_populates="access_logs")
