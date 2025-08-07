"""
用户服务模块

处理与管理员账户相关的业务逻辑。
"""
from sqlalchemy.orm import Session
from typing import Optional
from domain import models
from application import schemas
from utils.security import get_password_hash

class UserService:
    """
    封装管理员用户相关的数据库操作。
    """

    def get_user_by_username(self, db: Session, username: str) -> Optional[models.Admin]:
        """
        根据用户名查询管理员。

        Args:
            db: 数据库会话。
            username: 管理员用户名。

        Returns:
            Optional[models.Admin]: 如果找到则返回 Admin 模型实例，否则返回 None。
        """
        return db.query(models.Admin).filter(models.Admin.username == username).first()

    def create_admin_user(self, db: Session, user: schemas.AdminCreate) -> models.Admin:
        """
        创建一个新的管理员用户。

        Args:
            db: 数据库会话。
            user: 包含用户名和密码的 Pydantic 模型。

        Returns:
            models.Admin: 创建的 Admin 模型实例。
        """
        hashed_password = get_password_hash(user.password)
        db_user = models.Admin(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

# 创建一个服务实例，以便在其他地方直接导入和使用
user_service = UserService()
