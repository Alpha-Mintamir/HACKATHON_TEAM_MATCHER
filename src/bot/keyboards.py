from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

def get_skill_keyboard():
    """
    Create an inline keyboard for skill selection.
    """
    keyboard = []
    for skill in config.REQUIRED_SKILLS:
        keyboard.append([InlineKeyboardButton(skill, callback_data=f"skill_{skill}")])
    
    return InlineKeyboardMarkup(keyboard)

def get_experience_keyboard():
    """
    Create an inline keyboard for experience selection.
    """
    keyboard = []
    for experience in config.EXPERIENCE_LEVELS:
        keyboard.append([InlineKeyboardButton(experience, callback_data=f"exp_{experience}")])
    
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(team_id):
    """
    Create an inline keyboard for team confirmation.
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"confirm_{team_id}_yes"),
            InlineKeyboardButton("❌ Decline", callback_data=f"confirm_{team_id}_no")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_edit_registration_keyboard():
    """
    Create an inline keyboard for editing registration.
    """
    keyboard = [
        [InlineKeyboardButton("✏️ Update Registration", callback_data="edit_registration")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]
    ]
    
    return InlineKeyboardMarkup(keyboard)
