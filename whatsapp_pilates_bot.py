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
from flask import Flask, request
from pyngrok import ngrok
import threading

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
    completed_members: Set[str]  # Set of phone numbers for backward compatibility
    completed_members_info: Dict[str, str]  # Dict mapping phone_number -> pushname
    messages_analyzed: Set[str]

@dataclass
class AutoReplyMember:
    phone_number: str
    group_uuid: str
    message_sent: str
    created_at: str

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
        self.available_groups: List[GroupInfo] = []
        self.weekly_progress: Dict[str, WeeklyProgress] = {}
        
        # Auto reply members tracking
        self.auto_reply_members: List[AutoReplyMember] = []
        
        # Headers for API requests
        self.headers = {
            'X-User-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # File paths for data persistence
        self.available_groups_file = 'available_groups.json'
        self.weekly_progress_file = 'weekly_progress.json'
        self.auto_reply_members_file = 'auto_reply_members.json'
        
        # Load existing data on initialization
        self.load_available_groups()
        self.load_weekly_progress()
        self.load_auto_reply_members()
    
    def save_available_groups(self):
        """Save available_groups to JSON file"""
        try:
            # Convert GroupInfo objects to dictionaries
            groups_data = []
            for group in self.available_groups:
                groups_data.append({
                    'uuid': group.uuid,
                    'name': group.name,
                    'participants': group.participants,
                    'created_at': group.created_at
                })
            
            with open(self.available_groups_file, 'w', encoding='utf-8') as f:
                json.dump(groups_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(groups_data)} groups to {self.available_groups_file}")
            
        except Exception as e:
            logger.error(f"Error saving available_groups: {e}")
    
    def load_available_groups(self):
        """Load available_groups from JSON file"""
        try:
            if os.path.exists(self.available_groups_file):
                with open(self.available_groups_file, 'r', encoding='utf-8') as f:
                    groups_data = json.load(f)
                
                # Convert dictionaries back to GroupInfo objects
                self.available_groups = []
                for group_dict in groups_data:
                    group = GroupInfo(
                        uuid=group_dict.get('uuid', ''),
                        name=group_dict.get('name', ''),
                        participants=group_dict.get('participants', []),
                        created_at=group_dict.get('created_at', '')
                    )
                    self.available_groups.append(group)
                
                logger.info(f"Loaded {len(self.available_groups)} groups from {self.available_groups_file}")
            else:
                logger.info(f"No existing {self.available_groups_file} found, starting with empty groups")
                
        except Exception as e:
            logger.error(f"Error loading available_groups: {e}")
            self.available_groups = []
    
    def save_weekly_progress(self):
        """Save weekly_progress to JSON file"""
        try:
            # Convert WeeklyProgress objects to dictionaries
            progress_data = {}
            for group_uuid, progress in self.weekly_progress.items():
                progress_data[group_uuid] = {
                    'group_uuid': progress.group_uuid,
                    'week_start': progress.week_start,
                    'completed_members': list(progress.completed_members),  # Convert set to list
                    'completed_members_info': progress.completed_members_info,
                    'messages_analyzed': list(progress.messages_analyzed)  # Convert set to list
                }
            
            with open(self.weekly_progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved weekly progress for {len(progress_data)} groups to {self.weekly_progress_file}")
            
        except Exception as e:
            logger.error(f"Error saving weekly_progress: {e}")
    
    def load_weekly_progress(self):
        """Load weekly_progress from JSON file"""
        try:
            if os.path.exists(self.weekly_progress_file):
                with open(self.weekly_progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                
                # Convert dictionaries back to WeeklyProgress objects
                self.weekly_progress = {}
                for group_uuid, progress_dict in progress_data.items():
                    # Ensure backward compatibility - add completed_members_info if missing
                    if 'completed_members_info' not in progress_dict:
                        progress_dict['completed_members_info'] = {}
                    
                    progress = WeeklyProgress(
                        group_uuid=progress_dict.get('group_uuid', ''),
                        week_start=progress_dict.get('week_start', ''),
                        completed_members=set(progress_dict.get('completed_members', [])),  # Convert list to set
                        completed_members_info=progress_dict.get('completed_members_info', {}),
                        messages_analyzed=set(progress_dict.get('messages_analyzed', []))  # Convert list to set
                    )
                    self.weekly_progress[group_uuid] = progress
                
                logger.info(f"Loaded weekly progress for {len(self.weekly_progress)} groups from {self.weekly_progress_file}")
            else:
                logger.info(f"No existing {self.weekly_progress_file} found, starting with empty progress")
                
        except Exception as e:
            logger.error(f"Error loading weekly_progress: {e}")
            self.weekly_progress = {}

    def save_auto_reply_members(self):
        """Save auto_reply_members to JSON file"""
        try:
            # Convert AutoReplyMember objects to dictionaries
            members_data = []
            for member in self.auto_reply_members:
                members_data.append({
                    'phone_number': member.phone_number,
                    'group_uuid': member.group_uuid,
                    'message_sent': member.message_sent,
                    'created_at': member.created_at
                })
            
            with open(self.auto_reply_members_file, 'w', encoding='utf-8') as f:
                json.dump(members_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(members_data)} auto reply members to {self.auto_reply_members_file}")
            
        except Exception as e:
            logger.error(f"Error saving auto_reply_members: {e}")
    
    def load_auto_reply_members(self):
        """Load auto_reply_members from JSON file"""
        try:
            if os.path.exists(self.auto_reply_members_file):
                with open(self.auto_reply_members_file, 'r', encoding='utf-8') as f:
                    members_data = json.load(f)
                
                # Convert dictionaries back to AutoReplyMember objects
                self.auto_reply_members = []
                for member_dict in members_data:
                    member = AutoReplyMember(
                        phone_number=member_dict.get('phone_number', ''),
                        group_uuid=member_dict.get('group_uuid', ''),
                        message_sent=member_dict.get('message_sent', ''),
                        created_at=member_dict.get('created_at', '')
                    )
                    self.auto_reply_members.append(member)
                
                logger.info(f"Loaded {len(self.auto_reply_members)} auto reply members from {self.auto_reply_members_file}")
            else:
                logger.info(f"No existing {self.auto_reply_members_file} found, starting with empty auto reply members")
                
        except Exception as e:
            logger.error(f"Error loading auto_reply_members: {e}")
            self.auto_reply_members = []

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
                logger.warning("Group creation date not available.")
                return False
            
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
            url = f"{self.base_url}/groups/{self.bot_number}"
            response = requests.get(url, headers={'X-User-API-Key': self.api_key})
            
            if response.status_code != 200:
                logger.error(f"Failed to get groups: {response.text}")
                return []
            
            groups_data = response.json()
            pilates_groups = []
            
            for group in groups_data.get('data', []):
                group_name = group.get('wa_group_name', '').lower()
                if config.PILATES_KEYWORD.lower() in group_name:
                    # Get group details including participants
                    group_details = self.get_group_details(group['uuid']).get('data', None)
                    if group_details:
                        group_created_at = group_details.get('wa_created_at', '')
                        
                        # Check if group is old enough to safely monitor
                        if not self.is_group_old_enough(group_created_at):
                            logger.info(f"Skipping recently created Pilates group: {group['wa_group_name']} (created: {group_created_at})")
                            continue
                        
                        group_info = GroupInfo(
                            uuid=group['uuid'],
                            name=group['wa_group_name'],
                            participants=group_details.get('participants', []),
                            created_at=group_created_at
                        )
                        pilates_groups.append(group_info)
                        age_days = (datetime.now(self.ireland_tz) - datetime.fromisoformat(group_created_at.replace('Z', '+00:00')).astimezone(self.ireland_tz)).days if group_created_at else "unknown"
                        logger.info(f"Found Pilates group: {group['wa_group_name']} ({group['uuid']}) - Age: {age_days} days")
            
            # Update available_groups and save to file
            self.available_groups = pilates_groups
            self.save_available_groups()
            
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
    
    def saturday_report(self):
        """Send weekly reports on Saturday at 8 AM Ireland time"""
        logger.info("Generating Saturday weekly reports...")

        self.find_pilates_groups()
        self.auto_reply_members = []
        
        for uuid, progress in self.weekly_progress.items():
            group = None
            
            for g in self.available_groups:
                if g.uuid == uuid:
                    group = g
                    break

            if not progress or not group:
                continue
            
            # Ensure backward compatibility - add completed_members_info if missing
            if not hasattr(progress, 'completed_members_info'):
                progress.completed_members_info = {}
            
            completed_numbers = progress.completed_members
            completed_members_info = progress.completed_members_info
            all_participants = {p.get('phone_number', '') for p in group.participants if p.get('phone_number')}
            incomplete_numbers = all_participants - completed_numbers
            
            # Send congratulations to group for completed members
            if completed_numbers:
                completed_count = len(completed_numbers)
                
                # Create list of completed member names for the message
                completed_names = []
                for phone_number in completed_numbers:
                    pushname = completed_members_info.get(phone_number, "Unknown")
                    if pushname != "Unknown":
                        completed_names.append(pushname)
                
                # Create enhanced group message with names
                # if completed_count <= 5:  # If few members, list their names
                names_list = ", ".join(completed_names)
                group_message = f"🎉 Well done on training! {names_list} completed their weekly pilates plan this week. Keep up the great work! 💪"
                # else:  # If many members, just show count
                    # group_message = config.GROUP_CONGRATULATIONS_TEMPLATE.format(count=completed_count)
                
                #### send messages to group ####
                # self.send_group_message(group.uuid, group_message)
                print(group_message)
            
            print("-------------------------------- incompleted members --------------------------------")
            # Send individual reminders to incomplete members and update auto_reply_members
            for phone_number in incomplete_numbers:
                if phone_number and phone_number != self.bot_number:
                    # Send reminder message
                    # self.send_individual_message(phone_number, config.INDIVIDUAL_REMINDER_TEMPLATE)
                    print(phone_number)
                    
                    # Add to auto_reply_members for future auto-replies
                    # Check if member is already in auto_reply_members
                    existing_member = None
                    for member in self.auto_reply_members:
                        if member.phone_number == phone_number and member.group_uuid == group.uuid:
                            existing_member = member
                            break
                    
                    # If not already in list, add them
                    if not existing_member:
                        current_time = datetime.now(self.ireland_tz).isoformat()
                        auto_reply_member = AutoReplyMember(
                            phone_number=phone_number,
                            group_uuid=group.uuid,
                            message_sent=config.INDIVIDUAL_REMINDER_TEMPLATE,
                            created_at=current_time
                        )
                        self.auto_reply_members.append(auto_reply_member)
                        logger.info(f"Added {phone_number} to auto_reply_members for group {group.name}")
            
            logger.info(f"Group {group.name}: {len(completed_numbers)} completed, {len(incomplete_numbers)} reminded")
        
        # Save updated auto_reply_members after processing all groups
        self.save_auto_reply_members()
        logger.info(f"Updated auto_reply_members list with {len(self.auto_reply_members)} members")
    
    def process_webhook_message(self, webhook_data: Dict):
        """Process incoming webhook message from 2chat"""
        try:
            # Extract message details from webhook data (matches listener.json format)
            message_id = webhook_data.get('id', '')
            message_uuid = webhook_data.get('uuid', '')
            created_at = webhook_data.get('created_at', '')
            sent_by = webhook_data.get('sent_by', '')
            
            # Get message text
            message_obj = webhook_data.get('message', {})
            text_content = message_obj.get('text', '')
            
            # Get participant (sender) information
            participant = webhook_data.get('participant', {})
            from_number = participant.get('phone_number', '')
            sender_name = participant.get('pushname', '')
            
            # Get group information
            group_info = webhook_data.get('group', {})
            group_uuid = group_info.get('uuid', '') if group_info else ''
            group_name = group_info.get('wa_group_name', '') if group_info else ''
            group_created_at = group_info.get('wa_created_at', '') if group_info else ''
            
            # Get bot's channel phone number
            channel_phone_number = webhook_data.get('channel_phone_number', '')
            
            logger.info(f"Processing webhook message: {message_id} from {from_number} ({sender_name}) in group: {group_name}")
            
            # Check if this group is in our available pilates groups
            group_found = False
            for available_group in self.available_groups:
                if available_group.uuid == group_uuid:
                    group_found = True
                    break
            
            if not group_found:
                logger.info(f"Group {group_name} not in available pilates groups, skipping")
                return

            # Only process user messages (not bot messages)
            if sent_by != 'user':
                logger.info(f"Skipping non-user message, sent_by: {sent_by}")
                return
            
            # Skip if message is from bot itself
            if from_number == self.bot_number or channel_phone_number == from_number:
                logger.info("Skipping message from bot itself")
                return
            
            # Only process group messages
            if not group_uuid or not group_info:
                logger.info("Skipping non-group message")
                return
            
            # Check if this is a pilates group by name
            if not group_name or config.PILATES_KEYWORD.lower() not in group_name.lower():
                logger.info(f"Message not from a pilates group: {group_name}")
                return
            
            # Check if group is old enough (safety feature)
            if group_created_at and not self.is_group_old_enough(group_created_at):
                logger.info(f"Skipping message from recently created group: {group_name} (created: {group_created_at})")
                return
            
            # Process the message for completion tracking
            week_start = self.get_current_week_start()
            
            # Initialize weekly progress if not exists
            if group_uuid not in self.weekly_progress:
                self.weekly_progress[group_uuid] = WeeklyProgress(
                    group_uuid=group_uuid,
                    week_start=week_start,
                    completed_members=set(),
                    completed_members_info={},
                    messages_analyzed=set()
                )
            
            progress = self.weekly_progress[group_uuid]
            
            # Ensure backward compatibility - add completed_members_info if missing
            if not hasattr(progress, 'completed_members_info'):
                progress.completed_members_info = {}
            
            # Reset if new week
            if progress.week_start != week_start:
                progress.week_start = week_start
                progress.completed_members.clear()
                progress.completed_members_info.clear()
                progress.messages_analyzed.clear()
            
            # Skip if already analyzed
            if message_id in progress.messages_analyzed:
                logger.info(f"Message {message_id} already analyzed")
                return

            if from_number in progress.completed_members:
                logger.info(f"This user {from_number}:{sender_name} complete his work.")
                return
            
            # Check if message is from this week
            try:
                # Parse timestamp (format: "2025-08-15T07:56:11")
                if created_at:
                    if 'Z' in created_at:
                        msg_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        # Add timezone info if missing
                        msg_datetime = datetime.fromisoformat(created_at)
                        if msg_datetime.tzinfo is None:
                            msg_datetime = msg_datetime.replace(tzinfo=pytz.UTC)
                    
                    msg_datetime = msg_datetime.astimezone(self.ireland_tz)
                    week_start_date = datetime.strptime(week_start, '%Y-%m-%d').replace(tzinfo=self.ireland_tz)
                    
                    if msg_datetime < week_start_date:
                        logger.info("Message is from previous week, skipping")
                        return
            except Exception as e:
                logger.warning(f"Could not parse timestamp '{created_at}': {e}")
                # Assume message is current if parsing fails
                pass
            
            # Analyze message with Gemini
            if text_content and self.analyze_message_with_gemini(text_content):
                progress.completed_members.add(from_number)
                progress.completed_members_info[from_number] = sender_name or "Unknown"
                logger.info(f"Member {from_number} ({sender_name}) completed weekly plan in group {group_name}")
            
            progress.messages_analyzed.add(message_id)
            
            # Save progress after each update
            self.save_weekly_progress()
            
        except Exception as e:
            logger.error(f"Error processing webhook message: {e}")
            logger.error(f"Webhook data: {webhook_data}")
    
    def process_private_message(self, webhook_data: Dict):
        """Process incoming private message from 2chat"""
        try:
            # Extract message details from webhook data
            message_id = webhook_data.get('id', '')
            message_uuid = webhook_data.get('uuid', '')
            sent_by = webhook_data.get('sent_by', '')
            
            # Get message text
            message_obj = webhook_data.get('message', {})
            text_content = message_obj.get('text', '')
            
            # Get sender information
            from_number =webhook_data.get('remote_phone_number', '')
            sender_name = webhook_data.get('contact', {}).get('first_name', '') or webhook_data.get('contact', {}).get('last_name', '') or webhook_data.get('contact', {}).get('friendly_name', '')
            
            # Get bot's channel phone number
            channel_phone_number = webhook_data.get('channel_phone_number', '')
            
            logger.info(f"Processing private message: {message_id} from {from_number} ({sender_name})")
            
            # Only process user messages (not bot messages)
            if sent_by != 'user':
                logger.info(f"Skipping non-user message, sent_by: {sent_by}")
                return
            
            # Skip if message is from bot itself
            if from_number == self.bot_number or channel_phone_number == from_number:
                logger.info("Skipping message from bot itself")
                return
            
            # Check if this sender is in auto_reply_members
            auto_reply_member = None
            for member in self.auto_reply_members:
                if member.phone_number == from_number:
                    auto_reply_member = member
                    break
            
            if not auto_reply_member:
                logger.info(f"User {from_number} not in auto_reply_members list")
                return
            
            # Generate auto reply using Gemini
            reply_message = self.generate_auto_reply(auto_reply_member.message_sent, text_content, sender_name)
            
            if reply_message:
                # Send the auto reply
                print(reply_message)
                # success = self.send_individual_message(from_number, reply_message)
                
                # if success:
                #     logger.info(f"Auto reply sent to {from_number} ({sender_name})")
                    
                #     # Remove member from auto_reply_members after successful reply
                #     self.auto_reply_members.remove(auto_reply_member)
                #     self.save_auto_reply_members()
                #     logger.info(f"Removed {from_number} from auto_reply_members")
                # else:
                #     logger.error(f"Failed to send auto reply to {from_number}")
            else:
                logger.error(f"Failed to generate auto reply for {from_number}")
                
        except Exception as e:
            logger.error(f"Error processing private message: {e}")
            logger.error(f"Webhook data: {webhook_data}")
    
    def generate_auto_reply(self, original_message: str, user_response: str, user_name: str) -> str:
        """Generate auto reply using Gemini based on original message and user response"""
        try:
            prompt = f"""
You are a friendly pilates instructor bot. You previously sent this message to a member who didn't complete their weekly pilates plan:
"{original_message}"

The member ({user_name}) has now replied with:
"{user_response}"

Generate a supportive, encouraging, and personalized response to their message. Keep it friendly and motivating. Consider their response and provide appropriate support or encouragement for their pilates journey.

Response should be in a conversational tone and not too long (2-3 sentences maximum).
"""
            
            response = self.model.generate_content(prompt)
            reply = response.text.strip()
            
            logger.info(f"Generated auto reply for {user_name}: {reply[:50]}...")
            return reply
            
        except Exception as e:
            logger.error(f"Error generating auto reply with Gemini: {e}")
            return ""
    
    def start_scheduler(self):
        """Start the scheduled tasks in a separate thread"""
        logger.info("Starting scheduler for weekly reports...")
        
        # Schedule Saturday reports (Ireland timezone)
        schedule.every().saturday.at(config.SATURDAY_REPORT_TIME).do(self.saturday_report)
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks


# Global bot instance
bot_instance = None

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    @app.route("/", methods=["GET"])
    def index():
        return {"status": "WhatsApp Pilates Bot is running", "webhook": "/webhook"}, 200

    @app.route("/webhook", methods=["POST"])
    def webhook():
        """Handle incoming webhooks from 2chat"""
        if not request.is_json:
            logger.error("Webhook received non-JSON data")
            return {"error": "Expected JSON"}, 400
        
        try:
            data = request.get_json()
            logger.info(f"Received webhook: {data}")
            
            # Process webhook with bot instance
            if bot_instance:
                bot_instance.process_webhook_message(data)
            else:
                logger.error("Bot instance not initialized")
                return {"error": "Bot not ready"}, 500
            
            return {"status": "success"}, 200
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/receive_chat_message", methods=["POST"])
    def receive_chat_message():
        """Handle incoming private chat messages from 2chat"""
        if not request.is_json:
            logger.error("Chat webhook received non-JSON data")
            return {"error": "Expected JSON"}, 400
        
        try:
            data = request.get_json()
            logger.info(f"Received chat message webhook: {data}")
            
            # Process chat message with bot instance
            if bot_instance:
                bot_instance.process_private_message(data)
            else:
                logger.error("Bot instance not initialized")
                return {"error": "Bot not ready"}, 500
            
            return {"status": "success"}, 200
            
        except Exception as e:
            logger.error(f"Error processing chat message webhook: {e}")
            return {"error": "Internal server error"}, 500

    return app

def main():
    """Main function to run the bot with Flask webhook"""
    global bot_instance
    
    # Load configuration
    TWOCHAT_API_KEY = config.TWOCHAT_API_KEY
    GEMINI_API_KEY = config.GEMINI_API_KEY
    BOT_NUMBER = config.BOT_NUMBER
    NGROK_TOKEN = config.NGROK_TOKEN
    
    if not GEMINI_API_KEY:
        logger.error("Please set your Gemini API key in the GEMINI_API_KEY environment variable or config.py")
        return
    
    if not TWOCHAT_API_KEY:
        logger.error("Please set your 2Chat API key in the TWOCHAT_API_KEY environment variable or config.py")
        return
    
    if not NGROK_TOKEN:
        logger.error("Please set your ngrok auth token in the NGROK_TOKEN environment variable or config.py")
        return
    
    # Create bot instance
    bot_instance = WhatsAppPilatesBot(
        api_key=TWOCHAT_API_KEY,
        gemini_api_key=GEMINI_API_KEY,
        bot_number=BOT_NUMBER
    )
    
    # Create Flask app
    app = create_app()
    
    try:
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=bot_instance.start_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Scheduler started in background")
        
        # Start ngrok tunnel
        ngrok.set_auth_token(NGROK_TOKEN)
        public_url = ngrok.connect(5000)
        logger.info(f"ngrok tunnel URL: {public_url}")
        print(f"🚀 Group Messages Webhook URL: {public_url}/webhook")
        print(f"🚀 Private Messages Webhook URL: {public_url}/receive_chat_message")
        print("📝 Configure these URLs in your 2chat webhook settings")
        print("   - Use /webhook for group message events")
        print("   - Use /receive_chat_message for private chat message events")
        
        # Start Flask server
        logger.info("Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    main()
