"""
一次性脚本：创建初始管理员用户

在命令行中运行此脚本以在数据库中添加一个管理员账户。
"""
import argparse
from sqlalchemy.orm import Session
from domain.database import SessionLocal, init_db
from application.services.user_service import user_service
from application.schemas import AdminCreate
from utils.logger import log

def create_initial_admin(db: Session, username: str, password: str):
    """
    创建或更新管理员用户。
    """
    log.info(f"正在检查用户 '{username}' 是否存在...")
    existing_user = user_service.get_user_by_username(db, username)
    
    if existing_user:
        log.warning(f"用户 '{username}' 已存在。此脚本不会更新现有用户的密码。")
        return

    log.info(f"用户 '{username}' 不存在，正在创建新用户...")
    admin_in = AdminCreate(username=username, password=password)
    user_service.create_admin_user(db, user=admin_in)
    log.info(f"管理员用户 '{username}' 创建成功。")

def main():
    """
    主函数，解析命令行参数并执行创建逻辑。
    """
    parser = argparse.ArgumentParser(description="创建 SecureDrop 初始管理员用户。")
    parser.add_argument(
        "--username", 
        type=str, 
        default="verne", 
        help="管理员的用户名 (默认为: admin)"
    )
    parser.add_argument(
        "--password", 
        type=str, 
        required=True, 
        help="管理员的密码 (必需)"
    )
    args = parser.parse_args()

    # 初始化数据库连接和表
    init_db()
    
    db = SessionLocal()
    try:
        create_initial_admin(db, username=args.username, password=args.password)
    finally:
        db.close()

if __name__ == "__main__":
    main()
