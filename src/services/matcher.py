import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
from src.database import operations

def find_potential_team():
    """
    Find potential team members based on skill requirements.
    Returns a list of users that can form a team, or None if not possible.
    """
    waiting_users = operations.get_waiting_users()
    
    if len(waiting_users) < config.TEAM_SIZE:
        return None
    
    # Group users by skill
    users_by_skill = {}
    for skill in config.REQUIRED_SKILLS:
        users_by_skill[skill] = [user for user in waiting_users if user.skill == skill]
    
    # Try to form a team with one user from each required skill
    team_members = []
    
    for skill in config.REQUIRED_SKILLS:
        if users_by_skill[skill]:
            # Take the user who has been waiting the longest
            team_members.append(users_by_skill[skill][0])
        else:
            # If no user with this skill, check if we can duplicate from other skills
            remaining_skills = [s for s in config.REQUIRED_SKILLS if s != skill]
            for remaining_skill in remaining_skills:
                if len(users_by_skill[remaining_skill]) > 1:
                    # Take the second user who has been waiting the longest
                    team_members.append(users_by_skill[remaining_skill][1])
                    break
            else:
                # If we can't find a replacement, we can't form a team
                return None
    
    # If we don't have enough members, we can't form a team
    if len(team_members) < config.TEAM_SIZE:
        return None
    
    return team_members[:config.TEAM_SIZE]

def create_team_from_users(users):
    """
    Create a team from a list of users.
    Returns the created team.
    """
    # Create a new team
    team = operations.create_team()
    
    # Add users to the team
    for user in users:
        operations.add_users

def check_team_confirmation(team_id):
    """
    Check if all members of a team have confirmed.
    Returns True if all members have confirmed, False otherwise.
    """
    team_members = operations.get_team_members(team_id)
    
    if not team_members:
        return False
    
    return all(member.has_confirmed for member in team_members)

def batch_match_teams():
    """
    Match multiple teams at once from the waiting users pool.
    Returns a list of created teams.
    """
    waiting_users = operations.get_waiting_users()
    created_teams = []
    
    # Group users by skill
    users_by_skill = {}
    for skill in config.REQUIRED_SKILLS:
        users_by_skill[skill] = [user for user in waiting_users if user.skill == skill]
    
    # Keep matching teams until we can't form any more
    while True:
        # Try to form a balanced team first (one from each skill)
        team_members = []
        for skill in config.REQUIRED_SKILLS:
            if users_by_skill[skill]:
                team_members.append(users_by_skill[skill][0])
                users_by_skill[skill].pop(0)
            else:
                # If we can't find a user with this skill, try to find a replacement
                found_replacement = False
                for other_skill in config.REQUIRED_SKILLS:
                    if len(users_by_skill[other_skill]) > (1 if other_skill in [m.skill for m in team_members] else 0):
                        # Use a user from another skill as replacement
                        replacement_index = 0
                        while replacement_index < len(users_by_skill[other_skill]):
                            if users_by_skill[other_skill][replacement_index].skill not in [m.skill for m in team_members]:
                                team_members.append(users_by_skill[other_skill][replacement_index])
                                users_by_skill[other_skill].pop(replacement_index)
                                found_replacement = True
                                break
                            replacement_index += 1
                        if found_replacement:
                            break
                
                if not found_replacement:
                    # If we can't find a replacement, we'll have to use a duplicate skill
                    for other_skill in config.REQUIRED_SKILLS:
                        if users_by_skill[other_skill]:
                            team_members.append(users_by_skill[other_skill][0])
                            users_by_skill[other_skill].pop(0)
                            found_replacement = True
                            break
                    
                    if not found_replacement:
                        # If we still can't find a replacement, we can't form a team
                        break
        
        # If we don't have enough members, we can't form a team
        if len(team_members) < config.TEAM_SIZE:
            # Try to form a team with whatever users we have left
            all_remaining_users = []
            for skill in config.REQUIRED_SKILLS:
                all_remaining_users.extend(users_by_skill[skill])
            
            if len(all_remaining_users) >= config.TEAM_SIZE:
                # Form a team with the first TEAM_SIZE users
                team_members = all_remaining_users[:config.TEAM_SIZE]
                
                # Remove these users from the skill groups
                for user in team_members:
                    if user in users_by_skill[user.skill]:
                        users_by_skill[user.skill].remove(user)
            else:
                # Not enough users left to form a team
                break
        
        # Create a team with these members
        if len(team_members) == config.TEAM_SIZE:
            from src.services import team_manager
            team = team_manager.create_team_from_users(team_members)
            created_teams.append((team, team_members))
        else:
            # Not enough members to form a team
            break
    
    return created_teams