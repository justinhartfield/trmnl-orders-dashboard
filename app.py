#!/usr/bin/env python3
"""
TRMNL Orders Dashboard Plugin
Displays order metrics from Metabase API
"""

import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Metabase configuration
METABASE_URL = os.environ.get('METABASE_URL', 'https://bi.weed.de')
METABASE_API_KEY = os.environ.get('METABASE_API_KEY', 'mb_c1iFO7gACiVcI8UcWMT+/cJSaYspkgJc6/5/5RCw/oM=')

# Metabase card IDs for order metrics
TOTAL_ORDERS_CARD_ID = 146
COMPLETED_ORDERS_CARD_ID = 907
ORDER_AVERAGE_CARD_ID = 939


def execute_metabase_card(card_id, row_limit=10):
    """Execute a Metabase card and return the results using REST API"""
    try:
        url = f"{METABASE_URL}/api/card/{card_id}/query/json"
        headers = {
            'X-Metabase-Session': METABASE_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Make the request
        response = requests.post(url, headers=headers, json={}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Limit rows if needed
            if isinstance(data, list) and len(data) > row_limit:
                data = data[:row_limit]
            return {'success': True, 'data': data}
        else:
            print(f"Error from Metabase API: {response.status_code} - {response.text}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"Error executing Metabase card {card_id}: {e}")
        return {'success': False, 'error': str(e)}


def format_number(num):
    """Format number with thousand separators"""
    if num is None:
        return "N/A"
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


def generate_week_rows(recent_orders):
    """Generate HTML for week rows"""
    rows = []
    for week in recent_orders:
        try:
            week_date = datetime.fromisoformat(week['week'].replace('Z', '+00:00')).strftime('%b %d')
        except:
            week_date = "Recent"
        row = f'''
                        <div class="week-row">
                            <span class="week-label">Week {week_date}</span>
                            <span class="week-stat">{format_number(week['orders'])} orders | EUR {format_number(week['sales'])} | {format_number(week['quantity'])} items</span>
                        </div>'''
        rows.append(row)
    return ''.join(rows)


def generate_markup():
    """Generate the HTML markup for the TRMNL display"""
    
    # Fetch data from Metabase
    total_orders_data = execute_metabase_card(TOTAL_ORDERS_CARD_ID, 1)
    completed_orders_data = execute_metabase_card(COMPLETED_ORDERS_CARD_ID, 5)
    order_average_data = execute_metabase_card(ORDER_AVERAGE_CARD_ID, 1)
    
    # Extract metrics with error handling
    total_orders = 0
    if total_orders_data and total_orders_data.get('success'):
        data = total_orders_data.get('data', [])
        if isinstance(data, list) and len(data) > 0:
            total_orders = data[0].get('Number of orders', 0)
        elif isinstance(data, dict):
            total_orders = data.get('Number of orders', 0)
    
    # Get recent week data
    recent_orders = []
    if completed_orders_data and completed_orders_data.get('success'):
        data = completed_orders_data.get('data', [])
        if isinstance(data, list):
            for item in data[:3]:  # Get last 3 weeks
                recent_orders.append({
                    'week': item.get('OrderDate: Week', ''),
                    'orders': item.get('Number of orders', 0),
                    'sales': item.get('Total sales', 0),
                    'quantity': item.get('Total quantity', 0)
                })
    
    # Get averages
    avg_quantity = 0
    avg_value = 0
    avg_products = 0
    if order_average_data and order_average_data.get('success'):
        data = order_average_data.get('data', [])
        if isinstance(data, list) and len(data) > 0:
            avg_quantity = data[0].get('Quantity', 0)
            avg_value = data[0].get('Value (€)', 0)
            avg_products = data[0].get('Products', 0)
        elif isinstance(data, dict):
            avg_quantity = data.get('Quantity', 0)
            avg_value = data.get('Value (€)', 0)
            avg_products = data.get('Products', 0)
    
    # Generate week rows HTML
    week_rows_html = generate_week_rows(recent_orders) if recent_orders else '<div class="week-row"><span class="week-label">No recent data</span></div>'
    
    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Generate HTML markup
    markup_full = f'''<div class="view view--full">
    <div class="layout">
        <div class="columns">
            <div class="column">
                <div class="markdown gap--large">
                    <span class="title">Orders Dashboard</span>
                    
                    <div class="content-element">
                        <div class="stat-row">
                            <span class="stat-label">Total Orders</span>
                            <span class="stat-value">{format_number(total_orders)}</span>
                        </div>
                    </div>
                    
                    <span class="label label--underline mt-4">Recent Activity (Last 3 Weeks)</span>
                    
                    <div class="content-element">{week_rows_html}
                    </div>
                    
                    <span class="label label--underline mt-4">Order Averages</span>
                    
                    <div class="content-element">
                        <div class="avg-row">
                            <span class="avg-label">Avg Quantity</span>
                            <span class="avg-value">{format_number(avg_quantity)}</span>
                        </div>
                        <div class="avg-row">
                            <span class="avg-label">Avg Value</span>
                            <span class="avg-value">EUR {format_number(avg_value)}</span>
                        </div>
                        <div class="avg-row">
                            <span class="avg-label">Avg Products</span>
                            <span class="avg-value">{format_number(avg_products)}</span>
                        </div>
                    </div>
                    
                    <span class="label mt-4">Updated: {current_time}</span>
                </div>
            </div>
        </div>
    </div>
</div>'''
    
    # Generate half vertical layout
    markup_half_vertical = f'''<div class="view view--half_vertical">
    <div class="layout">
        <div class="columns">
            <div class="column">
                <div class="markdown">
                    <span class="title">Orders</span>
                    <div class="content-element">
                        <div class="stat-row">
                            <span class="stat-label">Total</span>
                            <span class="stat-value">{format_number(total_orders)}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Avg Value</span>
                            <span class="stat-value">EUR {format_number(avg_value)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>'''
    
    # Generate half horizontal layout
    markup_half_horizontal = f'''<div class="view view--half_horizontal">
    <div class="layout">
        <div class="columns">
            <div class="column">
                <div class="markdown">
                    <span class="title">Orders Dashboard</span>
                    <div class="content-element">
                        <span class="stat-value">{format_number(total_orders)}</span>
                        <span class="stat-label">Total Orders</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>'''
    
    # Generate quadrant layout
    markup_quadrant = f'''<div class="view view--quadrant">
    <div class="layout">
        <div class="columns">
            <div class="column">
                <div class="markdown">
                    <span class="title">Orders</span>
                    <div class="content-element">
                        <span class="stat-value">{format_number(total_orders)}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>'''
    
    return {
        'markup': markup_full,
        'markup_half_vertical': markup_half_vertical,
        'markup_half_horizontal': markup_half_horizontal,
        'markup_quadrant': markup_quadrant,
        'shared': ''
    }


@app.route('/plugin/markup', methods=['GET', 'POST'])
def plugin_markup():
    """Handle TRMNL plugin markup requests"""
    try:
        # Get request data (support both GET and POST)
        if request.method == 'POST':
            user_uuid = request.form.get('user_uuid')
            trmnl_data = request.form.get('trmnl')
        else:
            user_uuid = request.args.get('user_uuid', 'unknown')
            trmnl_data = request.args.get('trmnl')
        
        # Log the request
        print(f"Plugin markup request from user: {user_uuid}")
        if trmnl_data:
            print(f"TRMNL data: {trmnl_data}")
        
        # Generate and return markup
        markup = generate_markup()
        return jsonify(markup)
    
    except Exception as e:
        print(f"Error generating markup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'markup': f'<div class="view view--full"><div class="layout"><div class="columns"><div class="column"><div class="markdown"><span class="title">Error</span><div class="content">Failed to load orders data: {str(e)}</div></div></div></div></div></div>',
            'markup_half_vertical': '<div class="view view--half_vertical"><div class="layout"><div class="columns"><div class="column"><div class="markdown"><span class="title">Error</span></div></div></div></div></div>',
            'markup_half_horizontal': '<div class="view view--half_horizontal"><div class="layout"><div class="columns"><div class="column"><div class="markdown"><span class="title">Error</span></div></div></div></div></div>',
            'markup_quadrant': '<div class="view view--quadrant"><div class="layout"><div class="columns"><div class="column"><div class="markdown"><span class="title">Error</span></div></div></div></div></div>',
            'shared': ''
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with info"""
    return jsonify({
        'name': 'TRMNL Orders Dashboard',
        'version': '1.0.0',
        'endpoints': {
            'markup': '/plugin/markup',
            'health': '/health'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
