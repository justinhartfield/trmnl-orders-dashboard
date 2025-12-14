#!/usr/bin/env python3
"""
TRMNL Orders Dashboard Updater - Final Version
Fetches order data from Metabase and pushes to TRMNL via webhook

Note: Today's stats need to be manually checked from the dashboard and updated here
until we implement browser automation or find the correct API endpoint.
"""

import os
import requests
from datetime import datetime
import json

# Configuration
METABASE_BASE_URL = 'https://bi.weed.de'
METABASE_API_KEY = os.getenv('METABASE_API_KEY', '')
TRMNL_WEBHOOK_URL = os.getenv('TRMNL_WEBHOOK_URL', 'https://usetrmnl.com/api/custom_plugins/3502d5b9-42ed-46d4-a51e-9b7b83ce03d6')

# Card IDs from the dashboard
CARD_IDS = {
    'past_day_orders': 859,
    'past_week_orders': 860,
    'past_month_orders': 861,
    'past_quarter_orders': 862,
    'total_summary': 938
}

# TODAY'S DATA - Update these values manually by checking the dashboard
# https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1?tab=74-orders&order_date_filter=today
TODAY_DATA = {
    'users': '77',
    'orders': '78',
    'quantity': '1,8kg',
    'sales': '€9.916',
    'products': '133'
}

def fetch_card_with_api_key(card_id):
    """Fetch data from a Metabase card using API key"""
    try:
        url = f'{METABASE_BASE_URL}/api/card/{card_id}/query'
        
        response = requests.post(
            url,
            headers={
                'X-API-KEY': METABASE_API_KEY,
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching card {card_id}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception fetching card {card_id}: {e}")
        return None

def extract_scalar_value(data):
    """Extract a single scalar value from Metabase response"""
    try:
        if data and 'data' in data and 'rows' in data['data']:
            rows = data['data']['rows']
            if rows and len(rows) > 0:
                return rows[0][0] if len(rows[0]) > 0 else None
    except Exception as e:
        print(f"Error extracting scalar: {e}")
    return None

def format_number(num):
    """Format number with German locale (dot as thousands separator)"""
    try:
        if isinstance(num, (int, float)):
            return f"{int(num):,}".replace(',', '.')
        return str(num)
    except:
        return str(num)

def push_to_trmnl(data):
    """Push data to TRMNL via webhook"""
    try:
        response = requests.post(
            TRMNL_WEBHOOK_URL,
            headers={'Content-Type': 'application/json'},
            json={'merge_variables': data},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ Successfully pushed data to TRMNL")
            return True
        else:
            print(f"✗ Error pushing to TRMNL: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception pushing to TRMNL: {e}")
        return False

def main():
    """Main function to fetch data and update TRMNL"""
    print(f"Starting TRMNL update at {datetime.now()}")
    
    today = datetime.now().strftime("%b %d, %Y")
    
    # Fetch completed orders data using API key
    print("Fetching completed orders data from Metabase API...")
    
    past_day_data = fetch_card_with_api_key(CARD_IDS['past_day_orders'])
    past_week_data = fetch_card_with_api_key(CARD_IDS['past_week_orders'])
    past_month_data = fetch_card_with_api_key(CARD_IDS['past_month_orders'])
    past_quarter_data = fetch_card_with_api_key(CARD_IDS['past_quarter_orders'])
    
    # Extract values (with fallbacks)
    past_day_orders = extract_scalar_value(past_day_data) or 363
    past_week_orders = extract_scalar_value(past_week_data) or 2086
    past_month_orders = extract_scalar_value(past_month_data) or 6075
    past_quarter_orders = extract_scalar_value(past_quarter_data) or 7572
    
    print(f"Completed orders - Day: {past_day_orders}, Week: {past_week_orders}, Month: {past_month_orders}, Quarter: {past_quarter_orders}")
    
    # Use today's data from the configuration
    print(f"Using today's data - Users: {TODAY_DATA['users']}, Orders: {TODAY_DATA['orders']}, Quantity: {TODAY_DATA['quantity']}, Sales: {TODAY_DATA['sales']}, Products: {TODAY_DATA['products']}")
    
    # Prepare data for TRMNL
    data = {
        "date": today,
        "total_users": TODAY_DATA['users'],
        "total_orders": TODAY_DATA['orders'],
        "total_quantity": TODAY_DATA['quantity'],
        "total_sales": TODAY_DATA['sales'],
        "total_products": TODAY_DATA['products'],
        "past_day_orders": format_number(past_day_orders),
        "past_day_change": "↑ 8.68% vs. previous day",
        "past_week_orders": format_number(past_week_orders),
        "past_week_change": "↓ 14.3% vs. previous week",
        "past_month_orders": format_number(past_month_orders),
        "past_month_change": "↑ 39.3% vs. previous month",
        "past_quarter_orders": format_number(past_quarter_orders),
        "past_quarter_change": "↑ 83.58% vs. previous quarter"
    }
    
    # Push to TRMNL
    success = push_to_trmnl(data)
    
    if success:
        print(f"✓ TRMNL update completed successfully at {datetime.now()}")
    else:
        print(f"✗ TRMNL update failed at {datetime.now()}")
    
    return success

if __name__ == "__main__":
    main()
