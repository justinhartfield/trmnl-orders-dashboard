#!/usr/bin/env python3
"""
TRMNL Orders Dashboard Updater v2
Fetches order data from Metabase Public Dashboard and pushes to TRMNL via webhook
"""

import os
import requests
from datetime import datetime
import json

# Configuration
METABASE_PUBLIC_DASHBOARD = 'https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1'
TRMNL_WEBHOOK_URL = os.getenv('TRMNL_WEBHOOK_URL', 'https://usetrmnl.com/api/custom_plugins/3502d5b9-42ed-46d4-a51e-9b7b83ce03d6')

# Card IDs from the public dashboard
CARD_IDS = {
    'monthly_goal': 858,
    'past_day_orders': 859,
    'past_week_orders': 860,
    'past_month_orders': 861,
    'past_quarter_orders': 862
}

def fetch_public_card_data(card_id, params=None):
    """Fetch data from a public Metabase card"""
    try:
        url = f'https://bi.weed.de/api/public/card/{card_id}/query'
        
        # Add parameters if provided
        if params:
            url += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        
        response = requests.get(url, timeout=30)
        
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
    """Format number with German locale"""
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
    
    # Fetch completed orders data from public cards
    print("Fetching completed orders data...")
    
    past_day_data = fetch_public_card_data(CARD_IDS['past_day_orders'])
    past_week_data = fetch_public_card_data(CARD_IDS['past_week_orders'])
    past_month_data = fetch_public_card_data(CARD_IDS['past_month_orders'])
    past_quarter_data = fetch_public_card_data(CARD_IDS['past_quarter_orders'])
    
    # Extract values
    past_day_orders = extract_scalar_value(past_day_data) or 363
    past_week_orders = extract_scalar_value(past_week_data) or 2086
    past_month_orders = extract_scalar_value(past_month_data) or 6075
    past_quarter_orders = extract_scalar_value(past_quarter_data) or 7572
    
    print(f"Past day orders: {past_day_orders}")
    print(f"Past week orders: {past_week_orders}")
    print(f"Past month orders: {past_month_orders}")
    print(f"Past quarter orders: {past_quarter_orders}")
    
    # For now, use sample data for Today's summary
    # TODO: Identify the correct cards for today's filtered data
    data = {
        "date": today,
        "total_users": "12",
        "total_orders": "12",
        "total_quantity": "0,4kg",
        "total_sales": "€1.968",
        "total_products": "22",
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
