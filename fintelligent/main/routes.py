from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from fintelligent.extensions import db
import random

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

@main.route('/payment/checkout', methods=['POST'])
@login_required
def checkout():
    plan = request.form.get('plan')
    # logic to handle different plans if needed
    return render_template('payment_mock.html', plan=plan)

@main.route('/payment/success', methods=['POST'])
@login_required
def payment_success():
    # In real world, verify payment ID here
    current_user.is_premium = True
    db.session.commit()
    flash('Payment Successful! Welcome to Fintelligent Pro.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/expenses')
@login_required
def expenses():
    from fintelligent.auth.models import Expense
    user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    dashboard_data = get_dashboard_data(current_user.id)
    return render_template('expenses.html', expenses=user_expenses, dashboard_data=dashboard_data)

def get_dashboard_data(user_id):
    from fintelligent.auth.models import Expense, User
    import pandas as pd
    from datetime import datetime
    import calendar
    
    expenses = Expense.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)
    budget_limit = getattr(user, 'monthly_budget', 20000.0) or 20000.0
    
    if not expenses:
        return {
            'total_spent': 0,
            'total_spending': 0,
            'category_distribution': {},
            'category_totals': {},
            'monthly_trend': {'labels': [], 'data': []},
            'monthly_labels': [],
            'monthly_data': [],
            'budget': {'limit': budget_limit, 'status': 'healthy', 'spent': 0, 'forecast': 0, 'burn_rate': 0},
            'health_score': {'score': 0, 'level': 'Initializing', 'color': '#94a3b8', 'factors': {}, 'recommendations': []},
            'insights': []
        }

    df = pd.DataFrame([{
        'amount': e.amount,
        'category': e.category,
        'date': e.date,
        'merchant': e.merchant
    } for e in expenses])
    
    now = datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_df = df[df['date'] >= first_day]
    
    spent_this_month = float(current_month_df['amount'].sum())
    days_passed = (now - first_day).days + 1
    burn_rate = spent_this_month / max(1, days_passed)
    
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_remaining = days_in_month - days_passed
    forecast = spent_this_month + (burn_rate * days_remaining)
    
    # Health Score Calculation (Balanced logic)
    savings_rate = max(0, (budget_limit - spent_this_month) / budget_limit) * 100
    score = 70
    if savings_rate > 30: score += 15
    elif savings_rate > 10: score += 5
    else: score -= 10
    score = min(score, 100)
    
    level = "Gold" if score > 80 else "Silver" if score > 60 else "Bronze"
    color = "#fbbf24" if level == "Gold" else "#94a3b8" if level == "Silver" else "#cd7f32"
    
    cat_dist = df.groupby('category')['amount'].sum().to_dict()
    df['month_key'] = df['date'].dt.strftime('%b %Y')
    monthly_trend_raw = df.groupby('month_key')['amount'].sum().tail(6)
    
    return {
        'total_spent': float(df['amount'].sum()),
        'total_spending': float(df['amount'].sum()),
        'spent_this_month': spent_this_month,
        'category_distribution': {k: float(v) for k, v in cat_dist.items()},
        'category_totals': {k: float(v) for k, v in cat_dist.items()},
        'monthly_trend': {
            'labels': list(monthly_trend_raw.index),
            'data': [float(v) for v in monthly_trend_raw.values]
        },
        'monthly_labels': list(monthly_trend_raw.index),
        'monthly_data': [float(v) for v in monthly_trend_raw.values],
        'budget': {
            'limit': budget_limit,
            'spent': spent_this_month,
            'forecast': float(forecast),
            'burn_rate': float(burn_rate),
            'status': 'broke_alert' if forecast > budget_limit else ('warning' if forecast > budget_limit * 0.85 else 'healthy')
        },
        'health_score': {
            'score': score,
            'level': level,
            'color': color,
            'factors': {
                'Savings': {'score': savings_rate, 'status': 'Good' if savings_rate > 20 else 'Fair'},
                'Budget': {'score': (1 - (spent_this_month / budget_limit)) * 100 if budget_limit > 0 else 0, 'status': 'Safe' if spent_this_month < budget_limit else 'Over'},
                'Velocity': {'score': 100 - (spent_this_month / (now.day / 30 * budget_limit) * 100) if spent_this_month > 0 else 100, 'status': 'Steady'}
            },
            'recommendations': [
                "Alert: Spending is trending high." if forecast > budget_limit else "Budget looks healthy.",
                "Review your '{}' category for savings.".format(max(cat_dist, key=cat_dist.get) if cat_dist else "top")
            ]
        },
        'insights': [],
        'cluster_colors': ["#3b82f6", "#10b981", "#f59e0b"],
        'n_clusters': 0,
        'pca_points': [],
        'centers_points': [],
        'cluster_stats': {}
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