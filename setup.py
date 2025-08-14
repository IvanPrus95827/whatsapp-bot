#!/usr/bin/env python3
"""
Setup script for WhatsApp Pilates Bot
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False

def setup_environment():
    """Guide user through environment setup"""
    print("\n=== Environment Setup ===")
    print("Please set up your API keys:")
    print()
    
    print("1. Get your 2Chat API key from: https://2chat.io")
    print("2. Get your Gemini AI API key from: https://aistudio.google.com")
    print()
    
    print("3. Set environment variables (recommended):")
    print("   export TWOCHAT_API_KEY='your-2chat-api-key'")
    print("   export GEMINI_API_KEY='your-gemini-api-key'")
    print("   export BOT_NUMBER='+353873326005'")
    print()
    
    print("   OR edit config.py directly with your API keys")
    print()

def main():
    """Main setup function"""
    print("WhatsApp Pilates Bot - Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("\nSetup failed. Please fix package installation issues.")
        return 1
    
    # Setup environment
    setup_environment()
    
    print("Setup complete! Next steps:")
    print("1. Configure your API keys")
    print("2. Run: python test_bot.py (to test setup)")
    print("3. Run: python whatsapp_pilates_bot.py (to start the bot)")
    
    return 0

if __name__ == "__main__":
    exit(main())
