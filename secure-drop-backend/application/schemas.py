"""
Pydantic 模型定义模块

用于 API 的数据验证、序列化和自动文档生成。
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ================== Token Schemas ==================

class TokenBase(BaseModel):
    """
    令牌策略的基础模型，包含所有可配置的字段。
    """
    description: Optional[str] = Field(None, description="管理员备注")
    expires_at: Optional[datetime] = Field(None, description="绝对过期时间")
    max_usage_count: int = Field(1, description="最大使用次数 (0 代表无限)")
    delete_on_exhaust: bool = Field(False, description="用尽后自动删除")
    page_title: Optional[str] = Field(None, description="访客页面标题")
    welcome_message: Optional[str] = Field(None, description="访客页面欢迎信息")
    
    allow_upload: bool = Field(False, description="是否允许上传")
    upload_path: Optional[str] = Field(None, description="上传文件保存的相对路径")
    allowed_file_types: Optional[str] = Field(None, description="允许的文件类型 (逗号分隔, e.g., .jpg,.pdf)")
    max_file_size_mb: Optional[int] = Field(None, description="最大单文件大小 (MB)")
    max_total_upload_gb: Optional[int] = Field(None, description="最大总上传大小 (GB)")
    upload_bandwidth_limit_kbps: int = Field(0, description="上传带宽限制 (KB/s, 0不限制)")
    filename_conflict_strategy: str = Field('rename', description="文件名冲突策略: rename, overwrite, reject")
    
    allow_download: bool = Field(False, description="是否允许下载")
    downloadable_path: Optional[str] = Field(None, description="可供下载的文件夹路径 (相对路径)")
    download_bandwidth_limit_kbps: int = Field(0, description="下载带宽限制 (KB/s, 0不限制)")
    allow_resumable_download: bool = Field(True, description="是否允许断点续传")

class TokenCreate(TokenBase):
    """
    创建新令牌时使用的模型。
    """
    pass

class TokenUpdate(TokenBase):
    """
    更新令牌时使用的模型。
    """
    pass

class TokenInDB(TokenBase):
    """
    从数据库读取的完整令牌模型。
    """
    id: int
    token_string: str
    status: str
    created_at: datetime
    current_usage_count: int

    class Config:
        from_attributes = True # Pydantic v2, was orm_mode

class TokenPublic(BaseModel):
    """
    令牌的公开信息，用于展示给管理员。
    """
    id: int
    token_string: str
    description: Optional[str]
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    max_usage_count: int
    current_usage_count: int

    class Config:
        from_attributes = True

# ================== Admin Schemas ==================

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str

class AdminInDB(AdminBase):
    id: int
    
    class Config:
        from_attributes = True

# ================== Auth Schemas ==================

class AdminLoginRequest(BaseModel):
    """
    管理员登录请求体。
    """
    username: str
    password: str

class GuestLoginRequest(BaseModel):
    """
    访客登录请求体。
    """
    token_string: str

class JwtToken(BaseModel):
    """
    JWT 令牌响应模型。
    """
    access_token: str
    token_type: str = "bearer"

class GuestSession(BaseModel):
    """
    访客会话响应模型。
    """
    session_token: str
    policy: TokenBase

# ================== API Response Schemas ==================

class PaginatedResponse(BaseModel):
    """
    分页响应的通用模型。
    """
    total: int
    items: List[TokenPublic]

class MessageResponse(BaseModel):
    """
    简单的消息响应模型。
    """
    message: str
