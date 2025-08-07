"""
文件服务模块

处理文件上传、下载、带宽限制等相关的业务逻辑。
"""
import os
from fastapi import UploadFile, HTTPException, status
from domain.storage import storage_service
from domain.models import Token
from utils.logger import log

class FileService:
    """
    封装文件处理的核心业务逻辑。
    """

    def _handle_filename_conflict(
        self, destination_path: str, strategy: str
    ) -> str:
        """
        根据策略处理文件名冲突。
        """
        if not storage_service.file_exists(destination_path):
            return destination_path

        if strategy == 'overwrite':
            log.warning(f"文件名冲突，将覆盖文件: {destination_path}")
            return destination_path
        
        if strategy == 'reject':
            log.error(f"文件名冲突，拒绝上传: {destination_path}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"文件 '{os.path.basename(destination_path)}' 已存在。"
            )

        # 默认策略: rename
        base, ext = os.path.splitext(destination_path)
        counter = 1
        new_path = f"{base}_{counter}{ext}"
        while storage_service.file_exists(new_path):
            counter += 1
            new_path = f"{base}_{counter}{ext}"
        log.info(f"文件名冲突，重命名为: {new_path}")
        return new_path

    def _validate_file(self, file: UploadFile, policy: Token):
        """
        根据令牌策略验证文件。
        """
        # 验证文件大小
        if policy.max_file_size_mb is not None:
            max_size_bytes = policy.max_file_size_mb * 1024 * 1024
            if file.size > max_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"文件大小超过限制 ({policy.max_file_size_mb} MB)。"
                )
        
        # 验证文件类型
        if policy.allowed_file_types:
            allowed_types = [t.strip() for t in policy.allowed_file_types.split(',')]
            file_ext = os.path.splitext(file.filename)[1]
            if file_ext.lower() not in [t.lower() for t in allowed_types]:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"不支持的文件类型。允许的类型: {policy.allowed_file_types}"
                )

    def upload_file(self, file: UploadFile, policy: Token) -> str:
        """
        处理文件上传的完整流程。
        """
        self._validate_file(file, policy)

        upload_rel_path = policy.upload_path or ""
        destination_path = os.path.join(upload_rel_path, file.filename)

        final_path = self._handle_filename_conflict(
            destination_path, policy.filename_conflict_strategy
        )

        saved_path = storage_service.save_file(file, final_path)
        return os.path.basename(saved_path)

# 创建一个服务实例
file_service = FileService()
