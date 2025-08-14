# Configuration file for WhatsApp Pilates Bot

import os

# 2Chat API Configuration
TWOCHAT_API_KEY = os.getenv('TWOCHAT_API_KEY', 'UAKab3401ad-1a9f-4ecb-822a-cb960f89903c')
BOT_NUMBER = os.getenv('BOT_NUMBER', '+353873326005')

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # Must be set

# Bot Settings
IRELAND_TIMEZONE = 'Europe/Dublin'
SATURDAY_REPORT_TIME = "08:00"
MESSAGE_CHECK_INTERVAL = 30  # seconds
ERROR_RETRY_INTERVAL = 60   # seconds

# Group Settings
PILATES_KEYWORD = 'pilates'  # Case insensitive search

# Message Templates
GROUP_CONGRATULATIONS_TEMPLATE = "🎉 Well done on training! {count} members completed their weekly pilates plan this week. Keep up the great work! 💪"

INDIVIDUAL_REMINDER_TEMPLATE = """Hi! I noticed you haven't completed your weekly pilates plan yet. Remember that consistent training is key to achieving your fitness goals. Why not take some time today to catch up? Your body will thank you! 🧘‍♀️💪"""

# Gemini Analysis Prompt
GEMINI_ANALYSIS_PROMPT = """
Analyze this WhatsApp message to determine if the person is indicating they have completed their weekly pilates training plan.

Look for indicators such as:
- Statements about finishing workouts/exercises
- Mentions of completing weekly goals/plans
- References to being done with training for the week
- Updates about finishing their pilates routine
- Any positive statements about workout completion

Message: "{message_text}"

Respond with only "YES" if the message indicates weekly plan completion, or "NO" if it doesn't.
"""
