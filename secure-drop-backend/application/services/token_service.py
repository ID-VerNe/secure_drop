"""
令牌服务模块

处理令牌的创建、验证、使用等核心逻辑。
"""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from domain import models
from application import schemas
from utils.logger import log

class TokenService:
    """
    封装令牌相关的数据库操作和业务逻辑。
    """

    def _generate_token_string(self) -> str:
        """
        生成一个格式化的唯一令牌字符串。
        格式: XXXX-XXXX-XXXX-XXXX
        """
        return str(uuid.uuid4()).upper().replace('-', '')[:16]

    def create_token(self, db: Session, token_in: schemas.TokenCreate) -> models.Token:
        """
        创建一个新的访问令牌。

        Args:
            db: 数据库会话。
            token_in: 包含令牌策略的 Pydantic 模型。

        Returns:
            models.Token: 创建的 Token 模型实例。
        """
        token_string = self._generate_token_string()
        db_token = models.Token(
            **token_in.model_dump(),
            token_string=token_string
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        log.info(f"成功创建新令牌: {token_string}")
        return db_token

    def get_token_by_id(self, db: Session, token_id: int) -> Optional[models.Token]:
        """
        根据 ID 获取令牌。
        """
        return db.query(models.Token).filter(models.Token.id == token_id).first()

    def get_all_tokens(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Token]:
        """
        获取所有令牌的列表，支持分页。
        """
        return db.query(models.Token).offset(skip).limit(limit).all()

    def get_tokens_count(self, db: Session) -> int:
        """
        获取令牌总数。
        """
        return db.query(models.Token).count()

    def update_token(
        self, db: Session, token_id: int, token_in: schemas.TokenUpdate
    ) -> Optional[models.Token]:
        """
        更新一个令牌的策略。
        """
        db_token = self.get_token_by_id(db, token_id)
        if not db_token:
            return None
        
        update_data = token_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_token, key, value)
        
        db.commit()
        db.refresh(db_token)
        log.info(f"令牌 ID {token_id} 已更新。")
        return db_token

    def delete_token(self, db: Session, token_id: int) -> bool:
        """
        删除一个令牌。
        """
        db_token = self.get_token_by_id(db, token_id)
        if not db_token:
            return False
        
        db.delete(db_token)
        db.commit()
        log.info(f"令牌 ID {token_id} 已删除。")
        return True

    def revoke_token(self, db: Session, token_id: int) -> Optional[models.Token]:
        """
        手动撤销一个令牌。
        """
        db_token = self.get_token_by_id(db, token_id)
        if not db_token:
            return None
        
        db_token.status = "revoked"
        db.commit()
        db.refresh(db_token)
        log.info(f"令牌 ID {token_id} 已被撤销。")
        return db_token

# 创建一个服务实例
token_service = TokenService()
