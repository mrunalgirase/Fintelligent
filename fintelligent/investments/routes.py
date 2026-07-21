from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
import numpy as np
import pandas as pd
from datetime import datetime
import json

investments = Blueprint('investments', __name__)

@investments.route('/investments')
@login_required
def investment_dashboard():
    return render_template('investments.html')

@investments.route('/api/investments/roundup', methods=['POST'])
@login_required
def calculate_roundup():
    """Calculate spare change from a list of transactions"""
    data = request.json
    transactions = data.get('transactions', [])
    
    total_roundup = 0
    for amount in transactions:
        roundup = (np.ceil(amount) - amount)
        total_roundup += roundup
        
    return jsonify({
        'total_roundup': round(float(total_roundup), 2),
        'transaction_count': len(transactions)
    })

@investments.route('/api/investments/simulate', methods=['GET'])
def simulate_investment():
    """Simulate returns for a monthly SIP"""
    monthly_amount = float(request.args.get('amount', 1000))
    years = int(request.args.get('years', 5))
    expected_return = float(request.args.get('return', 12)) / 100 # Default 12%
    
    months = years * 12
    monthly_rate = expected_return / 12
    
    # FV = P * [((1 + r)^n - 1) / r] * (1 + r)
    future_value = monthly_amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
    
    total_invested = monthly_amount * months
    wealth_gained = future_value - total_invested
    
    return jsonify({
        'total_invested': round(total_invested, 2),
        'future_value': round(future_value, 2),
        'wealth_gained': round(wealth_gained, 2),
        'years': years
    })

@investments.route('/api/investments/recommend-sip', methods=['POST'])
@login_required
def recommend_sip():
    """Suggest SIP amount based on spending patterns"""
    # In a real app, we'd fetch actual spending data from DB
    # For now, we'll take it from input or use a default
    data = request.json
    avg_monthly_income = data.get('income', 50000)
    avg_monthly_expense = data.get('expenses', 30000)
    
    surplus = avg_monthly_income - avg_monthly_expense
    
    # 50/30/20 rule: 20% should go to savings/investments
    recommended_sip = max(0, avg_monthly_income * 0.2)
    
    # Adjust based on actual surplus
    if surplus < recommended_sip:
        recommended_sip = max(0, surplus * 0.7) # Save 70% of surplus
        
    return jsonify({
        'recommended_sip': round(float(recommended_sip), 0),
        'surplus': float(surplus),
        'savings_rate': round((recommended_sip / avg_monthly_income) * 100, 1)
    })

@investments.route('/api/investments/risk-profile', methods=['GET'])
@login_required
def get_risk_profile():
    """Mock risk profiling based on user behavior"""
    # A real implementation would analyze spending categories
    # (e.g. high entertainment spend might correlate with higher risk appetite?)
    # or use a dedicated questionnaire.
    
    # Placeholder profiles
    profiles = [
        {'type': 'Conservative', 'equity': 20, 'debt': 80, 'description': 'Focus on capital preservation.'},
        {'type': 'Moderate', 'equity': 50, 'debt': 50, 'description': 'Balanced growth and stability.'},
        {'type': 'Aggressive', 'equity': 80, 'debt': 20, 'description': 'Maximized long-term wealth creation.'}
    ]
    
    # Mock logic: older users or users with higher expense ratios might be conservative
    # For now, return a default or random for demo
    profile = profiles[1] # Moderate default
    
    return jsonify({
        'risk_profile': profile,
        'recommendation': f"We recommend a {profile['type']} portfolio with {profile['equity']}% Equity and {profile['debt']}% Debt."
    })
