"""Shared analytics helpers for dashboard and analytics pages."""
from __future__ import annotations

import calendar
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

CLUSTER_NAMES = [
    "Dining & Food", "Shopping", "Grocery & Essentials",
    "Transport", "Entertainment", "Others",
]
CLUSTER_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#f43f5e", "#a78bfa", "#64748b"]
CLUSTER_ICONS = ["fa-utensils", "fa-bag-shopping", "fa-cart-shopping", "fa-bus", "fa-film", "fa-microchip"]


def expenses_to_dataframe(expenses) -> pd.DataFrame:
    if not expenses:
        return pd.DataFrame(columns=["amount", "category", "date", "merchant"])
    return pd.DataFrame([{
        "amount": e.amount,
        "category": e.category or "Others",
        "date": e.date,
        "merchant": e.merchant or "Unknown",
    } for e in expenses])


def compute_roundup_savings(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    spare = 0.0
    for amount in df["amount"]:
        remainder = round(float(amount) % 10, 2)
        if remainder > 0:
            spare += 10 - remainder
    return round(spare, 2)


def compute_recommended_sip(budget_limit: float, spent_this_month: float) -> int:
    surplus = max(0.0, budget_limit - spent_this_month)
    if surplus <= 0:
        return 500
    return max(500, int(round(surplus * 0.15 / 500) * 500))


def run_clustering(df: pd.DataFrame) -> dict[str, Any]:
    """K-Means + PCA on category-level spending features."""
    empty = {
        "n_clusters": 0,
        "pca_points": [],
        "centers_points": [],
        "cluster_stats": {},
        "cluster_colors": CLUSTER_COLORS,
    }
    if len(df) < 5:
        return empty

    try:
        cat_features = df.groupby("category")["amount"].agg(["mean", "sum", "count"])
        n_cats = len(cat_features)
        n_clusters = min(max(2, n_cats), 5)

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(cat_features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(x_scaled)

        n_components = min(2, n_cats)
        pca = PCA(n_components=n_components)
        pca_res = pca.fit_transform(x_scaled)
        if pca_res.shape[1] == 1:
            pca_res = np.column_stack([pca_res[:, 0], np.zeros(len(pca_res))])

        pca_points = []
        for i, (point, cluster_id) in enumerate(zip(pca_res, clusters)):
            pca_points.append({
                "x": float(point[0]),
                "y": float(point[1]) if len(point) > 1 else 0.0,
                "cluster": int(cluster_id),
                "label": str(cat_features.index[i]),
            })

        category_to_cluster = dict(zip(list(cat_features.index), clusters))
        df = df.copy()
        df["cluster"] = df["category"].map(category_to_cluster)
        total_spent = float(df["amount"].sum())

        cluster_stats = {}
        for cid in range(n_clusters):
            c_df = df[df["cluster"] == cid]
            if c_df.empty:
                continue
            c_total = float(c_df["amount"].sum())
            c_count = len(c_df)
            cluster_stats[cid] = {
                "count": c_count,
                "avg_amount": float(c_df["amount"].mean()),
                "total_amount": c_total,
                "frequency_score": round(min(10.0, (c_count / len(df)) * 20), 2),
                "spend_ratio": round((c_total / total_spent) * 100, 1),
                "categories": [str(x) for x in c_df.groupby("category")["amount"].sum().nlargest(3).index.tolist()],
                "merchants": [str(x) for x in c_df["merchant"].value_counts().head(3).index.tolist()],
                "payment_methods": {"UPI": c_count},
            }

        return {
            "n_clusters": n_clusters,
            "pca_points": pca_points,
            "centers_points": [],
            "cluster_stats": cluster_stats,
            "cluster_colors": CLUSTER_COLORS[:n_clusters],
        }
    except Exception as exc:
        print(f"Clustering error: {exc}")
        return empty


def cluster_stats_to_details(cluster_stats: dict, n_clusters: int) -> tuple[dict, list]:
    """Convert dashboard cluster_stats to analytics cluster_details format."""
    cluster_details = {}
    cluster_list = []
    for cid in range(n_clusters):
        stats = cluster_stats.get(cid)
        if not stats:
            continue
        detail = {
            "name": CLUSTER_NAMES[cid] if cid < len(CLUSTER_NAMES) else f"Cluster {cid + 1}",
            "color": CLUSTER_COLORS[cid] if cid < len(CLUSTER_COLORS) else "#64748b",
            "icon": CLUSTER_ICONS[cid] if cid < len(CLUSTER_ICONS) else "fa-cube",
            "count": int(stats.get("count", 0)),
            "avg_amount": float(stats.get("avg_amount", 0)),
            "total_amount": float(stats.get("total_amount", 0)),
            "frequency_score": float(stats.get("frequency_score", 0)),
            "spend_ratio": float(stats.get("spend_ratio", 0)),
            "top_categories": stats.get("categories", []),
            "primary_categories": stats.get("categories", []),
            "top_merchants": stats.get("merchants", ["—"]),
            "payment_methods": stats.get("payment_methods", {}),
        }
        cluster_details[int(cid)] = detail
        cluster_list.append((int(cid), detail))
    return cluster_details, cluster_list


def build_insights(cat_dist: dict, forecast: float, budget_limit: float, transaction_count: int) -> list[dict]:
    insights = []
    if not cat_dist:
        return [{
            "type": "info",
            "title": "Get Started",
            "message": "Scan a receipt or upload a bank statement to unlock personalized insights.",
        }]

    top_cat = max(cat_dist, key=cat_dist.get)
    top_val = float(cat_dist[top_cat])
    insights.append({
        "type": "info",
        "title": "Top Spending Category",
        "message": f"{top_cat} leads at ₹{top_val:,.0f} across {transaction_count} transactions.",
    })

    if forecast > budget_limit:
        insights.append({
            "type": "warning",
            "title": "Budget Alert",
            "message": f"Projected month-end spend (₹{forecast:,.0f}) exceeds your ₹{budget_limit:,.0f} budget.",
        })
    elif forecast > budget_limit * 0.85:
        insights.append({
            "type": "warning",
            "title": "Approaching Limit",
            "message": "You're on track to use most of your monthly budget. Consider slowing discretionary spends.",
        })
    else:
        insights.append({
            "type": "success",
            "title": "Healthy Pace",
            "message": "Your spending velocity is within budget. Great discipline this month.",
        })

    if top_val > sum(cat_dist.values()) * 0.4:
        insights.append({
            "type": "warning",
            "title": "Category Concentration",
            "message": f"Over 40% of spending is in {top_cat}. Diversifying could improve savings.",
        })

    return insights


def get_market_snapshot() -> list[dict]:
    """Fetch live NSE index snapshot; fall back to static demo values."""
    fallback = [
        {"name": "NIFTY 50", "price": "22,147.50", "change": "+142.30 (0.65%)", "positive": True},
        {"name": "SENSEX", "price": "73,088.33", "change": "+482.70 (0.66%)", "positive": True},
        {"name": "BANK NIFTY", "price": "46,919.80", "change": "-85.40 (0.18%)", "positive": False},
    ]
    try:
        import yfinance as yf

        symbols = [("NIFTY 50", "^NSEI"), ("SENSEX", "^BSESN"), ("BANK NIFTY", "^NSEBANK")]
        result = []
        for name, symbol in symbols:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) < 2:
                continue
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2])
            chg = price - prev
            pct = (chg / prev) * 100 if prev else 0
            result.append({
                "name": name,
                "price": f"{price:,.2f}",
                "change": f"{chg:+,.2f} ({pct:+.2f}%)",
                "positive": chg >= 0,
            })
        return result if len(result) == 3 else fallback
    except Exception:
        return fallback
