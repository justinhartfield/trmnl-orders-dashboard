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

1. **TRMNL Plugin** (Webhook strategy)
   - Plugin UUID: `3502d5b9-42ed-46d4-a51e-9b7b83ce03d6`
   - Receives data via webhook POST requests
   - Displays data using custom HTML markup with TRMNL framework classes

2. **Update Script** (`update_trmnl_v2.py`)
   - Fetches data from Metabase public dashboard
   - Formats data for TRMNL display
   - Pushes data to TRMNL webhook endpoint
   - Runs automatically every 15 minutes

3. **Metabase Integration**
   - Public Dashboard: https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1
   - Fetches completed orders statistics
   - No authentication required for public dashboard

### Automated Scheduling

The update script runs every 15 minutes (900 seconds) using the Manus scheduling system:
- **Task Name**: TRMNL Orders Dashboard Update
- **Interval**: 900 seconds (15 minutes)
- **Script Location**: `/home/ubuntu/trmnl-orders-dashboard/update_trmnl_v2.py`

## Manual Updates

To manually trigger an update, run:

```bash
cd /home/ubuntu/trmnl-orders-dashboard
python3 update_trmnl_v2.py
```

Expected output:
```
Starting TRMNL update at 2025-12-13 07:26:48.977186
Fetching completed orders data...
Past day orders: 363
Past week orders: 2086
Past month orders: 6075
Past quarter orders: 7572
✓ Successfully pushed data to TRMNL
✓ TRMNL update completed successfully at 2025-12-13 07:26:50.292493
```

## TRMNL Plugin Configuration

### Strategy
**Webhook** - Data is pushed to TRMNL via API

### Webhook URL
```
https://usetrmnl.com/api/custom_plugins/3502d5b9-42ed-46d4-a51e-9b7b83ce03d6
```

### Markup Template
The complete HTML markup is stored in `trmnl_with_logo.html`. It includes:
- Two-column layout
- TRMNL framework CSS classes
- Weed.de logo in the title bar
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

1. **Check the scheduled task status**
   - The task should be running every 15 minutes
   - Check Manus task logs for errors

2. **Run the script manually**
   ```bash
   python3 /home/ubuntu/trmnl-orders-dashboard/update_trmnl_v2.py
   ```
   - Look for success message: "✓ TRMNL update completed successfully"
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
2. Verify the script can fetch data (check error messages)
3. The script uses fallback values if Metabase is unavailable

## Future Improvements

### Real-Time Today's Data

Currently, the "Today's Orders" section uses sample data. To fetch real-time today's data:

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

- `update_trmnl_v2.py` - Main update script
- `trmnl_with_logo.html` - TRMNL markup template with logo
- `AUTOMATION_GUIDE.md` - This documentation
- `README.md` - Project overview

## Support

For issues or questions:
- Check TRMNL logs: https://usetrmnl.com/logs
- Review Metabase dashboard: https://bi.weed.de/public/dashboard/a529771c-34aa-4f1d-b6e3-6130f99f51c1
- GitHub repository: https://github.com/justinhartfield/trmnl-orders-dashboard
