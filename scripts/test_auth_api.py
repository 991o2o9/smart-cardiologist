#!/usr/bin/env python3
"""
Test script for authentication API endpoints
"""

import requests
import json
import time
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class AuthAPITester:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session = requests.Session()
    
    def test_register(self) -> bool:
        """Test user registration"""
        print(f"✅ Testing user registration: {TEST_EMAIL}")
        
        url = f"{BASE_URL}/auth/register"
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Registration successful: {result['message']}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Registration error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during registration: {e}")
            return False
    
    def test_activate(self) -> bool:
        """Test account activation"""
        print(f"✅ Testing account activation: {TEST_EMAIL}")
        
        # Note: In real scenario, you would get activation code from email
        # For testing, we'll use a dummy code
        url = f"{BASE_URL}/auth/activate"
        data = {
            "email": TEST_EMAIL,
            "activation_code": "123456"  # Dummy code
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Activation successful: {result['message']}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Activation error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during activation: {e}")
            return False
    
    def test_login(self) -> bool:
        """Test user login"""
        print(f"✅ Testing user login: {TEST_EMAIL}")
        
        url = f"{BASE_URL}/auth/login"
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result['access_token']
                self.refresh_token = result['refresh_token']
                print(f"✅ Login successful! Token received")
                return True
            else:
                error_data = response.json()
                print(f"❌ Login error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def test_protected_endpoint(self) -> bool:
        """Test access to protected endpoint"""
        if not self.access_token:
            print("❌ No token for testing protected endpoint")
            return False
        
        print("✅ Testing protected endpoint access")
        
        url = f"{BASE_URL}/auth/me"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Protected endpoint accessible: {result['email']}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Access error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing protected endpoint: {e}")
            return False
    
    def test_cardio_analysis(self) -> bool:
        """Test cardio analysis endpoint"""
        if not self.access_token:
            print("❌ No token for testing cardio analysis")
            return False
        
        print("✅ Testing cardio analysis endpoint")
        
        url = f"{BASE_URL}/cardio-assistant/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": "What are the symptoms of heart disease?"
                }
            ]
        }
        
        try:
            response = self.session.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Cardio analysis successful: {len(result['response'])} characters")
                return True
            else:
                error_data = response.json()
                print(f"❌ Cardio analysis error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during cardio analysis: {e}")
            return False
    
    def test_history(self) -> bool:
        """Test chat history endpoint"""
        if not self.access_token:
            print("❌ No token for testing history")
            return False
        
        print("✅ Testing chat history endpoint")
        
        url = f"{BASE_URL}/cardio-assistant/history"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ History retrieved: {len(result)} chats")
                return True
            else:
                error_data = response.json()
                print(f"❌ History retrieval error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during history retrieval: {e}")
            return False
    
    def test_refresh_token(self) -> bool:
        """Test token refresh"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        print("✅ Testing token refresh")
        
        url = f"{BASE_URL}/auth/refresh"
        data = {
            "refresh_token": self.refresh_token
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result['access_token']
                print("✅ Token refreshed successfully!")
                return True
            else:
                error_data = response.json()
                print(f"❌ Token refresh error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during token refresh: {e}")
            return False
    
    def test_logout(self) -> bool:
        """Test user logout"""
        if not self.access_token:
            print("❌ No token for logout")
            return False
        
        print("✅ Testing user logout")
        
        url = f"{BASE_URL}/auth/logout"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.post(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Logout successful: {result['message']}")
                # Clear tokens
                self.access_token = None
                self.refresh_token = None
                return True
            else:
                error_data = response.json()
                print(f"❌ Logout error: {error_data}")
                return False
                
        except Exception as e:
            print(f"❌ Error during logout: {e}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting authentication API tests...\n")
        
        tests = [
            ("Registration", self.test_register),
            ("Activation", self.test_activate),
            ("Login", self.test_login),
            ("Protected Endpoint", self.test_protected_endpoint),
            ("Cardio Analysis", self.test_cardio_analysis),
            ("History", self.test_history),
            ("Token Refresh", self.test_refresh_token),
            ("Logout", self.test_logout)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                print()
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ Critical error in {test_name}: {e}")
                results.append((test_name, False))
                print()
        
        # Summary
        print("📊 Test Results Summary:")
        print("=" * 40)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:20} {status}")
            if success:
                passed += 1
        
        print("=" * 40)
        print(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed")

def main():
    """Main function"""
    try:
        tester = AuthAPITester()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"\n\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
