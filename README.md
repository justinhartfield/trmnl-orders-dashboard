# TRMNL Orders Dashboard Plugin

A TRMNL plugin that displays order metrics from Metabase API.

## Features

- **Total Orders**: Display the total number of orders
- **Recent Activity**: Show order statistics for the last 3 weeks
- **Order Averages**: Display average quantity, value, and products per order
- **Multiple Layouts**: Supports full screen, half vertical, half horizontal, and quadrant layouts

## Data Sources

The plugin fetches data from the following Metabase cards:

- **Card 146**: Total orders count
- **Card 907**: Completed orders by week (with sales and quantity)
- **Card 939**: Order averages (quantity, value, products)

## Requirements

- Python 3.11+
- Flask 3.0.0
- Access to Metabase MCP server
- `manus-mcp-cli` tool installed

## Installation

1. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Make sure the Metabase MCP server is configured and accessible via `manus-mcp-cli`

## Running the App

### Local Development

Run the Flask app locally:

```bash
python3 app.py
```

The app will start on `http://localhost:5000`

### Testing the Plugin

Test the plugin endpoint:

```bash
curl -X POST http://localhost:5000/plugin/markup \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_uuid=test-user"
```

### Health Check

Check if the app is running:

```bash
curl http://localhost:5000/health
```

## Deployment

### Using a Public URL

To use this plugin with TRMNL, you need to deploy it to a publicly accessible server. Options include:

1. **Cloud Platforms**: Deploy to Heroku, Railway, Render, or similar platforms
2. **VPS**: Deploy to a VPS with a domain name
3. **Serverless**: Deploy as a serverless function on AWS Lambda, Google Cloud Functions, etc.

### Environment Variables

- `PORT`: Port to run the Flask app (default: 5000)

## TRMNL Plugin Configuration

When creating the plugin in TRMNL:

1. **Name**: Orders Dashboard
2. **Description**: Display order metrics from Metabase
3. **Plugin Markup URL**: `https://your-server.com/plugin/markup`
4. **Installation URL**: (optional, for OAuth flow)
5. **Plugin Management URL**: (optional, for settings)

## Response Format

The plugin returns JSON with HTML markup for different layouts:

```json
{
  "markup": "<div class=\"view view--full\">...</div>",
  "markup_half_vertical": "<div class=\"view view--half_vertical\">...</div>",
  "markup_half_horizontal": "<div class=\"view view--half_horizontal\">...</div>",
  "markup_quadrant": "<div class=\"view view--quadrant\">...</div>",
  "shared": ""
}
```

## Customization

You can customize the plugin by:

- Modifying the Metabase card IDs in `app.py`
- Adjusting the HTML markup in the `generate_markup()` function
- Adding more metrics or data sources
- Customizing the layout and styling

## Troubleshooting

### Metabase Connection Issues

If the plugin fails to fetch data from Metabase:

1. Verify the Metabase MCP server is configured correctly
2. Check that the card IDs are valid and accessible
3. Ensure OAuth authentication is working

### Plugin Not Displaying

If the plugin doesn't display on TRMNL:

1. Check the server logs for errors
2. Verify the markup URL is publicly accessible
3. Test the endpoint with curl to ensure it returns valid JSON

## License

MIT License
