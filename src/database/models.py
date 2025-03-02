from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    skill = Column(String, nullable=False)
    experience = Column(String, nullable=False)
    registration_time = Column(DateTime, default=datetime.utcnow)
    is_waiting = Column(Boolean, default=True)
    
    # Relationships
    team_memberships = relationship("TeamMember", back_populates="user")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, skill={self.skill})>"


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_confirmed = Column(Boolean, default=False)
    chat_id = Column(BigInteger, nullable=True)
    
    # Relationships
    members = relationship("TeamMember", back_populates="team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, is_confirmed={self.is_confirmed})>"


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    has_confirmed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="team_memberships")
    team = relationship("Team", back_populates="members")
    
    def __repr__(self):
        return f"<TeamMember(user_id={self.user_id}, team_id={self.team_id}, has_confirmed={self.has_confirmed})>"


# Initialize database
engine = create_engine(config.DATABASE_URL)

# Drop all tables and recreate them
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
