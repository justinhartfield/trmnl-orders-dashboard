import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from string import Template

from stats.metabase import OrdersDashboardStats, StatsCache, fetch_orders_dashboard_stats

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
    """<div class="view view--full">
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


def generate_markup(stats: OrdersDashboardStats) -> str:
    updated_local = datetime.now().strftime("%Y-%m-%d %H:%M")
    return _MARKUP_TEMPLATE.safe_substitute(
        {
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
    return jsonify(stats.__dict__)

@app.route('/plugin/markup', methods=['GET', 'POST'])
def plugin_markup():
    """Main plugin endpoint that returns TRMNL markup"""

    stats = _get_stats()
    markup = generate_markup(stats)

    # Even though the markup is fully server-rendered, we also include merge_variables
    # for compatibility with TRMNL and easier troubleshooting.
    return jsonify(
        {
            "markup": markup,
            "merge_variables": {
                "date": datetime.now().strftime("%b %d, %Y"),
                "total_users": stats.total_users,
                "total_orders": stats.total_orders,
                "total_quantity": stats.total_quantity,
                "total_sales": stats.total_sales,
                "total_products": stats.total_products,
                "past_day_orders": stats.past_day_orders,
                "past_week_orders": stats.past_week_orders,
                "past_month_orders": stats.past_month_orders,
                "past_quarter_orders": stats.past_quarter_orders,
                "as_of_iso": stats.as_of_iso,
                "source": stats.source,
            },
        }
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
