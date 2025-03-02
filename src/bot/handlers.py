from telegram import Update
from telegram.ext import ContextTypes
import sys
import os
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database import operations
from src.services import matcher, team_manager
from src.bot import keyboards, messages

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User state dictionary
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    try:
        logger.info(f"Start command received from user {update.effective_user.id}")
        
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # Check if user is already registered
        logger.info(f"Checking if user {user_id} is registered")
        existing_user = operations.get_user_by_telegram_id(user_id)
        logger.info(f"User exists: {existing_user is not None}")
        
        if existing_user:
            # Check if user is already in a team or waiting for confirmation
            is_in_active_team = not existing_user.is_waiting
            logger.info(f"User is in active team: {is_in_active_team}")
            
            if is_in_active_team:
                # User is already in a team or waiting for confirmation, don't allow changes
                await update.message.reply_text(
                    "You're already part of a team or waiting for team confirmation. "
                    "You cannot change your registration details at this time."
                )
            else:
                # User is registered but not in a team, allow editing
                await update.message.reply_text(
                    messages.get_already_registered_message(existing_user.skill, existing_user.experience),
                    reply_markup=keyboards.get_edit_registration_keyboard()
                )
        else:
            # New user, start registration process
            logger.info(f"Starting registration for new user {user_id}")
            user_states[user_id] = {"step": "skill_selection"}
            
            # Send welcome message with skill selection keyboard
            await update.message.reply_text(
                messages.get_welcome_message(),
                reply_markup=keyboards.get_skill_keyboard()
            )
            logger.info(f"Welcome message sent to user {user_id}")
    except Exception as e:
        logger.error(f"Error in start command handler: {e}", exc_info=True)
        # Try to send a simple message to the user
        try:
            await update.message.reply_text(
                "Sorry, something went wrong. Please try again later or contact the administrator."
            )
        except Exception as inner_e:
            logger.error(f"Failed to send error message: {inner_e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    data = query.data
    
    await query.answer()
    
    # Handle edit registration request
    if data == "edit_registration":
        # Check if user is already in a team or waiting for confirmation
        existing_user = operations.get_user_by_telegram_id(user_id)
        if existing_user and not existing_user.is_waiting:
            await query.edit_message_text(
                "You're already part of a team or waiting for team confirmation. "
                "You cannot change your registration details at this time."
            )
            return
        
        # Start the registration process again
        user_states[user_id] = {"step": "skill_selection"}
        
        # Show skill selection keyboard
        await query.edit_message_text(
            "Let's update your registration. Please select your primary skill:",
            reply_markup=keyboards.get_skill_keyboard()
        )
    
    # Handle cancel edit request
    elif data == "cancel_edit":
        await query.edit_message_text(
            "Registration update cancelled. Your existing registration remains unchanged."
        )
    
    # Handle skill selection
    elif data.startswith("skill_"):
        # Check if user is already in a team or waiting for confirmation
        existing_user = operations.get_user_by_telegram_id(user_id)
        if existing_user and not existing_user.is_waiting:
            await query.edit_message_text(
                "You're already part of a team or waiting for team confirmation. "
                "You cannot change your registration details at this time."
            )
            return
            
        skill = data.replace("skill_", "")
        
        # Update user state
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id]["skill"] = skill
        user_states[user_id]["step"] = "experience_selection"
        
        # Ask for experience level
        await query.edit_message_text(
            messages.get_experience_message(),
            reply_markup=keyboards.get_experience_keyboard()
        )
    
    # Handle experience selection
    elif data.startswith("exp_"):
        # Check if user is already in a team or waiting for confirmation
        existing_user = operations.get_user_by_telegram_id(user_id)
        if existing_user and not existing_user.is_waiting:
            await query.edit_message_text(
                "You're already part of a team or waiting for team confirmation. "
                "You cannot change your registration details at this time."
            )
            return
            
        experience = data.replace("exp_", "")
        
        # Check if user has selected a skill
        if user_id not in user_states or "skill" not in user_states[user_id]:
            await query.edit_message_text(
                "Something went wrong. Please start again with /start"
            )
            return
        
        skill = user_states[user_id]["skill"]
        
        # Check if this is an update to an existing registration
        is_update = existing_user is not None
        
        # Create or update user in database
        operations.create_user(user_id, username, skill, experience)
        
        # Send confirmation message with information about batch matching
        if is_update:
            await query.edit_message_text(
                f"✅ Registration updated!\n\n"
                f"Your skill: {skill}\n"
                f"Your experience: {experience}\n\n"
                f"You've been added to the waiting list. Team matching happens every 2 hours. "
                f"We'll notify you when you've been matched with a team!"
            )
        else:
            await query.edit_message_text(
                f"✅ Registration complete!\n\n"
                f"Your skill: {skill}\n"
                f"Your experience: {experience}\n\n"
                f"You've been added to the waiting list. Team matching happens every 2 hours. "
                f"We'll notify you when you've been matched with a team!"
            )
        
        # No longer trying to match teams immediately
        # await try_match_teams(context)
    
    # Handle team confirmation
    elif data.startswith("confirm_"):
        _, team_id, response = data.split("_")
        team_id = int(team_id)
        confirmed = (response == "yes")
        
        # Handle team confirmation
        is_team_confirmed = team_manager.handle_team_confirmation(user_id, team_id, confirmed)
        
        if confirmed:
            if is_team_confirmed:
                # All members confirmed, notify them
                await query.edit_message_text(messages.get_team_confirmed_message())
                
                # Create a group chat for the team
                await create_team_chat(context, team_id)
            else:
                # Still waiting for other members
                await query.edit_message_text(
                    "Thanks for confirming! Waiting for other team members to confirm..."
                )
        else:
            # User declined, notify them
            await query.edit_message_text(
                "You've declined the team. You've been added back to the waiting list."
            )

