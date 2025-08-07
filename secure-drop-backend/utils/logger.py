"""
日志配置模块

配置全局日志记录器。
"""
import logging
import sys
from .config import settings

def setup_logger():
    """
    配置并返回一个日志记录器实例。
    """
    logger = logging.getLogger("secure_drop")
    logger.propagate = False  # 防止日志向上传播到根记录器

    # 如果已经有处理器，则不重复添加，避免日志重复输出
    if logger.hasHandlers():
        return logger

    # 设置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 创建一个流处理器，将日志输出到标准错误
    handler = logging.StreamHandler(sys.stderr)
    
    # 定义日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # 将处理器添加到记录器
    logger.addHandler(handler)

    return logger

# 创建一个全局可用的日志实例
log = setup_logger()
