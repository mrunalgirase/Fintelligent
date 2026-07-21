from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from fintelligent.extensions import db
import random
import calendar
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # If user is verified and premium, they might want to go straight to dashboard
    # But homepage is good landing.
    
    # Generate some sample data for the dashboard
    sample_data = {
        'total_savings': random.randint(200000, 500000),
        'tax_saved': random.randint(30000, 80000),
        'investments': random.randint(150000, 400000),
        'financial_score': random.randint(75, 95)
    }
    return render_template('home.html', data=sample_data)

@main.route('/pricing')
def pricing():
    return render_template('pricing.html')

@main.route('/budget2026')
def budget2026():
    """Union Budget 2026 - Youth & Student Benefits"""
    return render_template('budget2026.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/about')
def about():
    return render_template('about.html')



@main.route('/expenses')
@login_required
def expenses():
    from fintelligent.auth.models import Expense
    user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    dashboard_data = get_dashboard_data(current_user.id)
    return render_template('expenses.html', expenses=user_expenses, dashboard_data=dashboard_data)

def get_dashboard_data(user_id):
    from fintelligent.auth.models import Expense, User
    from fintelligent.utils.analytics_engine import (
        build_insights,
        compute_recommended_sip,
        compute_roundup_savings,
        expenses_to_dataframe,
        run_clustering,
    )

    expenses = Expense.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)
    budget_limit = getattr(user, 'monthly_budget', 20000.0) or 20000.0
    now = datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_passed = now.day
    days_remaining = max(0, days_in_month - days_passed)

    if not expenses:
        return {
            'has_data': False,
            'transaction_count': 0,
            'total_spent': 0,
            'total_spending': 0,
            'spent_this_month': 0,
            'category_distribution': {},
            'category_totals': {},
            'monthly_trend': {'labels': [], 'data': []},
            'monthly_labels': [],
            'monthly_data': [],
            'budget': {
                'limit': budget_limit,
                'status': 'healthy',
                'spent': 0,
                'forecast': 0,
                'burn_rate': 0,
                'days_remaining': days_remaining,
            },
            'health_score': {
                'score': 0,
                'level': 'Getting Started',
                'color': '#94a3b8',
                'message': 'Add your first transaction to unlock your financial health score.',
                'factors': {},
                'recommendations': [
                    'Scan a receipt to start tracking expenses.',
                    'Upload a bank statement for AI-powered analytics.',
                ],
            },
            'insights': build_insights({}, 0, budget_limit, 0),
            'budget_suggestions': {},
            'ai_insights': [{
                'type': 'info',
                'text': 'Welcome! Scan a receipt or upload a CSV in Analytics to get started.',
            }],
            'roundup_savings': 0,
            'recommended_sip': 500,
            'n_clusters': 0,
            'pca_points': [],
            'centers_points': [],
            'cluster_stats': {},
            'cluster_colors': [],
        }

    df = expenses_to_dataframe(expenses)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_df = df[df['date'] >= first_day]

    spent_this_month = float(current_month_df['amount'].sum())
    burn_rate = spent_this_month / max(1, days_passed)
    forecast = spent_this_month + (burn_rate * days_remaining)

    savings_rate = max(0, (budget_limit - spent_this_month) / budget_limit) * 100 if budget_limit > 0 else 0
    score = 70
    if savings_rate > 30:
        score += 15
    elif savings_rate > 10:
        score += 5
    else:
        score -= 10
    score = max(0, min(int(score), 100))

    level = "Gold" if score > 80 else "Silver" if score > 60 else "Bronze"
    color = "#fbbf24" if level == "Gold" else "#94a3b8" if level == "Silver" else "#cd7f32"
    if score == 0:
        level, color = "Getting Started", "#94a3b8"

    cat_dist = df.groupby('category')['amount'].sum().to_dict()
    df['month_key'] = df['date'].dt.strftime('%b %Y')
    monthly_trend_raw = df.groupby('month_key')['amount'].sum().tail(6)

    budget_status = (
        'broke_alert' if forecast > budget_limit
        else 'warning' if forecast > budget_limit * 0.85
        else 'healthy'
    )
    health_message = (
        "Excellent financial discipline — keep it up!"
        if score > 80 else
        "Solid progress. Small optimizations can boost your score."
        if score > 60 else
        "Review high-spend categories to improve your financial health."
    )

    clustering = run_clustering(df)
    insights = build_insights(cat_dist, forecast, budget_limit, len(expenses))
    top_cat = max(cat_dist, key=cat_dist.get) if cat_dist else "spending"

    return {
        'has_data': True,
        'transaction_count': len(expenses),
        'total_spent': float(df['amount'].sum()),
        'total_spending': float(df['amount'].sum()),
        'spent_this_month': spent_this_month,
        'category_distribution': {k: float(v) for k, v in cat_dist.items()},
        'category_totals': {k: float(v) for k, v in cat_dist.items()},
        'monthly_trend': {
            'labels': list(monthly_trend_raw.index),
            'data': [float(v) for v in monthly_trend_raw.values],
        },
        'monthly_labels': list(monthly_trend_raw.index),
        'monthly_data': [float(v) for v in monthly_trend_raw.values],
        'budget': {
            'limit': budget_limit,
            'spent': spent_this_month,
            'forecast': float(forecast),
            'burn_rate': float(burn_rate),
            'status': budget_status,
            'days_remaining': days_remaining,
        },
        'health_score': {
            'score': score,
            'level': level,
            'color': color,
            'message': health_message,
            'factors': {
                'Savings': {'score': savings_rate, 'status': 'Good' if savings_rate > 20 else 'Fair'},
                'Budget': {
                    'score': max(0, (1 - (spent_this_month / budget_limit)) * 100) if budget_limit > 0 else 0,
                    'status': 'Safe' if spent_this_month < budget_limit else 'Over',
                },
                'Velocity': {
                    'score': max(0, 100 - (spent_this_month / max(1, (now.day / 30) * budget_limit) * 100)),
                    'status': 'Steady' if budget_status == 'healthy' else 'High',
                },
            },
            'recommendations': [
                "Reduce discretionary spending to stay within budget." if forecast > budget_limit else "Budget looks healthy — consider increasing SIP.",
                f"Review your '{top_cat}' category for potential savings.",
            ],
        },
        'budget_suggestions': {cat: round(amt * 0.9, 2) for cat, amt in cat_dist.items()},
        'ai_insights': [
            {
                'type': 'warning' if budget_status != 'healthy' else 'info',
                'text': f"Your {top_cat} category is your largest spend area this month.",
            },
            {
                'type': 'success',
                'text': f"You've tracked {len(expenses)} transactions — ₹{float(df['amount'].sum()):,.0f} total analyzed.",
            },
            {
                'type': 'info',
                'text': f"Smart Roundup could invest ₹{compute_roundup_savings(current_month_df):,.0f} in spare change this month.",
            },
        ],
        'insights': insights,
        'roundup_savings': compute_roundup_savings(current_month_df),
        'recommended_sip': compute_recommended_sip(budget_limit, spent_this_month),
        'cluster_colors': clustering['cluster_colors'],
        'n_clusters': clustering['n_clusters'],
        'pca_points': clustering['pca_points'],
        'centers_points': clustering['centers_points'],
        'cluster_stats': clustering['cluster_stats'],
    }

@main.route('/api/update-budget', methods=['POST'])
@login_required
def update_budget():
    data = request.get_json()
    new_budget = data.get('budget')
    if new_budget is not None:
        try:
            current_user.monthly_budget = float(new_budget)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Budget updated successfully!'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid budget value.'}), 400
    return jsonify({'success': False, 'message': 'No budget provided.'}), 400

@main.route('/api/dashboard-stats')
def dashboard_stats():
    """API endpoint to get real-time dashboard statistics"""
    return jsonify({
        'total_savings': random.randint(200000, 500000),
        'tax_saved': random.randint(30000, 80000),
        'investments': random.randint(150000, 400000),
        'financial_score': random.randint(75, 95),
        'monthly_income': random.randint(80000, 200000),
        'expenses': random.randint(40000, 120000),
        'savings_rate': random.randint(15, 40)
    })