#!/usr/bin/env python3
"""
Test script for AI Service with multiple providers
"""

import os
import sys
import logging
from pathlib import Path

# Add src and root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_service import AIService
from config.settings import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_ai_service():
    """Test AI service with current configuration"""
    
    print("=== AI Service Test ===")
    print(f"Current AI Provider: {settings.AI_PROVIDER}")
    print(f"GROQ API Key: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
    print(f"GPT API Key: {'Set' if settings.GPT_API_KEY else 'Not set'}")
    print()
    
    try:
        # Initialize AI service
        ai_service = AIService()
        provider_info = ai_service.get_provider_info()
        
        print(f"✅ AI Service initialized successfully")
        print(f"   Provider: {provider_info['provider']}")
        print(f"   Model: {provider_info['model']}")
        print(f"   Healthy: {provider_info['healthy']}")
        print()
        
        # Test health check
        if ai_service.is_healthy():
            print("✅ AI Service health check passed")
        else:
            print("❌ AI Service health check failed")
            return
        
        # Test cardio analysis
        print("\n--- Testing Cardio Analysis ---")
        try:
            analysis = ai_service.get_cardio_analysis(
                age=45,
                pulse=85,
                risk="Medium",
                symptoms="Chest pain, shortness of breath"
            )
            print("✅ Cardio analysis successful")
            print(f"Response length: {len(analysis)} characters")
            print(f"Preview: {analysis[:200]}...")
        except Exception as e:
            print(f"❌ Cardio analysis failed: {e}")
        
        # Test health advice
        print("\n--- Testing Health Advice ---")
        try:
            advice = ai_service.get_health_advice(
                condition="High blood pressure"
            )
            print("✅ Health advice successful")
            print(f"Response length: {len(advice)} characters")
            print(f"Preview: {advice[:200]}...")
        except Exception as e:
            print(f"❌ Health advice failed: {e}")
            
    except Exception as e:
        print(f"❌ AI Service initialization failed: {e}")
        return False
    
    return True

def test_both_providers():
    """Test both AI providers by temporarily changing settings"""
    
    print("\n=== Testing Both AI Providers ===")
    
    # Store original settings
    original_provider = settings.AI_PROVIDER
    
    # Test GROQ
    if settings.GROQ_API_KEY:
        print("\n--- Testing GROQ Provider ---")
        settings.AI_PROVIDER = "GROQ"
        if test_ai_service():
            print("✅ GROQ provider test passed")
        else:
            print("❌ GROQ provider test failed")
    else:
        print("⚠️  GROQ API key not set, skipping GROQ test")
    
    # Test GPT
    if settings.GPT_API_KEY:
        print("\n--- Testing GPT Provider ---")
        settings.AI_PROVIDER = "GPT"
        if test_ai_service():
            print("✅ GPT provider test passed")
        else:
            print("❌ GPT provider test failed")
    else:
        print("⚠️  GPT API key not set, skipping GPT test")
    
    # Restore original settings
    settings.AI_PROVIDER = original_provider

if __name__ == "__main__":
    print("AI Service Test Script")
    print("=" * 50)
    
    # Test current configuration
    test_ai_service()
    
    # Test both providers if both API keys are available
    if settings.GROQ_API_KEY and settings.GPT_API_KEY:
        test_both_providers()
    else:
        print("\n⚠️  Both API keys not available, skipping provider comparison")
        print("   Set both GROQ_API_KEY and GPT_API_KEY to test both providers")
    
    print("\n" + "=" * 50)
    print("Test completed!")
