"""
文件存储抽象接口及实现

定义了文件存储的抽象基类和本地文件存储的具体实现。
"""
import os
import shutil
from abc import ABC, abstractmethod
from fastapi import UploadFile
from utils.config import settings
from utils.logger import log

class StorageInterface(ABC):
    """
    文件存储的抽象基类 (接口)。
    """
    @abstractmethod
    def save_file(self, file: UploadFile, destination_path: str) -> str:
        """
        保存上传的文件。

        Args:
            file: FastAPI 的 UploadFile 对象。
            destination_path: 文件保存的目标相对路径。

        Returns:
            str: 保存后的完整文件路径。
        """
        pass

    @abstractmethod
    def get_file_path(self, file_path: str) -> str:
        """
        获取文件的完整物理路径。

        Args:
            file_path: 文件的相对路径。

        Returns:
            str: 文件的绝对路径。
        """
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在。
        """
        pass

class LocalStorage(StorageInterface):
    """
    本地文件存储的实现。
    """
    def __init__(self, base_path: str = settings.STORAGE_PATH):
        self.base_path = os.path.abspath(base_path)
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            log.info(f"本地存储目录已创建: {self.base_path}")

    def save_file(self, file: UploadFile, destination_path: str) -> str:
        """
        将上传的文件保存到本地。
        """
        # 安全地拼接路径，防止路径遍历攻击
        full_dest_path = os.path.join(self.base_path, destination_path)
        
        # 创建目标目录（如果不存在）
        os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
        
        try:
            with open(full_dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            log.info(f"文件已保存到: {full_dest_path}")
            return full_dest_path
        finally:
            file.file.close()

    def get_file_path(self, file_path: str) -> str:
        """
        获取本地文件的完整路径。
        """
        return os.path.join(self.base_path, file_path)

    def file_exists(self, file_path: str) -> bool:
        """
        检查本地文件是否存在。
        """
        return os.path.exists(self.get_file_path(file_path))

# 创建一个全局可用的存储实例
storage_service = LocalStorage()
