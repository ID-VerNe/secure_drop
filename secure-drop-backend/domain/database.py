"""
数据库会话管理模块

负责创建数据库引擎和会话。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import settings
from utils.logger import log

# 创建数据库引擎
# connect_args 是 SQLite 特有的，用于允许多线程访问
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 创建一个 SessionLocal 类，用于创建数据库会话实例
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个 Base 类，我们的 ORM 模型将继承这个类
Base = declarative_base()

def get_db():
    """
    FastAPI 依赖项，用于获取数据库会话。

    这个函数是一个生成器，它会在请求开始时创建一个新的数据库会话，
    在请求处理完成后关闭它。这种模式确保了每个请求都有一个独立的会话，
    并且会话最终总是会被关闭，从而释放资源。

    Yields:
        Session: SQLAlchemy 数据库会话实例。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库，创建所有在 Base 中定义的表。
    """
    log.info("正在初始化数据库，创建所有表...")
    try:
        Base.metadata.create_all(bind=engine)
        log.info("数据库表创建成功。")
    except Exception as e:
        log.error(f"创建数据库表时发生错误: {e}")
        raise
