#!/usr/bin/env python3
"""
Simple test script for AI Service configuration
"""

import os
import sys
from pathlib import Path

# Add src and root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

def test_config():
    """Test AI configuration"""
    
    print("=== AI Configuration Test ===")
    print(f"AI Provider: {settings.AI_PROVIDER}")
    print(f"GROQ API Key: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
    print(f"GPT API Key: {'Set' if settings.GPT_API_KEY else 'Not set'}")
    print()
    
    # Check if current provider has API key
    if settings.AI_PROVIDER.upper() == "GROQ":
        if settings.GROQ_API_KEY:
            print("✅ GROQ provider configured correctly")
        else:
            print("❌ GROQ provider selected but API key not set")
    elif settings.AI_PROVIDER.upper() == "GPT":
        if settings.GPT_API_KEY:
            print("✅ GPT provider configured correctly")
        else:
            print("❌ GPT provider selected but API key not set")
    else:
        print(f"❌ Invalid AI provider: {settings.AI_PROVIDER}")
    
    print()
    print("Configuration test completed!")

if __name__ == "__main__":
    test_config()
