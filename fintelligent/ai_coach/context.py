"""Build rich financial context for AI Coach from receipts, CSV analytics, and statements."""
from __future__ import annotations

from typing import Any

from fintelligent.auth.models import Expense


def _format_expense_lines(expenses, limit: int = 12) -> list[str]:
    lines = []
    for e in expenses[:limit]:
        src = getattr(e, 'source', 'receipt') or 'receipt'
        lines.append(
            f"- {e.date.strftime('%Y-%m-%d')}: ₹{e.amount:,.2f} at {e.merchant} "
            f"({e.category}) [{src}]"
        )
    return lines


def _format_analytics_summary(analytics: dict[str, Any]) -> list[str]:
    lines = [
        "=== ANALYTICS CSV SYNTHESIS ===",
        f"Total analyzed: ₹{analytics.get('total_spent', 0):,.0f}",
        f"Transaction count: {analytics.get('transaction_count', 0)}",
        f"Financial profile: {analytics.get('financial_category', 'N/A')}",
    ]
    health = analytics.get('health_score') or {}
    if health:
        lines.append(
            f"Health score: {health.get('score', 0)}/100 ({health.get('level', 'N/A')})"
        )
        if health.get('message'):
            lines.append(f"Health note: {health['message']}")

    cat_dist = analytics.get('category_distribution') or {}
    if cat_dist:
        lines.append("Category breakdown:")
        for cat, amt in sorted(cat_dist.items(), key=lambda x: x[1], reverse=True)[:8]:
            lines.append(f"  • {cat}: ₹{float(amt):,.0f}")

    overspend = analytics.get('overspending_areas') or {}
    if overspend:
        lines.append("High-spend areas:")
        for cat, amt in overspend.items():
            lines.append(f"  • {cat}: ₹{float(amt):,.0f}")

    for insight in (analytics.get('insights') or [])[:5]:
        lines.append(f"Insight: {insight}")

    cluster_details = analytics.get('cluster_details') or {}
    if cluster_details:
        lines.append("Behavioral clusters:")
        for _cid, det in sorted(cluster_details.items()):
            name = det.get('name', 'Cluster')
            total = det.get('total_amount', 0)
            ratio = det.get('spend_ratio', 0)
            cats = ', '.join(det.get('top_categories') or det.get('primary_categories') or [])
            lines.append(f"  • {name}: ₹{float(total):,.0f} ({float(ratio):.1f}%) — {cats}")

    sample = analytics.get('transactions_sample') or []
    if sample:
        lines.append("Sample CSV transactions:")
        for tx in sample[:15]:
            lines.append(
                f"  - {tx.get('date')}: ₹{float(tx.get('amount', 0)):,.2f} "
                f"{tx.get('merchant', 'Unknown')} ({tx.get('category', 'Others')})"
            )
    return lines


def _format_statement_summary(statement: dict[str, Any]) -> list[str]:
    lines = ["=== BANK STATEMENT ANALYSIS ==="]
    summary = statement.get('summary') or {}
    lines.append(f"Total debits: ₹{summary.get('total_debit', 0):,.0f}")
    lines.append(f"Transactions extracted: {summary.get('count', 0)}")
    for cat, amt in (summary.get('categories') or {}).items():
        lines.append(f"  • {cat}: ₹{float(amt):,.0f}")
    for insight in (statement.get('insights') or [])[:3]:
        lines.append(f"Insight: {insight}")
    return lines


def build_coach_context(user_id: int, session: dict | None = None) -> str:
    """Merge receipt, CSV analytics, and statement data for the AI coach."""
    session = session or {}
    sections: list[str] = []

    all_expenses = Expense.query.filter_by(user_id=user_id).order_by(
        Expense.date.desc()
    ).limit(40).all()

    csv_expenses = [e for e in all_expenses if e.source == 'csv_upload']
    receipt_expenses = [e for e in all_expenses if e.source in (None, 'receipt')]
    statement_expenses = [e for e in all_expenses if e.source == 'bank_statement']

    analytics = session.get('analytics_data')
    if analytics:
        sections.extend(_format_analytics_summary(analytics))
    elif csv_expenses:
        sections.append("=== ANALYTICS CSV DATA (from saved uploads) ===")
        sections.extend(_format_expense_lines(csv_expenses, 20))

    statement = session.get('statement_data')
    if statement:
        sections.extend(_format_statement_summary(statement))
    elif statement_expenses:
        sections.append("=== BANK STATEMENT TRANSACTIONS ===")
        sections.extend(_format_expense_lines(statement_expenses, 15))

    if receipt_expenses:
        sections.append("=== RECEIPT SCANS ===")
        sections.extend(_format_expense_lines(receipt_expenses, 12))

    if not sections:
        return "No financial data recorded yet. User has not uploaded CSV, scanned receipts, or statements."

    return "\n".join(sections)


def get_data_sources(user_id: int, session: dict | None = None) -> list[str]:
    """Human-readable list of connected data sources for UI."""
    session = session or {}
    sources = []
    if session.get('analytics_data') or Expense.query.filter_by(
        user_id=user_id, source='csv_upload'
    ).first():
        sources.append('Analytics CSV')
    if session.get('statement_data') or Expense.query.filter_by(
        user_id=user_id, source='bank_statement'
    ).first():
        sources.append('Bank Statement')
    if Expense.query.filter_by(user_id=user_id, source='receipt').first():
        sources.append('Receipts')
    return sources or ['No data yet']
