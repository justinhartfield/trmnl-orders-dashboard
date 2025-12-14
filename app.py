import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from string import Template

from stats.metabase import (
    OrdersDashboardStats,
    StatsCache,
    fetch_orders_dashboard_stats,
    probe_card_with_api_key,
    probe_public_card,
)

app = Flask(__name__)

_CACHE = StatsCache(
    ttl_seconds=int(os.getenv("STATS_CACHE_TTL_SECONDS", "900")),
    persist_path=os.getenv("STATS_CACHE_PATH", os.path.join(".cache", "trmnl_stats.json")),
)


def _get_stats() -> OrdersDashboardStats:
    cached = _CACHE.get()
    if cached:
        return cached

    stats = fetch_orders_dashboard_stats()
    _CACHE.set(stats)
    return stats

_MARKUP_TEMPLATE = Template(
    """<div class="view $view_class">
  <div class="layout">
    <div class="columns">
      <div class="column">
        <div class="markdown gap--large">
          <span class="title">Orders Dashboard</span>

          <span class="label label--underline">Today</span>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Users</span>
                <span class="value">$total_users</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Orders</span>
                <span class="value">$total_orders</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Quantity</span>
                <span class="value">$total_quantity</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Sales</span>
                <span class="value">$total_sales</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Products</span>
                <span class="value">$total_products</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="column">
        <div class="markdown gap--large">
          <span class="title">Completed Orders</span>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Past Day</span>
                <span class="value">$past_day_orders</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Past Week</span>
                <span class="value">$past_week_orders</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Past Month</span>
                <span class="value">$past_month_orders</span>
              </div>
            </div>
          </div>

          <div class="item">
            <div class="content">
              <div class="flex gap--small">
                <span class="label">Past Quarter</span>
                <span class="value">$past_quarter_orders</span>
              </div>
            </div>
          </div>

          <span class="label label--small">Updated: $updated_local</span>
        </div>
      </div>
    </div>
  </div>

  <div class="title_bar">
    <span class="title">Orders Dashboard</span>
    <span class="instance">weed.de / Metabase</span>
  </div>
</div>"""
)


def generate_markup(stats: OrdersDashboardStats, view_class: str) -> str:
    updated_local = datetime.now().strftime("%Y-%m-%d %H:%M")
    return _MARKUP_TEMPLATE.safe_substitute(
        {
            "view_class": view_class,
            "total_users": stats.total_users,
            "total_orders": stats.total_orders,
            "total_quantity": stats.total_quantity,
            "total_sales": stats.total_sales,
            "total_products": stats.total_products,
            "past_day_orders": stats.past_day_orders,
            "past_week_orders": stats.past_week_orders,
            "past_month_orders": stats.past_month_orders,
            "past_quarter_orders": stats.past_quarter_orders,
            "updated_local": updated_local,
        }
    )

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/metrics/json', methods=['GET'])
def metrics_json():
    """Debug endpoint to view current computed metrics."""
    stats = _get_stats()
    # Do not expose secrets; just confirm whether the env var exists.
    d = dict(stats.__dict__)
    d["metabase_api_key_present"] = bool(os.getenv("METABASE_API_KEY", "").strip())
    d["metabase_url"] = os.getenv("METABASE_URL", "")
    if request.args.get("debug") == "1":
        base_url = (os.getenv("METABASE_URL", "") or "https://bi.weed.de").rstrip("/")
        api_key = os.getenv("METABASE_API_KEY", "").strip()
        d["metabase_probe"] = {
            "api_key_cards": (
                {
                    "938": probe_card_with_api_key(base_url, 938, api_key),
                    "859": probe_card_with_api_key(base_url, 859, api_key),
                    "860": probe_card_with_api_key(base_url, 860, api_key),
                    "861": probe_card_with_api_key(base_url, 861, api_key),
                    "862": probe_card_with_api_key(base_url, 862, api_key),
                }
                if api_key
                else {"error": "METABASE_API_KEY not set"}
            ),
            "public_cards": {
                "859": probe_public_card(base_url, 859),
                "860": probe_public_card(base_url, 860),
                "861": probe_public_card(base_url, 861),
                "862": probe_public_card(base_url, 862),
                "1275": probe_public_card(base_url, 1275),
            },
        }
    return jsonify(d)

@app.route('/plugin/markup', methods=['GET', 'POST'])
def plugin_markup():
    """Main plugin endpoint that returns TRMNL markup"""

    stats = _get_stats()
    # TRMNL expects layout-specific keys. We render the same KPI content for each view.
    # We ALSO include merge_variables for compatibility with setups where TRMNL stores
    # the template server-side and only uses merge_variables from polling/webhook.
    merge_vars = {
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

    # TRMNL polling implementations vary by plugin type/version:
    # - Some use `merge_variables`
    # - Some use `variables`
    # - Some treat top-level JSON fields as variables
    # We provide all three for maximum compatibility.
    return jsonify(
        {
            "markup": generate_markup(stats, "view--full"),
            "markup_half_vertical": generate_markup(stats, "view--half_vertical"),
            "markup_half_horizontal": generate_markup(stats, "view--half_horizontal"),
            "markup_quadrant": generate_markup(stats, "view--quadrant"),
            "shared": "",
            "status": 200,
            "merge_variables": merge_vars,
            "variables": merge_vars,
            **merge_vars,
        }
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
