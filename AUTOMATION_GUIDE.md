# TRMNL Orders Dashboard - Automation Guide

## Overview

Your TRMNL Orders Dashboard is now set up with automated updates every 15 minutes. The dashboard displays:

**Left Column - Today's Orders:**
- Total Users
- Total Orders
- Total Quantity
- Total Sales (€)
- Total Products

**Right Column - Completed Orders:**
- Past Day orders with % change
- Past Week orders with % change
- Past Month orders with % change
- Past Quarter orders with % change

## How It Works

### Architecture

1. **TRMNL Plugin** (Polling + optional Webhook fallback)
   - Plugin UUID: `3502d5b9-42ed-46d4-a51e-9b7b83ce03d6`
   - **Polling**: TRMNL calls your server for the rendered markup (`/plugin/markup`)
   - **Webhook (optional)**: a scheduled job pushes `merge_variables` to TRMNL
   - Displays data using custom HTML markup with TRMNL framework classes

2. **Polling Server** (`app.py`)
   - Fetches/normalizes metrics from Metabase
   - Caches for 15 minutes (TTL) with last-known-good fallback
   - Serves TRMNL markup at `/plugin/markup`

3. **Webhook Push Job** (`push_trmnl.py`) (optional fallback)
   - Fetches the same metrics source-of-truth
   - Pushes merge variables to TRMNL webhook endpoint
   - Runs every 15 minutes via cron/scheduler

4. **Metabase Integration**
   - Public Dashboard: https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1
   - Completed orders (past day/week/month/quarter) use card IDs (859–862) and require `METABASE_API_KEY`.
   - “Today” KPIs prefer a summary card (938) requiring `METABASE_API_KEY`.

### Automated Scheduling

You have two ways to get 15-minute refresh:

1) **Polling only (recommended)**: set TRMNL device refresh to **15 minutes**.
2) **Webhook fallback**: run `python3 push_trmnl.py` every **900 seconds** using any scheduler/cron.

## Manual Updates

To manually trigger a webhook push, run:

```bash
python3 push_trmnl.py
```

Expected output: `✓ pushed TRMNL merge_variables at ...`

## TRMNL Plugin Configuration

### Strategy
**Polling** (recommended) + optional **Webhook** fallback

### Polling URL
Use your deployed server’s URL:
```
https://<your-host>/plugin/markup
```

### Webhook URL (fallback)
```
https://usetrmnl.com/api/custom_plugins/3502d5b9-42ed-46d4-a51e-9b7b83ce03d6
```

### Markup Template
The complete HTML markup is stored in `trmnl_with_logo.html`. It includes:
- Two-column layout
- TRMNL framework CSS classes
- Merge variables for dynamic data

### Merge Variables

The script sends these variables to TRMNL:

```json
{
  "date": "Dec 13, 2025",
  "total_users": "12",
  "total_orders": "12",
  "total_quantity": "0,4kg",
  "total_sales": "€1.968",
  "total_products": "22",
  "past_day_orders": "363",
  "past_day_change": "↑ 8.68% vs. previous day",
  "past_week_orders": "2,086",
  "past_week_change": "↓ 14.3% vs. previous week",
  "past_month_orders": "6,075",
  "past_month_change": "↑ 39.3% vs. previous month",
  "past_quarter_orders": "7,571",
  "past_quarter_change": "↑ 83.58% vs. previous quarter"
}
```

## Troubleshooting

### Dashboard Not Updating

1. **If using Polling**
   - Confirm TRMNL device refresh is set to **15 minutes**
   - Visit `https://<your-host>/metrics/json` to confirm the server has fresh stats

2. **If using Webhook fallback**
   ```bash
   python3 push_trmnl.py
   ```
   - Look for success message: "✓ pushed TRMNL merge_variables"
   - Check for error messages

3. **Verify TRMNL webhook**
   - Test the webhook endpoint directly:
   ```bash
   curl -X POST https://usetrmnl.com/api/custom_plugins/3502d5b9-42ed-46d4-a51e-9b7b83ce03d6 \
     -H "Content-Type: application/json" \
     -d '{"merge_variables": {"date": "Test"}}'
   ```

### Metabase Connection Issues

If Metabase data isn't updating:
1. Check if the public dashboard is accessible: https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1
2. Verify your server can reach Metabase (check logs)
3. The server uses last-known-good cached values if Metabase is temporarily unavailable

## Future Improvements

### Real-Time Today's Data

The server fetches real-time “Today” KPIs primarily from a Metabase summary card (requires `METABASE_API_KEY`).
If that card is unavailable, it will fall back to other sources or last-known-good cache.

1. Identify the Metabase card IDs for today's filtered metrics
2. Update the script to fetch from those cards
3. Add date filtering to the API requests

### Additional Metrics

You can add more metrics by:
1. Finding the card ID in Metabase
2. Adding a fetch function in the script
3. Adding the merge variable to the data dictionary
4. Adding the display element in the TRMNL markup

## Files

- `app.py` - Polling server (TRMNL pulls markup)
- `push_trmnl.py` - Webhook push job (optional fallback)
- `trmnl_with_logo.html` - TRMNL markup template with logo
- `AUTOMATION_GUIDE.md` - This documentation
- `README.md` - Project overview

## Support

For issues or questions:
- Check TRMNL logs: https://usetrmnl.com/logs
- Review Metabase dashboard: https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1
- GitHub repository: https://github.com/justinhartfield/trmnl-orders-dashboard
