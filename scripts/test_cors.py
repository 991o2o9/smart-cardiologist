#!/usr/bin/env python3
"""
Simple CORS Test Script
"""

import requests

def test_cors():
    url = "https://fastapi-app-963329908787.europe-central2.run.app"
    
    # Test different origins
    test_origins = [
        "https://pulseai-lovat.vercel.app",
        "http://localhost:3000",
        "https://example.com"
    ]
    
    print("🔍 Testing CORS Configuration")
    print("=" * 40)
    
    for origin in test_origins:
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
        
        try:
            response = requests.options(f"{url}/auth/register", headers=headers)
            allow_origin = response.headers.get('access-control-allow-origin', 'Not set')
            
            if response.status_code == 200:
                print(f"✅ {origin} -> {allow_origin}")
            else:
                print(f"❌ {origin} -> Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {origin} -> Error: {e}")
    
    print("\n📋 Config endpoint:")
    try:
        response = requests.get(f"{url}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ CORS config: {config.get('allowed_origins', 'Not found')}")
            print(f"   All origins allowed: {config.get('cors_all_origins_allowed', 'Unknown')}")
        else:
            print(f"❌ Config endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Config endpoint error: {e}")

if __name__ == "__main__":
    test_cors()
