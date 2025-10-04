#!/usr/bin/env python3
"""
Test script to verify API integrations
"""

import requests

def test_country_api():
    """Test restcountries.com API"""
    print("Testing Country API...")
    try:
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,currencies')
        response.raise_for_status()
        countries_data = response.json()
        print(f"✅ Country API working - Found {len(countries_data)} countries")
        
        # Test specific country lookup
        for country_data in countries_data[:5]:  # Test first 5 countries
            name = country_data['name']['common']
            currencies = country_data.get('currencies', {})
            if currencies:
                currency = list(currencies.keys())[0]
                print(f"  {name}: {currency}")
        return True
    except Exception as e:
        print(f"❌ Country API failed: {e}")
        return False

def test_currency_api():
    """Test exchangerate-api.com API"""
    print("\nTesting Currency API...")
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        response.raise_for_status()
        rates = response.json()['rates']
        print(f"✅ Currency API working - Found {len(rates)} currencies")
        
        # Test specific conversions
        test_currencies = ['EUR', 'GBP', 'JPY', 'CAD']
        for currency in test_currencies:
            if currency in rates:
                rate = rates[currency]
                print(f"  1 USD = {rate} {currency}")
        return True
    except Exception as e:
        print(f"❌ Currency API failed: {e}")
        return False

if __name__ == "__main__":
    print("API Integration Test")
    print("=" * 50)
    
    country_ok = test_country_api()
    currency_ok = test_currency_api()
    
    print("\n" + "=" * 50)
    if country_ok and currency_ok:
        print("✅ All APIs working correctly!")
    else:
        print("❌ Some APIs failed")
