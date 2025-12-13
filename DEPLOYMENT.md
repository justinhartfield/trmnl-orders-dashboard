# Deployment Guide for TRMNL Orders Dashboard

## Quick Start (For Production)

The current setup is running on a temporary sandbox URL. For production use, you'll need to deploy to a permanent hosting service.

## Recommended Deployment Options

### Option 1: Railway (Easiest)

1. Create account at [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select this repository
4. Railway will auto-detect the Flask app
5. Add environment variable: `PORT=5000`
6. Deploy and get your public URL

### Option 2: Render

1. Create account at [Render](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 app.py`
   - **Environment**: Python 3
5. Deploy and get your public URL

### Option 3: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python3 app.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 4: Google Cloud Run (Serverless)

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python3", "app.py"]
   ```
2. Deploy:
   ```bash
   gcloud run deploy trmnl-orders --source .
   ```

## Important: Metabase MCP Access

**Critical Requirement**: The deployed app needs access to the Metabase MCP server via `manus-mcp-cli`.

### Current Limitation
The app currently uses `manus-mcp-cli` which is only available in the Manus sandbox environment. For production deployment, you have two options:

### Solution 1: Direct Metabase API (Recommended)
Modify the app to use Metabase's REST API directly instead of MCP:

1. Get your Metabase API credentials
2. Replace `execute_metabase_card()` function to use direct HTTP requests
3. Example:
   ```python
   import requests
   
   def execute_metabase_card(card_id, row_limit=10):
       url = f"https://your-metabase.com/api/card/{card_id}/query"
       headers = {"X-Metabase-Session": "YOUR_SESSION_TOKEN"}
       response = requests.post(url, headers=headers)
       return response.json()
   ```

### Solution 2: Webhook Strategy
Instead of polling Metabase, have Metabase push data to your TRMNL plugin:

1. Change TRMNL strategy from "Polling" to "Webhook"
2. Set up Metabase to send data to your endpoint
3. Store the data and serve it when TRMNL requests it

## Environment Variables

For production deployment, set these environment variables:

```bash
PORT=5000
METABASE_URL=https://your-metabase-instance.com
METABASE_API_KEY=your-api-key
```

## Files to Deploy

Make sure these files are in your repository:
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `README.md` - Documentation
- `Procfile` (for Heroku)
- `Dockerfile` (for containerized deployments)

## Post-Deployment

After deploying, you'll get a permanent URL like:
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Heroku: `https://your-app.herokuapp.com`

Use this URL in the TRMNL plugin configuration:
```
https://your-app.railway.app/plugin/markup
```

## Monitoring

Monitor your app's health using the health endpoint:
```bash
curl https://your-app.railway.app/health
```

## Troubleshooting

### App Won't Start
- Check logs for Python errors
- Verify all dependencies are in `requirements.txt`
- Ensure PORT environment variable is set

### No Data Showing
- Verify Metabase API credentials
- Check app logs for Metabase connection errors
- Test Metabase API endpoints directly

### TRMNL Not Updating
- Verify the polling URL is correct
- Check TRMNL refresh interval settings
- Review TRMNL plugin logs for errors
