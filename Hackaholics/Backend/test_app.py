#!/usr/bin/env python3
"""
Simple test script to verify the Flask application is working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_signup():
    """Test user signup"""
    print("Testing signup...")
    data = {
        "username": "testuser",
        "email": "testuser@example.com", 
        "password": "testpass123",
        "country": "USA"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    print(f"Signup Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Access Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting login...")
    data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Access Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    print("\nTesting protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting all expenses (admin endpoint)
    response = requests.get(f"{BASE_URL}/admin/all_expenses", headers=headers)
    print(f"Protected endpoint Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Expenses: {result}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Flask Application Test")
    print("=" * 50)
    
    try:
        # Test signup
        token = test_signup()
        
        if token:
            # Test login
            login_token = test_login()
            
            if login_token:
                # Test protected endpoint
                test_protected_endpoint(login_token)
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the application.")
        print("Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
<<<<<<< HEAD
        print(f"Error: {e}")
=======
        print(f"Error: {e}")
>>>>>>> 1abd9f33606ff953fc8975f17f8e0da064520f4f
