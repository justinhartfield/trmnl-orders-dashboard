# TRMNL Plugin Setup Guide

## Public URL
Your plugin is now accessible at:
**https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer**

## Form Field Values

### Strategy (Recommended: Polling + Webhook fallback)
You can run **both** strategies for resilience:
- **Polling**: TRMNL pulls the latest markup from your server.
- **Webhook**: a scheduled job pushes merge variables to TRMNL every 15 minutes.

If you only want one:
- Choose **Polling** for the simplest setup (no scheduler required).
- Choose **Webhook** for push-based updates (requires a scheduler/cron).

## Polling setup (TRMNL pulls)

### Strategy
**Select:** `Polling`

### Polling URL(s)
```
https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer/plugin/markup
```

### Polling Verb
**Select:** `GET` (or keep as default)

Note: The app currently supports POST, but TRMNL typically uses GET for polling. You may need to leave this as GET and the app will handle it.

### Polling Headers
Leave empty (optional field)

### Polling Body
Leave empty (optional field)

### Form Fields
Leave empty (optional field) - This is for user configuration options

### Remove bleed margin?
**Select:** `No` (default)

### Enable Dark Mode?
**Select:** `No` (default)

## Important Notes

1. **Plugin Name**: You can name it "Orders Dashboard" or "Metabase Orders"

2. **Strategy**: We're using "Polling" which means TRMNL will periodically fetch data from your server

3. **Response Format**: The app returns JSON with HTML markup for different layouts:
   - `markup` - Full screen layout
   - `markup_half_vertical` - Half screen vertical layout
   - `markup_half_horizontal` - Half screen horizontal layout
   - `markup_quadrant` - Quadrant layout

4. **Data Refresh**: TRMNL will poll the endpoint based on the refresh interval you set in your TRMNL device settings

   - Set the device refresh interval to **15 minutes**.
   - The server caches stats for 15 minutes by default to avoid overloading Metabase.

5. **Temporary URL**: Note that this URL is temporary and tied to this sandbox session. For production use, you'll need to deploy the app to a permanent server (Heroku, Railway, Render, etc.)

## Webhook fallback setup (Scheduler pushes)

1. In TRMNL, create (or use) a **Custom Plugin** with **Webhook** strategy.
2. Paste the markup from `trmnl_with_logo.html` into the plugin template.
3. Run the job every 15 minutes:

   - Command: `python3 push_trmnl.py`
   - Env vars:
     - `TRMNL_WEBHOOK_URL` (your TRMNL custom plugin webhook endpoint)
     - `METABASE_API_KEY` (required for real metrics from Metabase card IDs)

4. Use any scheduler/cron to run it every 15 minutes (Railway cron, Render cron, server cron, etc.).

## Testing the Endpoint

You can test the endpoint with:
```bash
curl https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer/health
```

Or test the markup endpoint:
```bash
curl -X POST https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer/plugin/markup \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_uuid=test"
```

You can also inspect the computed numbers directly:
```bash
curl https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer/metrics/json
```
