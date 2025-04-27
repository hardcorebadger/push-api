from sqlalchemy import Column, String, Boolean, ARRAY, DateTime, BigInteger, ForeignKey, UniqueConstraint, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    vapid_public_key = Column(String, nullable=True)
    vapid_private_key = Column(String, nullable=True)
    vapid_subject = Column(String, nullable=True)

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    user_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', 'device_id', name='uix_devices_project_user_device'),
    )

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow) 