async def try_match_teams(context: ContextTypes.DEFAULT_TYPE):
    """Try to match teams and notify users"""
    potential_team = matcher.find_potential_team()
    
    if potential_team:
        # Create a team
        team = team_manager.create_team_from_users(potential_team)
        
        # Notify each team member
        for user in potential_team:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=messages.get_team_match_message(),
                    reply_markup=keyboards.get_confirmation_keyboard(team.id)
                )
            except Exception as e:
                logger.error(f"Failed to send message to user {user.telegram_id}: {e}")

async def create_team_chat(context: ContextTypes.DEFAULT_TYPE, team_id):
    """Notify team members about their teammates"""
    team_info = team_manager.get_team_info(team_id)
    
    if not team_info or not team_info["is_confirmed"]:
        return
    
    try:
        # For each team member, send them information about their teammates
        for member in team_info["members"]:
            # Get this member's teammates (everyone except themselves)
            teammates = [m for m in team_info["members"] if m["telegram_id"] != member["telegram_id"]]
            
            # Create a message with teammate information
            message = "🎉 Your hackathon team is confirmed! 🎉\n\n"
            message += "Here are your teammates:\n\n"
            
            for teammate in teammates:
                username = teammate["username"] or "No username"
                message += f"• @{username} - {teammate['skill']} ({teammate['experience']})\n"
            
            message += "\nWe recommend creating a group chat with your teammates to coordinate your hackathon project. Good luck! 🚀"
            
            # Send the message to this team member
            try:
                await context.bot.send_message(
                    chat_id=member["telegram_id"],
                    text=message
                )
            except Exception as e:
                logger.error(f"Failed to notify user {member['telegram_id']}: {e}")
        
        # Mark the team as confirmed in the database
        operations.set_team_confirmation(team_id, True)
        
    except Exception as e:
        logger.error(f"Failed to notify team members: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates"""
    logger.error(f"Update {update} caused error {context.error}")
