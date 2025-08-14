#!/usr/bin/env python3
"""
Test script for WhatsApp Pilates Bot
This script tests individual components without running the full bot
"""

import sys
import os
import logging
from whatsapp_pilates_bot import WhatsAppPilatesBot
import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_configuration():
    """Test if configuration is properly loaded"""
    print("=== Testing Configuration ===")
    print(f"2Chat API Key: {'✓ Set' if config.TWOCHAT_API_KEY else '✗ Missing'}")
    print(f"Gemini API Key: {'✓ Set' if config.GEMINI_API_KEY else '✗ Missing'}")
    print(f"Bot Number: {config.BOT_NUMBER}")
    print(f"Ireland Timezone: {config.IRELAND_TIMEZONE}")
    print(f"Saturday Report Time: {config.SATURDAY_REPORT_TIME}")
    print()

def test_bot_initialization():
    """Test if the bot can be initialized"""
    print("=== Testing Bot Initialization ===")
    try:
        if not config.GEMINI_API_KEY:
            print("✗ Cannot test bot initialization - Gemini API key missing")
            return False
        
        bot = WhatsAppPilatesBot(
            api_key=config.TWOCHAT_API_KEY,
            gemini_api_key=config.GEMINI_API_KEY,
            bot_number=config.BOT_NUMBER
        )
        print("✓ Bot initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Bot initialization failed: {e}")
        return False

def test_gemini_analysis():
    """Test Gemini AI message analysis"""
    print("=== Testing Gemini Analysis ===")
    try:
        if not config.GEMINI_API_KEY:
            print("✗ Cannot test Gemini - API key missing")
            return False
        
        bot = WhatsAppPilatesBot(
            api_key=config.TWOCHAT_API_KEY,
            gemini_api_key=config.GEMINI_API_KEY,
            bot_number=config.BOT_NUMBER
        )
        
        # Test messages
        test_messages = [
            ("I finished my pilates workout today!", True),
            ("Completed my weekly training plan", True),
            ("Just checking in with everyone", False),
            ("What time is class tomorrow?", False),
            ("Done with this week's exercises!", True)
        ]
        
        for message, expected in test_messages:
            try:
                result = bot.analyze_message_with_gemini(message)
                status = "✓" if result == expected else "✗"
                print(f"{status} '{message[:30]}...' -> {result} (expected {expected})")
            except Exception as e:
                print(f"✗ Error analyzing '{message[:30]}...': {e}")
        
        return True
    except Exception as e:
        print(f"✗ Gemini testing failed: {e}")
        return False

def test_2chat_connection():
    """Test 2Chat API connection"""
    print("=== Testing 2Chat Connection ===")
    try:
        bot = WhatsAppPilatesBot(
            api_key=config.TWOCHAT_API_KEY,
            gemini_api_key=config.GEMINI_API_KEY or "dummy",
            bot_number=config.BOT_NUMBER
        )
        
        # Try to get groups (this will test API connectivity)
        groups = bot.find_pilates_groups()
        print(f"✓ Found {len(groups)} Pilates groups")
        
        for group in groups:
            print(f"  - {group.name} ({group.uuid})")
            print(f"    Members: {len(group.participants)}")
        
        return True
    except Exception as e:
        print(f"✗ 2Chat connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("WhatsApp Pilates Bot - Test Suite")
    print("=" * 50)
    
    test_configuration()
    
    init_success = test_bot_initialization()
    if not init_success:
        print("\n⚠️  Bot initialization failed. Please check your API keys.")
        return
    
    # Test 2Chat first (doesn't require Gemini)
    chat_success = test_2chat_connection()
    
    # Test Gemini if available
    if config.GEMINI_API_KEY:
        gemini_success = test_gemini_analysis()
    else:
        print("\n⚠️  Skipping Gemini tests - API key not configured")
        gemini_success = False
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"2Chat API: {'✓ Working' if chat_success else '✗ Failed'}")
    print(f"Gemini AI: {'✓ Working' if gemini_success else '✗ Failed/Not configured'}")
    
    if chat_success and gemini_success:
        print("\n🎉 All tests passed! Your bot is ready to run.")
    elif chat_success:
        print("\n⚠️  2Chat is working but Gemini needs configuration.")
    else:
        print("\n❌ Please fix the issues above before running the bot.")

if __name__ == "__main__":
    main()
