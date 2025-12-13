# TRMNL Plugin Setup Guide

## Public URL
Your plugin is now accessible at:
**https://5000-ihneb49dd2u30f7n3t8u7-98d5b699.manusvm.computer**

## Form Field Values

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

5. **Temporary URL**: Note that this URL is temporary and tied to this sandbox session. For production use, you'll need to deploy the app to a permanent server (Heroku, Railway, Render, etc.)

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
