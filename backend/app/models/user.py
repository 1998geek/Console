from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    # Map "password" column from DB to hashed_password attribute
    hashed_password = Column("password", String)
    
    # 远程数据库中不存在 is_active 和 is_admin 字段
    # SQLAlchemy 会尝试选择所有 Column 定义的字段，所以必须删除 Column 定义
    # 改为纯 Python 属性
    
    @property
    def is_active(self):
        return True
        
    @property
    def is_admin(self):
        # 简单逻辑：如果是 admin 用户名则是管理员
        return self.username == "admin"
