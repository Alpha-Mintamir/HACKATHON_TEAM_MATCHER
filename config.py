import os
from dotenv import load_dotenv

# Load environment variables from .env file (only in development)
if os.path.exists('.env'):
    load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///hackathon_teams.db"
    print(f"No DATABASE_URL found, using SQLite: {DATABASE_URL}")

# If using Railway's PostgreSQL, make sure the URL is properly formatted for SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Team formation settings
TEAM_SIZE = 3
REQUIRED_SKILLS = ["Frontend Development", "Backend Development", "Design"]
EXPERIENCE_LEVELS = ["1 year", "2 years", "More than 2 years"]

# Message timeouts
CONFIRMATION_TIMEOUT = 3600  # 1 hour in seconds
