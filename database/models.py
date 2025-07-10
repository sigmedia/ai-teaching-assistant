from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Index, update
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import event

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        Index('idx_session', 'SessionID'),
    )
    Id = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(64), unique=True, nullable=False)
    Active = Column(Boolean(1), default=True, nullable=False)
    HasAgreedToPart1 = Column(Boolean(1), default=False, nullable=False)
    AgreementPart1Version = Column(String(64), nullable=False)
    HasAgreedToPart2 = Column(Boolean(1), default=False, nullable=False)
    AgreementPart2Version = Column(String(64), nullable=False)
    DateAgreedToPart1 = Column(DateTime(timezone=True), server_default=func.GETUTCDATE(), nullable=False)
    DateAgreedToPart2 = Column(DateTime(timezone=True), server_default=func.GETUTCDATE(), nullable=False)
    DateCreated = Column(DateTime(timezone=True), server_default=func.GETUTCDATE(), nullable=False)
    DateUpdated = Column(DateTime(timezone=True), onupdate=func.GETUTCDATE(), server_default=func.GETUTCDATE(), nullable=False)
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        Index('idx_messages_session_date', 'SessionID', 'DateCreated'),
    )
    Id = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(64), ForeignKey('sessions.SessionID'), nullable=False)
    IsBot = Column(Boolean(1), nullable=False)
    MessageText = Column(Text(), nullable=True)
    DateCreated = Column(DateTime(timezone=True), server_default=func.GETUTCDATE(), nullable=False)
    session = relationship("Session", back_populates="messages")

@event.listens_for(Message, 'after_insert')
def update_project_timestamp(mapper, connection, target):
    connection.execute(
        update(Session)
        .where(Session.SessionID == target.SessionID)
        .values(DateUpdated=func.current_timestamp())
    )