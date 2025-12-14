from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import requests


METABASE_BASE_URL_DEFAULT = "https://bi.weed.de"

# Public dashboard cards (no auth)
CARD_PAST_DAY_ORDERS = 859
CARD_PAST_WEEK_ORDERS = 860
CARD_PAST_MONTH_ORDERS = 861
CARD_PAST_QUARTER_ORDERS = 862

# Private (API key) “summary” card for Today KPIs (preferred)
CARD_TODAY_SUMMARY = 938

# Optional fallback card for today aggregation (may or may not be public in your instance)
CARD_TODAY_FALLBACK_PUBLIC = 1275


@dataclass(frozen=True)
class OrdersDashboardStats:
    # Meta
    as_of_iso: str
    source: str

    # Today
    total_users: str
    total_orders: str
    total_quantity: str
    total_sales: str
    total_products: str

    # Completed orders
    past_day_orders: str
    past_week_orders: str
    past_month_orders: str
    past_quarter_orders: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_int_de(num: Optional[Any]) -> str:
    """German thousands separator (.) for integers."""
    try:
        if num is None:
            return "0"
        if isinstance(num, str):
            # Keep already formatted strings (e.g. "1,8kg", "€9.916")
            return num
        return f"{int(num):,}".replace(",", ".")
    except Exception:
        return "0"


def _format_money_eur_de(amount: Optional[Any]) -> str:
    """Format EUR with German separators: €9.916,00 (but keep decimals if present)."""
    try:
        if amount is None:
            return "€0,00"
        if isinstance(amount, str) and amount.strip().startswith("€"):
            return amount
        value = float(amount)
        # thousands with '.' and decimals with ','
        s = f"{value:,.2f}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"€{s}"
    except Exception:
        return "€0,00"


def _format_kg_de(quantity_grams: Optional[Any]) -> str:
    """Convert grams to kg with German decimal separator, e.g. 1800g => 1,8kg."""
    try:
        if quantity_grams is None:
            return "0,0kg"
        if isinstance(quantity_grams, str) and quantity_grams.strip().endswith("kg"):
            return quantity_grams
        g = float(quantity_grams)
        kg = g / 1000.0
        s = f"{kg:.1f}".replace(".", ",")
        return f"{s}kg"
    except Exception:
        return "0,0kg"


def _extract_scalar_from_dataset(data: Optional[Dict[str, Any]]) -> Optional[Any]:
    """
    Extract first cell from Metabase dataset response:
    { data: { rows: [[x, ...], ...], ... } }
    """
    if not data or not isinstance(data, dict):
        return None
    d = data.get("data")
    if not isinstance(d, dict):
        return None
    rows = d.get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    first_row = rows[0]
    if not isinstance(first_row, list) or not first_row:
        return None
    return first_row[0]


