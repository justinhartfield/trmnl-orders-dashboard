#!/usr/bin/env python3
"""
Webhook push job for TRMNL Orders Dashboard.

Runs as a cron/scheduled job every 15 minutes to push merge_variables to TRMNL.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict

import requests

from stats.metabase import fetch_orders_dashboard_stats


def build_merge_variables() -> Dict[str, str]:
    stats = fetch_orders_dashboard_stats()
    return {
        "date": datetime.now().strftime("%b %d, %Y"),
        "total_users": stats.total_users,
        "total_orders": stats.total_orders,
        "total_quantity": stats.total_quantity,
        "total_sales": stats.total_sales,
        "total_products": stats.total_products,
        "past_day_orders": stats.past_day_orders,
        "past_day_change": "",
        "past_week_orders": stats.past_week_orders,
        "past_week_change": "",
        "past_month_orders": stats.past_month_orders,
        "past_month_change": "",
        "past_quarter_orders": stats.past_quarter_orders,
        "past_quarter_change": "",
        "as_of_iso": stats.as_of_iso,
        "source": stats.source,
    }


def push_to_trmnl(webhook_url: str, merge_variables: Dict[str, str]) -> None:
    r = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        json={"merge_variables": merge_variables},
        timeout=15,
    )
    if r.status_code != 200:
        raise RuntimeError(f"TRMNL webhook failed: HTTP {r.status_code}: {r.text}")


def main() -> int:
    webhook_url = os.getenv("TRMNL_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("Missing TRMNL_WEBHOOK_URL env var", file=sys.stderr)
        return 2

    merge_variables = build_merge_variables()
    push_to_trmnl(webhook_url, merge_variables)
    print(f"✓ pushed TRMNL merge_variables at {datetime.now().isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


