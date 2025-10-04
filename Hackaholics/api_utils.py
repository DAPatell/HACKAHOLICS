import requests

def get_country_currency(country):
    """Get currency for a country"""
    currency_map = {
        'India': 'INR',
        'United States': 'USD',
        'United Kingdom': 'GBP',
        'Canada': 'CAD',
        'Australia': 'AUD',
        'Germany': 'EUR',
        'France': 'EUR',
        'Japan': 'JPY',
        'China': 'CNY',
        'Brazil': 'BRL'
    }
    return currency_map.get(country, 'USD')

def convert_currency(amount, from_currency, to_currency):
    """Convert currency amount"""
    if from_currency == to_currency:
        return amount
    
    # Simple conversion rates (in production, use real API)
    rates = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.73,
        'INR': 74.0,
        'CAD': 1.25,
        'AUD': 1.35,
        'JPY': 110.0,
        'CNY': 6.45,
        'BRL': 5.2
    }
    
    usd_amount = amount / rates.get(from_currency, 1.0)
    return usd_amount * rates.get(to_currency, 1.0)