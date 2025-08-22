#!/usr/bin/env python3
"""
Script to switch between AI providers
"""

import os
import sys
from pathlib import Path

def switch_ai_provider(provider: str):
    """
    Switch AI provider by updating .env file
    
    Args:
        provider: 'GROQ' or 'GPT'
    """
    provider = provider.upper()
    
    if provider not in ['GROQ', 'GPT']:
        print(f"❌ Invalid provider: {provider}")
        print("   Valid options: GROQ, GPT")
        return False
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please create a .env file first using env.example as template")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update AI_PROVIDER line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('AI_PROVIDER='):
            lines[i] = f'AI_PROVIDER={provider}\n'
            updated = True
            break
    
    # If AI_PROVIDER not found, add it
    if not updated:
        lines.append(f'AI_PROVIDER={provider}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ AI provider switched to: {provider}")
    print(f"   Restart the application for changes to take effect")
    return True

def show_current_provider():
    """Show current AI provider configuration"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return
    
    # Read .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Extract AI_PROVIDER
    for line in content.split('\n'):
        if line.startswith('AI_PROVIDER='):
            provider = line.split('=')[1].strip()
            print(f"Current AI Provider: {provider}")
            
            # Check if API key is set
            if provider == 'GROQ':
                has_key = 'GROQ_API_KEY=' in content and not content.split('GROQ_API_KEY=')[1].split('\n')[0].strip() == ''
            elif provider == 'GPT':
                has_key = 'GPT_API_KEY=' in content and not content.split('GPT_API_KEY=')[1].split('\n')[0].strip() == ''
            else:
                has_key = False
            
            if has_key:
                print(f"✅ {provider} API key is configured")
            else:
                print(f"⚠️  {provider} API key is not configured")
            return
    
    print("❌ AI_PROVIDER not found in .env file")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("AI Provider Switch Script")
        print("=" * 30)
        print("Usage:")
        print("  python switch_ai_provider.py GROQ    # Switch to GROQ")
        print("  python switch_ai_provider.py GPT     # Switch to GPT")
        print("  python switch_ai_provider.py status  # Show current provider")
        print()
        show_current_provider()
        return
    
    command = sys.argv[1].upper()
    
    if command == 'STATUS':
        show_current_provider()
    elif command in ['GROQ', 'GPT']:
        switch_ai_provider(command)
    else:
        print(f"❌ Unknown command: {command}")
        print("   Valid commands: GROQ, GPT, status")

if __name__ == "__main__":
    main()
