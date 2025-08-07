"""
配置加载模块

使用 Pydantic 的 `BaseSettings` 来加载和验证 .env 文件中的配置。
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    应用配置类，自动从 .env 文件读取配置。
    """
    # 数据库配置
    DATABASE_URL: str

    # JWT 令牌配置
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # 文件存储配置
    STORAGE_PATH: str

    # 日志配置
    LOG_LEVEL: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例。

    使用 lru_cache 装饰器确保 `Settings` 实例在应用生命周期内只创建一次，
    实现单例模式，提高性能。

    Returns:
        Settings: 配置实例。
    """
    return Settings()

# 创建一个全局可用的配置实例
settings = get_settings()
