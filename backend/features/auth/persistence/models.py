from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON, Boolean, Enum
from backend.shared.database import Base
import enum

class AuthProvider(str, enum.Enum):
    LOCAL = "LOCAL"
    LARK = "LARK"

class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True) # Nullable for Lark users
    role = Column(String, default="USER")
    authProvider = Column(String, default=AuthProvider.LOCAL.value) # Stored as string
    
    # Extra fields
    full_name = Column(String, nullable=True)
    lark_user_id = Column(String, nullable=True)
    lark_open_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(BigInteger, nullable=True)
