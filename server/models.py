from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="member")  # guest, member, admin
    status = Column(String, default="pending")  # pending, approved
    created_at = Column(DateTime, default=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    memories = relationship("Memory", back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ✅ nullable for guests
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # structure, file, brainstorm
    status = Column(String, default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    context = Column(Text, nullable=True)

    user = relationship("User", back_populates="tasks")
    logs = relationship("Log", back_populates="task")
    user_logs = relationship("UserLog", back_populates="task")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(Text, nullable=False)

    task = relationship("Task", back_populates="logs")


class UserLog(Base):
    __tablename__ = "user_log"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response = Column(Text, nullable=False)  # ✅ matches DB column

    task = relationship("Task", back_populates="user_logs")


class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False, default="user")  # ✅ matches DB
    content = Column(Text, nullable=False, default="")      # ✅ matches DB
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")
