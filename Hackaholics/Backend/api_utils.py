"""
Utility functions for external API integrations
"""
import requests

def get_country_currency(country_name):
    """Get currency for a country using restcountries.com API"""
    try:
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,currencies')
        response.raise_for_status()
        countries_data = response.json()
        
        for country_data in countries_data:
            if (country_data['name']['common'].lower() == country_name.lower() or 
                country_data['name']['official'].lower() == country_name.lower()):
                currencies = country_data.get('currencies', {})
                if currencies:
                    return list(currencies.keys())[0]
        return 'USD'  # Default fallback
    except requests.RequestException:
        return 'USD'  # Default fallback

def convert_currency(amount, from_cur, to_cur):
    """Convert currency using exchangerate-api.com"""
    if from_cur == to_cur:
        return amount
    
    try:
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_cur}')
        response.raise_for_status()
        rates = response.json()['rates']
        return amount * rates.get(to_cur, 1.0)
    except requests.RequestException:
        # Fallback to 1:1 if API fails
<<<<<<< HEAD
        return amount
=======
        return amount
>>>>>>> 1abd9f33606ff953fc8975f17f8e0da064520f4f
