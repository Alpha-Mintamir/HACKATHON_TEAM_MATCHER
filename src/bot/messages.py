def get_welcome_message():
    """
    Get the welcome message for new users.
    """
    return (
        "👋 Welcome to the Hackathon Team Matching Bot!\n\n"
        "This bot will help you find teammates for the hackathon based on your skills and experience.\n\n"
        "Let's get started! Please select your primary skill:"
    )

def get_experience_message():
    """
    Get the message asking for experience level.
    """
    return "Great! Now, please select your experience level:"

def get_registration_complete_message(skill, experience):
    """
    Get the message confirming registration is complete.
    """
    return (
        f"✅ Registration complete!\n\n"
        f"Your skill: {skill}\n"
        f"Your experience: {experience}\n\n"
        f"You've been added to the waiting list. Team matching happens every 2 hours. "
        f"We'll notify you when you've been matched with a team!"
    )

def get_team_match_message():
    """
    Get the message notifying users they've been matched with a team.
    """
    return (
        "🎉 You've been matched with a team!\n\n"
        "Do you accept this team assignment? If all team members accept, "
        "we'll create a group chat for your team."
    )

def get_team_confirmed_message():
    """
    Get the message notifying users their team has been confirmed.
    """
    return (
        "✅ Your team has been confirmed!\n\n"
        "All members have accepted the team assignment. "
        "You'll be added to a group chat shortly."
    )

def get_team_declined_message():
    """
    Get the message notifying users someone declined the team.
    """
    return (
        "❌ Unfortunately, someone declined the team assignment.\n\n"
        "You've been added back to the waiting list. "
        "We'll notify you when we find a new team for you."
    )

def get_team_intro_message(team_info):
    """
    Get the introduction message for a new team chat.
    """
    message = "🚀 Welcome to your hackathon team chat! 🚀\n\n"
    message += "Here are your team members:\n\n"
    
    for member in team_info["members"]:
        username = member["username"] or "Anonymous"
        message += f"• {username} - {member['skill']} ({member['experience']})\n"
    
    message += "\nGood luck with your hackathon project! 🎉"
    return message

def get_already_registered_message(skill, experience):
    """
    Get the message for users who are already registered.
    """
    return (
        f"You're already registered with the following details:\n\n"
        f"Skill: {skill}\n"
        f"Experience: {experience}\n\n"
        f"Would you like to update your registration?"
    )
