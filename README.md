# Hackathon Team Matching Bot

A Telegram bot that helps hackathon participants find teammates based on their skills and experience levels.

## Features

- User registration with skill and experience selection
- Automatic team formation based on complementary skills
- Team confirmation process
- Team member notification with contact information

## Deployment on Railway

1. Fork this repository
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add the following environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token from BotFather
   - `DATABASE_URL`: Your PostgreSQL connection string (Railway will provide this automatically if you add a PostgreSQL plugin)
5. Deploy the application

## Local Development

1. Clone this repository
2. Create a `.env` file with your Telegram Bot Token and database URL:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=postgresql://username:password@localhost:5432/hackathon_teams
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```
   python main.py
   ```

## How It Works

1. Users register with their skill (Frontend, Backend, or Design) and experience level
2. The bot forms balanced teams of three with complementary skills
3. Team members receive confirmation requests
4. If all members confirm, a private group chat is created

## Project Structure
