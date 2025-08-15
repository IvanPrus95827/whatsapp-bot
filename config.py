# Configuration file for WhatsApp Pilates Bot

import os
import dotenv

dotenv.load_dotenv()

# 2Chat API Configuration
TWOCHAT_API_KEY = os.getenv('TWOCHAT_API_KEY')
BOT_NUMBER = os.getenv('BOT_NUMBER')

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # Must be set
NGROK_TOKEN = os.getenv('NGROK_TOKEN', '')

# Bot Settings
IRELAND_TIMEZONE = 'Europe/Dublin'
SATURDAY_REPORT_TIME = "08:00"
MESSAGE_CHECK_INTERVAL = 30  # seconds
ERROR_RETRY_INTERVAL = 60   # seconds

# Group Settings
PILATES_KEYWORD = 'pilates'  # Case insensitive search
MIN_GROUP_AGE_DAYS = 30  # Minimum group age in days to avoid newly created groups (safety feature)

# Message Templates
GROUP_CONGRATULATIONS_TEMPLATE = "🎉 Well done on training! {count} members completed their weekly pilates plan this week. Keep up the great work! 💪"

INDIVIDUAL_REMINDER_TEMPLATE = """Hi! I noticed you haven't completed your weekly pilates plan yet. Remember that consistent training is key to achieving your fitness goals. Why not take some time today to catch up? Your body will thank you! 🧘‍♀️💪"""

# Gemini Analysis Prompt
GEMINI_ANALYSIS_PROMPT = """
Analyze this WhatsApp message to determine if that the sender is indicating that he or she has completed the full or single or partial anything training or class.
Please focus on current week, not the previous weeks or the future one or the entire plan.

Message: "{message_text}"

Respond with only "YES" or "NO".
"""