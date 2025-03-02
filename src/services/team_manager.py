import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database import operations
from src.services import matcher

def create_team_from_users(users):
    """
    Create a team from a list of users.
    Returns the created team.
    """
    # Create a new team
    team = operations.create_team()
    
    # Add users to the team
    for user in users:
        operations.add_user_to_team(user.id, team.id)
        # Mark user as not waiting
        operations.update_user_waiting_status(user.id, False)
    
    return team

def handle_team_confirmation(user_id, team_id, confirmed):
    """
    Handle a user's confirmation for a team.
    Returns True if the team is now fully confirmed, False otherwise.
    """
    # Get the user
    user = operations.get_user_by_telegram_id(user_id)
    if not user:
        return False
    
    # Set the user's confirmation status
    operations.set_member_confirmation(user.id, team_id, confirmed)
    
    if not confirmed:
        # If the user declined, delete the team and return users to waiting list
        team_members = operations.get_team_members(team_id)
        for member in team_members:
            operations.update_user_waiting_status(member.user_id, True)
        operations.delete_team(team_id)
        return False
    
    # Check if all members have confirmed
    if matcher.check_team_confirmation(team_id):
        operations.set_team_confirmation(team_id, True)
        return True
    
    return False

def create_team_chat(team_id, chat_id):
    """
    Set the chat ID for a team.
    Returns True if successful, False otherwise.
    """
    return operations.set_team_chat_id(team_id, chat_id)

def get_team_info(team_id):
    """
    Get information about a team.
    Returns a dictionary with team information.
    """
    team = operations.get_team_by_id(team_id)
    if not team:
        return None
    
    team_members = operations.get_team_members(team_id)
    members_info = []
    
    for member in team_members:
        user = member.user
        members_info.append({
            "telegram_id": user.telegram_id,
            "username": user.username,
            "skill": user.skill,
            "experience": user.experience,
            "has_confirmed": member.has_confirmed
        })
    
    return {
        "team_id": team.id,
        "is_confirmed": team.is_confirmed,
        "chat_id": team.chat_id,
        "members": members_info
    }
