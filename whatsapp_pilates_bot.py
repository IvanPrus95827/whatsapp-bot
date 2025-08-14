import requests
import json
import schedule
import time
import google.generativeai as genai
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Set
import logging
import os
from dataclasses import dataclass
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GroupInfo:
    uuid: str
    name: str
    participants: List[Dict]
    created_at: str = ""

@dataclass
class WeeklyProgress:
    group_uuid: str
    week_start: str
    completed_members: Set[str]
    messages_analyzed: Set[str]

class WhatsAppPilatesBot:
    def __init__(self, api_key: str, gemini_api_key: str, bot_number: str):
        self.api_key = api_key
        self.bot_number = bot_number
        self.base_url = "https://api.p.2chat.io/open/whatsapp"
        
        # Initialize Gemini AI
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Ireland timezone
        self.ireland_tz = pytz.timezone(config.IRELAND_TIMEZONE)
        
        # Weekly progress tracking
        self.weekly_progress: Dict[str, WeeklyProgress] = {}
        
        # Headers for API requests
        self.headers = {
            'X-User-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_current_week_start(self) -> str:
        """Get the start of current week (Monday) in Ireland timezone"""
        now = datetime.now(self.ireland_tz)
        monday = now - timedelta(days=now.weekday())
        return monday.strftime('%Y-%m-%d')
    
    def is_group_old_enough(self, group_created_at: str) -> bool:
        """Check if group is old enough to be safely monitored (prevents account bans)"""
        try:
            if not group_created_at:
                # If no creation date available, assume it's old enough for safety
                logger.warning("Group creation date not available, assuming it's old enough")
                return True
            
            # Parse group creation date
            if group_created_at.endswith('Z'):
                created_date = datetime.fromisoformat(group_created_at.replace('Z', '+00:00'))
            else:
                created_date = datetime.fromisoformat(group_created_at)
            
            # Convert to Ireland timezone
            created_date = created_date.astimezone(self.ireland_tz)
            current_date = datetime.now(self.ireland_tz)
            
            # Calculate age in days
            age_days = (current_date - created_date).days
            
            is_old_enough = age_days >= config.MIN_GROUP_AGE_DAYS
            
            if not is_old_enough:
                logger.info(f"Group is only {age_days} days old (minimum: {config.MIN_GROUP_AGE_DAYS}), skipping for safety")
            
            return is_old_enough
            
        except Exception as e:
            logger.error(f"Error checking group age: {e}")
            # Return True for safety if we can't determine age
            return True
    
    def find_pilates_groups(self) -> List[GroupInfo]:
        """Find all groups containing 'pilates' in their name (case insensitive)"""
        try:
            # Get all groups for the bot number
            url = f"{self.base_url}/groups"
            response = requests.get(url, headers={'X-User-API-Key': self.api_key})
            
            if response.status_code != 200:
                logger.error(f"Failed to get groups: {response.text}")
                return []
            
            groups_data = response.json()
            pilates_groups = []
            
            for group in groups_data.get('data', []):
                group_name = group.get('name', '').lower()
                if config.PILATES_KEYWORD.lower() in group_name:
                    # Get group details including participants
                    group_details = self.get_group_details(group['uuid'])
                    if group_details:
                        group_created_at = group_details.get('created_at', '')
                        
                        # Check if group is old enough to safely monitor
                        if not self.is_group_old_enough(group_created_at):
                            logger.info(f"Skipping recently created Pilates group: {group['name']} (created: {group_created_at})")
                            continue
                        
                        pilates_groups.append(GroupInfo(
                            uuid=group['uuid'],
                            name=group['name'],
                            participants=group_details.get('participants', []),
                            created_at=group_created_at
                        ))
                        age_days = (datetime.now(self.ireland_tz) - datetime.fromisoformat(group_created_at.replace('Z', '+00:00')).astimezone(self.ireland_tz)).days if group_created_at else "unknown"
                        logger.info(f"Found Pilates group: {group['name']} ({group['uuid']}) - Age: {age_days} days")
            
            return pilates_groups
        
        except Exception as e:
            logger.error(f"Error finding Pilates groups: {e}")
            return []
    
    def get_group_details(self, group_uuid: str) -> Dict:
        """Get detailed information about a specific group"""
        try:
            url = f"{self.base_url}/group/{group_uuid}"
            response = requests.get(url, headers={'X-User-API-Key': self.api_key})
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get group details for {group_uuid}: {response.text}")
                return {}
        
        except Exception as e:
            logger.error(f"Error getting group details: {e}")
            return {}
    
    def get_group_messages(self, group_uuid: str, page: int = 0) -> List[Dict]:
        """Get messages from a specific group"""
        try:
            url = f"{self.base_url}/groups/messages/{group_uuid}?page_number={page}"
            response = requests.get(url, headers={'X-User-API-Key': self.api_key})
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get messages for group {group_uuid}: {response.text}")
                return []
        
        except Exception as e:
            logger.error(f"Error getting group messages: {e}")
            return []
    
    def analyze_message_with_gemini(self, message_text: str) -> bool:
        """Use Gemini AI to analyze if message indicates weekly plan completion"""
        try:
            prompt = config.GEMINI_ANALYSIS_PROMPT.format(message_text=message_text)
            
            response = self.model.generate_content(prompt)
            result = response.text.strip().upper()
            
            logger.info(f"Gemini analysis for '{message_text[:50]}...': {result}")
            return result == "YES"
        
        except Exception as e:
            logger.error(f"Error analyzing message with Gemini: {e}")
            return False
    
    def send_group_message(self, group_uuid: str, message: str) -> bool:
        """Send a message to a specific group"""
        try:
            url = f"{self.base_url}/send-message"
            payload = {
                "from_number": self.bot_number,
                "to_group_uuid": group_uuid,
                "text": message
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent group message to {group_uuid}")
                return True
            else:
                logger.error(f"Failed to send group message: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending group message: {e}")
            return False
    
    def send_individual_message(self, phone_number: str, message: str) -> bool:
        """Send a private message to an individual"""
        try:
            url = f"{self.base_url}/send-message"
            payload = {
                "from_number": self.bot_number,
                "to_number": phone_number,
                "text": message
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent individual message to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send individual message: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending individual message: {e}")
            return False
    
    def process_group_messages(self, group: GroupInfo):
        """Process new messages from a group and track weekly progress"""
        week_start = self.get_current_week_start()
        
        # Initialize weekly progress if not exists
        if group.uuid not in self.weekly_progress:
            self.weekly_progress[group.uuid] = WeeklyProgress(
                group_uuid=group.uuid,
                week_start=week_start,
                completed_members=set(),
                messages_analyzed=set()
            )
        
        progress = self.weekly_progress[group.uuid]
        
        # Reset if new week
        if progress.week_start != week_start:
            progress.week_start = week_start
            progress.completed_members.clear()
            progress.messages_analyzed.clear()
        
        # Get recent messages
        messages = self.get_group_messages(group.uuid)
        
        for message in messages:
            message_id = message.get('id', '')
            sender_number = message.get('from_number', '')
            message_text = message.get('text', '')
            message_time = message.get('timestamp', '')
            
            # Skip if already analyzed or from bot itself
            if message_id in progress.messages_analyzed or sender_number == self.bot_number:
                continue
            
            # Check if message is from this week
            try:
                msg_datetime = datetime.fromisoformat(message_time.replace('Z', '+00:00'))
                msg_datetime = msg_datetime.astimezone(self.ireland_tz)
                week_start_date = datetime.strptime(week_start, '%Y-%m-%d').replace(tzinfo=self.ireland_tz)
                
                if msg_datetime < week_start_date:
                    continue
            except:
                # If timestamp parsing fails, assume it's current
                pass
            
            # Analyze message with Gemini
            if self.analyze_message_with_gemini(message_text):
                progress.completed_members.add(sender_number)
                logger.info(f"Member {sender_number} completed weekly plan in group {group.name}")
            
            progress.messages_analyzed.add(message_id)
    
    def saturday_report(self):
        """Send weekly reports on Saturday at 8 AM Ireland time"""
        logger.info("Generating Saturday weekly reports...")
        
        pilates_groups = self.find_pilates_groups()
        
        for group in pilates_groups:
            progress = self.weekly_progress.get(group.uuid)
            if not progress:
                continue
            
            completed_numbers = progress.completed_members
            all_participants = {p.get('phone_number', '') for p in group.participants if p.get('phone_number')}
            incomplete_numbers = all_participants - completed_numbers
            
            # Send congratulations to group for completed members
            if completed_numbers:
                completed_count = len(completed_numbers)
                group_message = config.GROUP_CONGRATULATIONS_TEMPLATE.format(count=completed_count)
                self.send_group_message(group.uuid, group_message)
            
            # Send individual reminders to incomplete members
            for phone_number in incomplete_numbers:
                if phone_number and phone_number != self.bot_number:
                    self.send_individual_message(phone_number, config.INDIVIDUAL_REMINDER_TEMPLATE)
            
            logger.info(f"Group {group.name}: {len(completed_numbers)} completed, {len(incomplete_numbers)} reminded")
    
    def monitor_messages(self):
        """Continuously monitor messages from all Pilates groups"""
        logger.info("Starting message monitoring...")
        
        while True:
            try:
                pilates_groups = self.find_pilates_groups()
                
                for group in pilates_groups:
                    self.process_group_messages(group)
                
                # Sleep for configured interval before next check
                time.sleep(config.MESSAGE_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in message monitoring: {e}")
                time.sleep(config.ERROR_RETRY_INTERVAL)  # Wait longer if there's an error
    
    def start_bot(self):
        """Start the bot with scheduled tasks"""
        logger.info("Starting WhatsApp Pilates Bot...")
        
        # Schedule Saturday reports (Ireland timezone)
        schedule.every().saturday.at(config.SATURDAY_REPORT_TIME).do(self.saturday_report)
        
        # Start message monitoring in a separate thread
        import threading
        monitor_thread = threading.Thread(target=self.monitor_messages, daemon=True)
        monitor_thread.start()
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks

def main():
    """Main function to run the bot"""
    # Load configuration
    TWOCHAT_API_KEY = config.TWOCHAT_API_KEY
    GEMINI_API_KEY = config.GEMINI_API_KEY
    BOT_NUMBER = config.BOT_NUMBER
    
    if not GEMINI_API_KEY:
        logger.error("Please set your Gemini API key in the GEMINI_API_KEY environment variable or config.py")
        return
    
    if not TWOCHAT_API_KEY:
        logger.error("Please set your 2Chat API key in the TWOCHAT_API_KEY environment variable or config.py")
        return
    
    # Create and start the bot
    bot = WhatsAppPilatesBot(
        api_key=TWOCHAT_API_KEY,
        gemini_api_key=GEMINI_API_KEY,
        bot_number=BOT_NUMBER
    )
    
    try:
        bot.start_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    main()