def _dataset_first_row_as_mapping(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Try to convert Metabase dataset response first row into a name->value mapping using cols[].name.
    """
    if not data or not isinstance(data, dict):
        return {}
    d = data.get("data")
    if not isinstance(d, dict):
        return {}
    cols = d.get("cols")
    rows = d.get("rows")
    if not isinstance(cols, list) or not isinstance(rows, list) or not rows:
        return {}
    first_row = rows[0]
    if not isinstance(first_row, list):
        return {}
    mapping: Dict[str, Any] = {}
    for i, col in enumerate(cols):
        if not isinstance(col, dict):
            continue
        name = col.get("display_name") or col.get("name")
        if not isinstance(name, str) or not name:
            continue
        if i < len(first_row):
            mapping[name] = first_row[i]
    return mapping


def _find_value_ci(mapping: Dict[str, Any], *needles: str) -> Optional[Any]:
    """
    Find a value in mapping by matching any substring (case-insensitive) in the key.
    """
    lower = {str(k).lower(): v for k, v in mapping.items()}
    for needle in needles:
        n = needle.lower()
        for k, v in lower.items():
            if n in k:
                return v
    return None


def fetch_public_card_dataset(base_url: str, card_id: int, timeout_s: int = 30) -> Optional[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/public/card/{card_id}/query"
    try:
        r = requests.get(url, timeout=timeout_s)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def fetch_card_dataset_with_api_key(
    base_url: str,
    card_id: int,
    api_key: str,
    timeout_s: int = 30,
) -> Optional[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/card/{card_id}/query"
    try:
        r = requests.post(
            url,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={},
            timeout=timeout_s,
        )
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def probe_card_with_api_key(
    base_url: str,
    card_id: int,
    api_key: str,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """
    Lightweight diagnostic probe that returns only HTTP metadata (no data payload).
    Safe to expose in a debug endpoint.
    """
    url = f"{base_url.rstrip('/')}/api/card/{card_id}/query"
    try:
        r = requests.post(
            url,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={},
            timeout=timeout_s,
        )
        return {
            "url": url,
            "status_code": r.status_code,
            "ok": bool(200 <= r.status_code < 300),
            "content_type": r.headers.get("content-type", ""),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


def probe_public_card(
    base_url: str,
    card_id: int,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """
    Probe the public-card endpoint (some Metabase instances require tokenized IDs).
    Returns only HTTP metadata.
    """
    url = f"{base_url.rstrip('/')}/api/public/card/{card_id}/query"
    try:
        r = requests.get(url, timeout=timeout_s)
        return {
            "url": url,
            "status_code": r.status_code,
            "ok": bool(200 <= r.status_code < 300),
            "content_type": r.headers.get("content-type", ""),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


def _compute_today_from_summary_dataset(summary: Dict[str, Any]) -> Optional[Tuple[str, str, str, str, str]]:
    """
    Attempt to compute today KPIs from a summary dataset (card 938).
    Returns (users, orders, quantity, sales, products) as strings.
    """
    row_map = _dataset_first_row_as_mapping(summary)
    if not row_map:
        return None

    users = _find_value_ci(row_map, "users", "user")
    orders = _find_value_ci(row_map, "orders", "order")
    quantity = _find_value_ci(row_map, "quantity", "qty", "gram", "g ")
    sales = _find_value_ci(row_map, "sales", "revenue", "umsatz", "value")
    products = _find_value_ci(row_map, "products", "prod", "items")

    # Allow partial presence but require at least orders to avoid nonsense
    if orders is None:
        return None

    users_s = _format_int_de(users)
    orders_s = _format_int_de(orders)
    quantity_s = _format_kg_de(quantity)
    sales_s = _format_money_eur_de(sales)
    products_s = _format_int_de(products)
    return users_s, orders_s, quantity_s, sales_s, products_s


def _compute_today_from_public_fallback_dataset(ds: Dict[str, Any]) -> Optional[Tuple[str, str, str, str, str]]:
    """
    Fallback: if card 1275 is public, it may include rows by strain with columns like
    Orders / Quantity / Sales / Prod. We'll sum them.
    """
    if not ds or not isinstance(ds, dict):
        return None
    d = ds.get("data")
    if not isinstance(d, dict):
        return None
    rows = d.get("rows")
    cols = d.get("cols")
    if not isinstance(rows, list) or not isinstance(cols, list):
        return None

    # Build index by column name
    col_names = []
    for c in cols:
        if isinstance(c, dict):
            col_names.append((c.get("display_name") or c.get("name") or "").lower())
        else:
            col_names.append("")

    def idx_of(*needles: str) -> Optional[int]:
        for i, name in enumerate(col_names):
            for needle in needles:
                if needle.lower() in name:
                    return i
        return None

    i_orders = idx_of("orders", "order")
    i_qty = idx_of("quantity", "qty")
    i_sales = idx_of("sales", "revenue", "value")
    i_prod = idx_of("prod", "products", "items")

    if i_orders is None:
        return None

    total_orders = 0.0
    total_qty = 0.0
    total_sales = 0.0
    total_prod = 0.0
    for row in rows:
        if not isinstance(row, list):
            continue
        if i_orders is not None and i_orders < len(row) and row[i_orders] is not None:
            total_orders += float(row[i_orders])
        if i_qty is not None and i_qty < len(row) and row[i_qty] is not None:
            total_qty += float(row[i_qty])
        if i_sales is not None and i_sales < len(row) and row[i_sales] is not None:
            total_sales += float(row[i_sales])
        if i_prod is not None and i_prod < len(row) and row[i_prod] is not None:
            total_prod += float(row[i_prod])

    # Estimate users as 60% of orders (matches old v3 behavior) — better than blank.
    users_est = int(total_orders * 0.6)
    return (
        _format_int_de(users_est),
        _format_int_de(total_orders),
        _format_kg_de(total_qty),
        _format_money_eur_de(total_sales),
        _format_int_de(total_prod),
    )


class StatsCache:
    """
    15-minute TTL cache with last-known-good persistence to disk.
    """

    def __init__(self, ttl_seconds: int = 900, persist_path: Optional[str] = None):
        self.ttl_seconds = ttl_seconds
        self.persist_path = persist_path
        self._cached: Optional[OrdersDashboardStats] = None
        self._cached_at: float = 0.0

        # Best-effort load from disk
        if self.persist_path:
            self._cached = self._load_from_disk(self.persist_path)
            if self._cached:
                self._cached_at = time.time()

    def get(self) -> Optional[OrdersDashboardStats]:
        if self._cached and (time.time() - self._cached_at) <= self.ttl_seconds:
            return self._cached
        return None

    def set(self, stats: OrdersDashboardStats) -> None:
        self._cached = stats
        self._cached_at = time.time()
        if self.persist_path:
            self._save_to_disk(self.persist_path, stats)

    @staticmethod
    def _save_to_disk(path: str, stats: OrdersDashboardStats) -> None:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(stats.__dict__, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _load_from_disk(path: str) -> Optional[OrdersDashboardStats]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return None
            return OrdersDashboardStats(**raw)
        except Exception:
            return None


def fetch_orders_dashboard_stats(
    base_url: Optional[str] = None,
    metabase_api_key: Optional[str] = None,
) -> OrdersDashboardStats:
    """
    Fetch all KPIs needed for TRMNL.
    """
    b = (base_url or os.getenv("METABASE_URL") or METABASE_BASE_URL_DEFAULT).rstrip("/")
    api_key = metabase_api_key if metabase_api_key is not None else os.getenv("METABASE_API_KEY", "").strip()

    # Completed orders
    # NOTE: These cards are numeric IDs. In many Metabase setups, the "public card" API uses a token,
    # not numeric IDs, so we prefer the API-key path when available.
    if api_key:
        past_day = _extract_scalar_from_dataset(fetch_card_dataset_with_api_key(b, CARD_PAST_DAY_ORDERS, api_key))
        past_week = _extract_scalar_from_dataset(fetch_card_dataset_with_api_key(b, CARD_PAST_WEEK_ORDERS, api_key))
        past_month = _extract_scalar_from_dataset(fetch_card_dataset_with_api_key(b, CARD_PAST_MONTH_ORDERS, api_key))
        past_quarter = _extract_scalar_from_dataset(fetch_card_dataset_with_api_key(b, CARD_PAST_QUARTER_ORDERS, api_key))
    else:
        past_day = _extract_scalar_from_dataset(fetch_public_card_dataset(b, CARD_PAST_DAY_ORDERS))
        past_week = _extract_scalar_from_dataset(fetch_public_card_dataset(b, CARD_PAST_WEEK_ORDERS))
        past_month = _extract_scalar_from_dataset(fetch_public_card_dataset(b, CARD_PAST_MONTH_ORDERS))
        past_quarter = _extract_scalar_from_dataset(fetch_public_card_dataset(b, CARD_PAST_QUARTER_ORDERS))

    past_day_s = _format_int_de(past_day)
    past_week_s = _format_int_de(past_week)
    past_month_s = _format_int_de(past_month)
    past_quarter_s = _format_int_de(past_quarter)

    # Today KPIs (preferred: summary card w/ API key)
    today_source = "unknown"
    today_users = "0"
    today_orders = "0"
    today_qty = "0,0kg"
    today_sales = "€0,00"
    today_products = "0"

    if api_key:
        summary_ds = fetch_card_dataset_with_api_key(b, CARD_TODAY_SUMMARY, api_key)
        computed = _compute_today_from_summary_dataset(summary_ds) if summary_ds else None
        if computed:
            today_users, today_orders, today_qty, today_sales, today_products = computed
            today_source = f"card:{CARD_TODAY_SUMMARY}"

    # Fallback: public card 1275 aggregation (if accessible)
    if today_source == "unknown":
        fallback_ds = fetch_public_card_dataset(b, CARD_TODAY_FALLBACK_PUBLIC)
        computed_fb = _compute_today_from_public_fallback_dataset(fallback_ds) if fallback_ds else None
        if computed_fb:
            today_users, today_orders, today_qty, today_sales, today_products = computed_fb
            today_source = f"public_card:{CARD_TODAY_FALLBACK_PUBLIC}"

    return OrdersDashboardStats(
        as_of_iso=_utc_now_iso(),
        source=today_source,
        total_users=today_users,
        total_orders=today_orders,
        total_quantity=today_qty,
        total_sales=today_sales,
        total_products=today_products,
        past_day_orders=past_day_s,
        past_week_orders=past_week_s,
        past_month_orders=past_month_s,
        past_quarter_orders=past_quarter_s,
    )


