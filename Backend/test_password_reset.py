#!/usr/bin/env python3
"""
Test script for password reset functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_password_reset_flow():
    """Test complete password reset flow"""
    print("Testing Password Reset Flow")
    print("=" * 50)
    
    # Test 1: Request password reset
    print("1. Testing password reset request...")
    reset_data = {
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/password/request_reset", json=reset_data)
    print(f"Reset request status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Validate token (this would normally come from email)
    print("\n2. Testing token validation...")
    # Note: In real scenario, token would come from email
    test_token = "invalid_token_for_testing"
    validate_data = {"token": test_token}
    
    response = requests.post(f"{BASE_URL}/password/validate_token", json=validate_data)
    print(f"Token validation status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Test change password (requires authentication)
    print("\n3. Testing change password (requires login first)...")
    # First login to get token
    login_data = {
        "email": "test@example.com",
        "password": "password"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        change_data = {
            "current_password": "password",
            "new_password": "newpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/password/change_password", json=change_data, headers=headers)
        print(f"Change password status: {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print("Login failed - cannot test change password")
    
    print("\n" + "=" * 50)
    print("Password reset tests completed!")

def test_email_configuration():
    """Test email configuration"""
    print("\nTesting Email Configuration")
    print("=" * 30)
    
    # This would test if email settings are properly configured
    print("Email configuration test would go here...")
    print("Make sure to set MAIL_USERNAME and MAIL_PASSWORD environment variables")

if __name__ == "__main__":
    try:
        test_password_reset_flow()
        test_email_configuration()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the application.")
        print("Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")
