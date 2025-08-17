# WhatsApp Pilates Bot 🧘‍♀️🤖

An intelligent WhatsApp bot that automatically tracks weekly pilates training completion in group chats and sends personalized encouragement messages using AI.

## 🌟 Features

### 📊 **Automated Progress Tracking**
- Monitors WhatsApp group messages for pilates completion indicators
- Uses Google Gemini AI to analyze messages and detect training completion
- Tracks weekly progress for all group members
- Automatically resets progress every Monday at midnight (Ireland timezone)

### 🎉 **Smart Messaging System**
- **AI-Generated Varied Messages**: Every message is unique using Gemini AI
- **Group Congratulations**: Celebrates members who completed their weekly training
- **Individual Reminders**: Sends personalized reminders to members who haven't completed training
- **Auto-Reply System**: Responds to members who reply to reminder messages

### ⏰ **Intelligent Scheduling**
- **Monday 00:00**: Automatic weekly progress reset
- **Saturday 18:00**: Weekly reports with congratulations and reminders
- **Real-time**: Message analysis and progress tracking via webhooks

### 🛡️ **Safety Features**
- Only monitors groups containing "pilates" in the name
- Skips recently created groups (configurable minimum age)
- Fallback to static messages if AI generation fails
- Comprehensive error handling and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 2Chat WhatsApp API account
- Google Gemini AI API key
- ngrok account for webhook tunneling

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   
   Create a `.env` file in the project root:
   ```env
   # 2Chat API Configuration
   TWOCHAT_API_KEY=your_2chat_api_key_here
   BOT_NUMBER=your_whatsapp_bot_number_here
   
   # AI Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # ngrok Configuration
   NGROK_TOKEN=your_ngrok_auth_token_here
   
   # Optional: Custom report time (default: 18:00)
   SATURDAY_REPORT_TIME=18:00
   ```

4. **Run the bot**
   ```bash
   python whatsapp_pilates_bot.py
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TWOCHAT_API_KEY` | Your 2Chat API key | ✅ | - |
| `BOT_NUMBER` | WhatsApp bot phone number | ✅ | - |
| `GEMINI_API_KEY` | Google Gemini AI API key | ✅ | - |
| `NGROK_TOKEN` | ngrok authentication token | ✅ | - |
| `SATURDAY_REPORT_TIME` | Weekly report time (HH:MM) | ❌ | 18:00 |

### Bot Settings (config.py)

```python
# Timezone
IRELAND_TIMEZONE = 'Europe/Dublin'

# Group Detection
PILATES_KEYWORD = 'pilates'  # Groups must contain this word
MIN_GROUP_AGE_DAYS = 30     # Skip groups newer than this

# Message Templates (used as base for AI variation)
GROUP_CONGRATULATIONS_TEMPLATE = "🎉 Well done on training! ..."
INDIVIDUAL_REMINDER_TEMPLATE = "Hi! I'm Eoin, your coach! ..."
```

## 🏗️ Architecture

### Core Components

1. **WhatsAppPilatesBot**: Main bot class handling all functionality
2. **Webhook Server**: Flask app receiving real-time messages
3. **AI Message Generator**: Creates varied messages using Gemini AI
4. **Scheduler**: Manages weekly tasks and progress resets
5. **Data Persistence**: JSON files for groups, progress, and auto-replies

### Data Flow

```
WhatsApp Message → Webhook → AI Analysis → Progress Update → Weekly Report → AI-Generated Response
```

### File Structure

```
whatsapp-bot/
├── whatsapp_pilates_bot.py    # Main bot implementation
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
├── .env                       # Environment variables (not in git)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file

# Generated during runtime:
├── available_groups.json      # Discovered pilates groups
├── weekly_progress.json       # Current week's progress
└── auto_reply_members.json    # Members awaiting auto-replies
```

## 🤖 AI Integration

### Message Analysis
The bot uses Google Gemini AI to analyze incoming messages and determine if they indicate training completion:

```python
GEMINI_ANALYSIS_PROMPT = """
Analyze this WhatsApp message to determine if the sender is indicating 
that he or she has completed the full or single or partial anything 
training or class for the current week.

Message: "{message_text}"

Respond with only "YES" or "NO".
"""
```

### Varied Message Generation
Every outgoing message is made unique through AI:

```python
def generate_varied_message(self, message: str) -> str:
    """Generate a varied version of a message using AI"""
    prompt = f"""Give me one similar message related to this, not change names. 
    It's about pilates class training. Only answer the message, no other text.
    Message: '{message}'"""
```

## 📅 Weekly Cycle

### Monday 00:00 (Midnight) - Ireland Time
- ✨ **Weekly Progress Reset**
- 🔍 **Group Discovery** (finds new pilates groups)
- 📊 **Initialize Tracking** for all groups

### Throughout the Week
- 👂 **Real-time Message Monitoring**
- 🤖 **AI Message Analysis**
- 📈 **Progress Tracking**
- 💬 **Auto-reply Management**

### Saturday 18:00 - Ireland Time
- 🎉 **Group Congratulations** (AI-generated, unique each time)
- 📨 **Individual Reminders** (AI-generated, personalized)
- 🔄 **Auto-reply Setup** for incomplete members

## 🔧 API Integration

### 2Chat WhatsApp API
- **Group Management**: Discover and monitor pilates groups
- **Message Sending**: Send group and individual messages
- **Webhook Events**: Real-time message reception

### Google Gemini AI
- **Message Analysis**: Detect training completion
- **Content Generation**: Create varied, natural messages
- **Auto-replies**: Generate contextual responses

### ngrok Tunneling
- **Webhook Exposure**: Make local Flask server publicly accessible
- **Automatic Setup**: Bot configures webhooks automatically

## 🛠️ Development

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_ENV=development

# Run with detailed logging
python whatsapp_pilates_bot.py
```

### Testing Message Generation

The bot includes fallback mechanisms:
- If AI fails, uses static templates
- Comprehensive error logging
- Automatic retry logic

### Adding New Features

1. **Custom Message Templates**: Modify `config.py`
2. **New Scheduling**: Update `start_scheduler()` method
3. **Additional AI Prompts**: Extend `generate_*` methods

## 📊 Monitoring & Logs

### Log Levels
- **INFO**: Normal operations, message sending, progress updates
- **WARNING**: Non-critical issues, fallbacks triggered
- **ERROR**: Failed operations, API errors

### Key Metrics Logged
- Group discovery and monitoring
- Message analysis results
- Weekly progress statistics
- Auto-reply management
- Webhook events

## 🔒 Security & Privacy

### Data Protection
- Sensitive data in `.env` (not committed to git)
- No message content stored permanently
- Only tracking completion status, not personal details

### Safety Features
- Minimum group age requirement
- Rate limiting via API constraints
- Error handling prevents crashes

## 📋 Troubleshooting

### Common Issues

**Bot not receiving messages**
- Check webhook URL configuration
- Verify ngrok tunnel is active
- Ensure 2Chat webhooks are properly subscribed

**AI not working**
- Verify `GEMINI_API_KEY` is correct
- Check API quota limits
- Review error logs for specific issues

**Messages not sending**
- Validate `TWOCHAT_API_KEY` and `BOT_NUMBER`
- Check 2Chat account status
- Verify group permissions

**Scheduling not working**
- Confirm timezone settings (`IRELAND_TIMEZONE`)
- Check system time accuracy
- Review scheduler thread status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **2Chat API** for WhatsApp integration
- **Google Gemini AI** for intelligent message processing
- **ngrok** for webhook tunneling
- **Flask** for webhook server

---

**Made with ❤️ for pilates communities worldwide** 🧘‍♀️✨