from sqlalchemy import Column, Integer, String, BigInteger, Text, JSON, Boolean, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.shared.database import Base
import enum

class AuthProvider(str, enum.Enum):
    LOCAL = "LOCAL"
    LARK = "LARK"

# Association Table for Role <-> PagePermission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("page_permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    permissions = relationship("PagePermission", secondary=role_permissions, backref="roles")
    users = relationship("AdminUser", back_populates="role_obj")

class PagePermission(Base):
    __tablename__ = "page_permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # Display Name
    code = Column(String, unique=True, index=True, nullable=False) # Code for frontend check

    # Relationships
    api_permissions = relationship("ApiPermission", back_populates="page_permission", cascade="all, delete-orphan")

class ApiPermission(Base):
    __tablename__ = "api_permissions"

    id = Column(Integer, primary_key=True, index=True)
    page_permission_id = Column(Integer, ForeignKey("page_permissions.id", ondelete="CASCADE"))
    method = Column(String, nullable=False) # GET, POST, PUT, DELETE, *
    path = Column(String, nullable=False) # Regex or exact path

    # Relationships
    page_permission = relationship("PagePermission", back_populates="api_permissions")

class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True) # Nullable for Lark users
    
    # Store role name as string for backward compatibility or simple check
    # But ideally validation should link to Role ID
    role = Column(String, default="USER") 
    
    # New FK to Role table
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role_obj = relationship("Role", back_populates="users")

    authProvider = Column(String, default=AuthProvider.LOCAL.value) # Stored as string
    
    # Extra fields
    full_name = Column(String, nullable=True)
    lark_user_id = Column(String, nullable=True)
    lark_open_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(BigInteger, nullable=True)
