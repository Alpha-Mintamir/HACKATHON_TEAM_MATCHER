from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

from src.database.models import Base, User, Team, TeamMember
import config

# Create database engine and session
engine = create_engine(config.DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# User operations
def create_user(telegram_id, username, skill, experience):
    """Create a new user in the database"""
    db = get_db()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        existing_user.skill = skill
        existing_user.experience = experience
        existing_user.is_waiting = True
        db.commit()
        return existing_user
    
    # Create new user
    user = User(
        telegram_id=telegram_id,
        username=username,
        skill=skill,
        experience=experience,
        registration_time=datetime.utcnow(),
        is_waiting=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_waiting_users():
    """Get all users who are waiting for a team"""
    db = get_db()
    return db.query(User).filter(User.is_waiting == True).order_by(User.registration_time).all()

def get_user_by_telegram_id(telegram_id):
    """Get a user by their Telegram ID"""
    try:
        db = get_db()
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        db.close()  # Close the session
        return user
    except Exception as e:
        import logging
        logging.error(f"Error getting user by Telegram ID: {e}", exc_info=True)
        return None

def update_user_waiting_status(user_id, is_waiting):
    """Update a user's waiting status"""
    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_waiting = is_waiting
        db.commit()
        return True
    return False

# Team operations
def create_team():
    """Create a new team"""
    db = get_db()
    team = Team(created_at=datetime.utcnow())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def add_user_to_team(user_id, team_id):
    """Add a user to a team"""
    db = get_db()
    team_member = TeamMember(user_id=user_id, team_id=team_id)
    db.add(team_member)
    db.commit()
    db.refresh(team_member)
    return team_member

def set_team_confirmation(team_id, is_confirmed):
    """Set a team's confirmation status"""
    db = get_db()
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        team.is_confirmed = is_confirmed
        db.commit()
        return True
    return False

def set_team_chat_id(team_id, chat_id):
    """Set a team's chat ID"""
    db = get_db()
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        team.chat_id = chat_id
        db.commit()
        return True
    return False

def set_member_confirmation(user_id, team_id, has_confirmed):
    """Set a team member's confirmation status"""
    db = get_db()
    team_member = db.query(TeamMember).filter(
        TeamMember.user_id == user_id,
        TeamMember.team_id == team_id
    ).first()
    
    if team_member:
        team_member.has_confirmed = has_confirmed
        db.commit()
        return True
    return False

def get_team_members(team_id):
    """Get all members of a team"""
    db = get_db()
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

def get_team_by_id(team_id):
    """Get a team by its ID"""
    db = get_db()
    return db.query(Team).filter(Team.id == team_id).first()

def delete_team(team_id):
    """Delete a team and its members"""
    db = get_db()
    # Delete team members first
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    # Then delete the team
    db.query(Team).filter(Team.id == team_id).delete()
    db.commit()
    return True
