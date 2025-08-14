# WhatsApp Pilates Bot

An AI-powered WhatsApp bot that monitors Pilates group chats and tracks weekly training completion using Google's Gemini AI and 2Chat API.

## Features

- **Automatic Group Detection**: Finds all WhatsApp groups containing "pilates" in their name (case insensitive)
- **Group Age Safety Filter**: Only monitors groups older than 30 days to prevent account bans from interacting with newly created groups
- **AI Message Analysis**: Uses Google Gemini AI to analyze messages and detect when members complete their weekly training
- **Weekly Tracking**: Tracks completion status for each member per week
- **Saturday Reports**: Automatically sends reports every Saturday at 8 AM (Ireland timezone)
- **Group Congratulations**: Sends encouraging messages to groups for completed members
- **Individual Reminders**: Sends private reminders to members who haven't completed their weekly plan

## Requirements

- Python 3.7+
- 2Chat API account and API key
- Google Gemini AI API key
- WhatsApp Business account connected to 2Chat

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Get your 2Chat API key from [2Chat.io](https://2chat.io)
   - Get your Gemini API key from [Google AI Studio](https://aistudio.google.com)

4. Configure the bot:
   - Option 1: Edit the API keys directly in `whatsapp_pilates_bot.py`
   - Option 2: Set environment variables (recommended for security):
     ```bash
     export TWOCHAT_API_KEY="your-2chat-api-key"
     export GEMINI_API_KEY="your-gemini-api-key"
     export BOT_NUMBER="+353873326005"
     ```

## Usage

1. Ensure your WhatsApp number (+353873326005) is connected to 2Chat
2. Make sure the bot number is added to all Pilates groups you want to monitor
3. Run the bot:
   ```bash
   python whatsapp_pilates_bot.py
   ```

The bot will:
- Continuously monitor messages from all Pilates groups
- Use AI to analyze messages for weekly plan completion
- Send automatic reports every Saturday at 8 AM Ireland time

## Safety Features

### Account Protection
To prevent your WhatsApp account from being banned, the bot includes several safety measures:

1. **Group Age Filter**: Only monitors groups that are **30+ days old**
   - Newly created groups are automatically skipped
   - Prevents triggering WhatsApp's spam detection systems
   - Configurable via `MIN_GROUP_AGE_DAYS` in config.py

2. **Conservative Monitoring**: 
   - 30-second intervals between message checks (not too frequent)
   - Proper error handling with retry delays
   - Only monitors groups with "pilates" keyword

3. **Selective Engagement**:
   - Only sends messages to established groups
   - Individual reminders are sent privately
   - No bulk messaging or spam-like behavior

### Logs and Transparency
The bot provides detailed logging showing:
- Which groups are being monitored vs. skipped
- Group ages and creation dates
- AI analysis results
- Message sending success/failure

**Example log output:**
```
Found Pilates group: Weekly Pilates Class (WAG123...) - Age: 45 days
Skipping recently created Pilates group: New Pilates Group (created: 2024-01-15)
Gemini analysis for 'Finished my workout today...': YES
```

## How It Works

### Message Analysis
The bot uses Google's Gemini AI to analyze messages and determine if someone has completed their weekly training. It looks for patterns like:
- "Finished my workout today"
- "Completed this week's plan"
- "Done with training for the week"
- And many other variations

### Weekly Tracking
- Each week starts on Monday (Ireland timezone)
- The bot tracks which members have indicated completion
- Progress resets every week automatically

### Saturday Reports
Every Saturday at 8 AM (Ireland time), the bot:
1. **Group Messages**: Sends congratulations to groups mentioning how many members completed their weekly plan
2. **Individual Reminders**: Sends private messages to members who haven't completed their plan, encouraging them to catch up

## Configuration

You can modify settings in `config.py`:

### Safety Settings
- `MIN_GROUP_AGE_DAYS = 30` - Minimum group age in days before monitoring (prevents account bans)

### Bot Behavior
- `MESSAGE_CHECK_INTERVAL = 30` - How often to check for new messages (seconds)
- `ERROR_RETRY_INTERVAL = 60` - Wait time after errors (seconds)
- `SATURDAY_REPORT_TIME = "08:00"` - Time for weekly reports (Ireland timezone)

### Group Detection
- `PILATES_KEYWORD = 'pilates'` - Keyword to identify relevant groups (case insensitive)

### Message Templates
- `GROUP_CONGRATULATIONS_TEMPLATE` - Message sent to groups for completed members
- `INDIVIDUAL_REMINDER_TEMPLATE` - Private reminder for incomplete members
- `GEMINI_ANALYSIS_PROMPT` - AI prompt for analyzing training completion messages

### Timezone
- `IRELAND_TIMEZONE = 'Europe/Dublin'` - Timezone for scheduling and date calculations

## API Requirements

### 2Chat API
- Account with WhatsApp Business integration
- API key with permissions for:
  - Reading group messages
  - Sending group messages
  - Sending individual messages
  - Accessing group member lists

### Google Gemini AI
- API key from Google AI Studio
- Access to Gemini Pro model

## Security Notes

- Store API keys as environment variables in production
- Ensure your 2Chat account has appropriate permissions
- The bot only reads messages from groups containing "pilates" in the name
- **Safety Feature**: Bot automatically skips groups created less than 30 days ago to prevent account bans
- Individual reminder messages are sent privately

## Troubleshooting

### Common Issues

1. **Bot not receiving messages**
   - Verify the bot number is added to Pilates groups
   - Check 2Chat API key permissions
   - Ensure groups contain "pilates" in their name

2. **AI analysis not working**
   - Verify Gemini API key is correct
   - Check internet connection
   - Review log messages for specific errors

3. **Saturday reports not sending**
   - Verify system time and timezone
   - Check that the bot is running continuously
   - Review scheduled task logs

### Logs
The bot provides detailed logging. Check console output for:
- Group discovery results
- Message analysis results
- API call successes/failures
- Weekly report generation

## Support

For issues with:
- **2Chat API**: Contact [2Chat Support](https://2chat.io/support)
- **Gemini AI**: Check [Google AI Documentation](https://ai.google.dev/)
- **Bot Code**: Review logs and error messages

## License

This project is provided as-is for educational and personal use.
