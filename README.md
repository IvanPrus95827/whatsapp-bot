# WhatsApp Pilates Bot

An AI-powered WhatsApp bot that receives real-time messages from Pilates group chats and tracks weekly training completion using Google's Gemini AI, 2Chat API, Flask webhooks, and ngrok tunneling.

## Overview

This version of the bot uses Flask webhooks and ngrok to receive messages from 2Chat in real-time, rather than periodic polling. This approach is more efficient and provides better real-time performance.

## Key Changes

✅ **From Listener to Webhook**: Uses Flask to receive real-time messages  
✅ **ngrok Integration**: Automatically creates public tunnel  
✅ **Maintained Scheduled Tasks**: Saturday reporting functionality remains unchanged  
✅ **Real-time Processing**: Messages processed immediately with no delay  

## Features

- **Real-time Webhook Processing**: Receives instant messages from Pilates groups via 2Chat webhooks
- **Automatic Group Detection**: Finds all WhatsApp groups containing "pilates" in their name (case insensitive)
- **Group Age Safety Filter**: Only monitors groups older than 30 days to prevent account bans from interacting with newly created groups
- **AI Message Analysis**: Uses Google Gemini AI to analyze messages and detect when members complete their weekly training
- **Weekly Tracking**: Tracks completion status for each member per week
- **Saturday Reports**: Automatically sends reports every Saturday at 8 AM (Ireland timezone)
- **Group Congratulations**: Sends encouraging messages to groups for completed members
- **Individual Reminders**: Sends private reminders to members who haven't completed their weekly plan
- **ngrok Tunneling**: Automatically exposes local webhook endpoint to receive 2Chat messages

## Requirements

- Python 3.7+
- 2Chat API account and API key
- Google Gemini AI API key
- WhatsApp Business account connected to 2Chat
- ngrok account and auth token

## New Dependencies

- `flask==3.0.0` - Web framework for webhook handling
- `pyngrok==6.0.0` - ngrok tunnel integration

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Get your 2Chat API key from [2Chat.io](https://2chat.io)
   - Get your Gemini API key from [Google AI Studio](https://aistudio.google.com)
   - Sign up for ngrok and get your auth token from [ngrok.com](https://ngrok.com)

4. Configure environment variables:
   
   Copy the environment template:
   ```bash
   cp env_template.txt .env
   ```
   
   Edit the `.env` file with your API keys:
   ```bash
   # 2Chat API Configuration
   export TWOCHAT_API_KEY="your-2chat-api-key"
   export BOT_NUMBER="your-bot-phone-number"
   
   # Gemini AI Configuration
   export GEMINI_API_KEY="your-gemini-api-key"
   ```
   
   Load environment variables:
   ```bash
   source .env
   ```

## Usage

1. Ensure your WhatsApp number is connected to 2Chat
2. Make sure the bot number is added to all Pilates groups you want to monitor
3. Run the bot:
   ```bash
   python whatsapp_pilates_bot.py
   ```

When starting, you'll see:
```
🚀 Webhook URL: https://xxxxx.ngrok.io/webhook
📝 Configure this URL in your 2chat webhook settings
```

## Configure 2Chat Webhook

1. Login to 2Chat console
2. Go to API Settings → Webhook Configuration
3. Set Webhook URL to the displayed ngrok URL (e.g., `https://xxxxx.ngrok.io/webhook`)
4. Select events to receive: `message_received`
5. Save configuration

The bot will:
- Receive real-time messages from all Pilates groups via webhooks
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

### Real-time Message Processing
- Receives messages from Pilates groups via 2Chat webhooks
- Uses Gemini AI to analyze message content
- Automatically identifies members who complete training

### Saturday Reports (Unchanged)
- Every Saturday at 8 AM (Ireland time) sends reports
- Congratulates members who completed training
- Reminds incomplete members

### Intelligent Filtering
- Only processes Pilates-related groups
- Filters out bot's own messages
- Only analyzes messages from current week

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

## API Endpoints

- `GET /`: Health check, returns bot status
- `POST /webhook`: Webhook endpoint for receiving 2Chat messages

## Security Notes

- Store API keys as environment variables in production
- Ensure your 2Chat account has appropriate permissions
- The bot only reads messages from groups containing "pilates" in the name
- **Safety Feature**: Bot automatically skips groups created less than 30 days ago to prevent account bans
- Individual reminder messages are sent privately
- ngrok tunnels are public - ensure webhook endpoint security
- Don't expose API keys in logs
- Regularly rotate authentication tokens

## Advantages Over Listener Version

1. **Real-time**: Messages processed immediately with no delay
2. **Efficiency**: No need for periodic API polling
3. **Reliability**: Event-driven, won't miss messages
4. **Scalability**: Easier to add new features and integrations

## Technical Architecture

```
2Chat -> Webhook -> ngrok -> Flask -> Bot Processing -> Gemini AI
                                  -> Scheduled Tasks -> Saturday Reports
```

## Next Steps

The bot is now configured for webhook mode. Ensure:
1. ✅ Environment variables are set
2. ✅ 2Chat webhook is configured
3. ✅ Bot is running
4. ✅ ngrok tunnel is active

Start enjoying real-time Pilates training tracking! 🧘‍♀️💪

## Webhook Testing

You can test the webhook functionality by sending a POST request to the webhook endpoint while the bot is running.

## Logs and Debugging

The bot outputs detailed logs including:
- Received webhook data
- Message processing results
- AI analysis results
- Sent messages

## Troubleshooting

### Webhook Not Receiving Messages
1. Check if ngrok tunnel is running properly
2. Verify 2Chat webhook configuration is correct
3. Review Flask application logs

### ngrok Connection Issues
1. Check ngrok auth token
2. Verify network connection
3. Restart application

### Message Processing Errors
1. Check Gemini API key
2. Verify group permissions
3. Review detailed error logs

### Common Issues

1. **Bot not receiving messages**
   - Verify the bot number is added to Pilates groups
   - Check 2Chat webhook configuration
   - Ensure groups contain "pilates" in their name
   - Verify ngrok tunnel is active

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
- Webhook data reception
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
