import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Metabase configuration
METABASE_URL = os.getenv('METABASE_URL', 'https://bi.weed.de')
METABASE_API_KEY = os.getenv('METABASE_API_KEY', '')

def fetch_metabase_data():
    """Fetch order data from Metabase API"""
    headers = {
        'X-API-KEY': METABASE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        # Fetch total orders (card ID: 1)
        response = requests.get(
            f'{METABASE_URL}/api/card/1/query',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            total_orders = 0
            
            # Extract total orders from response
            if 'data' in data and 'rows' in data['data']:
                rows = data['data']['rows']
                if rows and len(rows) > 0:
                    total_orders = rows[0][0] if len(rows[0]) > 0 else 0
            
            return {
                'total_orders': total_orders,
                'status': 'success'
            }
        else:
            return {
                'total_orders': 0,
                'status': 'error',
                'message': f'API returned status {response.status_code}'
            }
            
    except Exception as e:
        return {
            'total_orders': 0,
            'status': 'error',
            'message': str(e)
        }

def generate_markup(data):
    """Generate TRMNL markup using proper framework classes"""
    
    total_orders = data.get('total_orders', 0)
    status = data.get('status', 'unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Build markup using proper TRMNL components
    markup = f'''<div class="view view--full">
    <div class="layout">
        <div class="columns">
            <div class="column">
                
                <span class="title">Orders Dashboard</span>
                
                <div class="item">
                    <div class="content">
                        <div class="flex gap--small">
                            <span class="label">Total Orders</span>
                            <span class="value">{total_orders}</span>
                        </div>
                    </div>
                </div>
                
                <span class="label label--underline">Status</span>
                
                <div class="item">
                    <div class="content">
                        <div class="flex gap--small">
                            <span class="label label--small">Connection</span>
                            <span class="description">{status}</span>
                        </div>
                    </div>
                </div>
                
                <div class="item">
                    <div class="content">
                        <div class="flex gap--small">
                            <span class="label label--small">Last Updated</span>
                            <span class="description">{timestamp}</span>
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
    
    <div class="title_bar">
        <span class="title">Orders Dashboard</span>
        <span class="instance">Metabase</span>
    </div>
</div>'''
    
    return markup

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/plugin/markup', methods=['GET', 'POST'])
def plugin_markup():
    """Main plugin endpoint that returns TRMNL markup"""
    
    # Fetch data from Metabase
    data = fetch_metabase_data()
    
    # Generate markup
    markup = generate_markup(data)
    
    # Return in TRMNL format
    response = {
        'markup': markup,
        'merge_variables': {
            'total_orders': data.get('total_orders', 0),
            'status': data.get('status', 'unknown')
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
