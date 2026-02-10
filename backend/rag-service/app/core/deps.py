# ============================================================
# Dependencies
# ============================================================

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_new_db_session() -> Session:
    """
    获取新的数据库会话（用于后台任务）

    注意：调用者负责关闭会话

    Returns:
        新的数据库会话
    """
    return SessionLocal()
