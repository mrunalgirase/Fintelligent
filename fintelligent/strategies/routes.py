from flask import Blueprint, render_template, request, session
from flask_login import login_required
from fintelligent.utils.decorators import tier_required
import pandas as pd

strategies = Blueprint('strategies', __name__)

def save_user_tax_data_new(user_id, income):
    """Save user tax data for new regime analysis"""
    import csv
    import os
    import pandas as pd
    
    csv_path = 'user_tax_data_new.csv'
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['user_id', 'income', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'user_id': user_id,
            'income': income,
            'timestamp': pd.Timestamp.now().isoformat()
        })

def get_income_based_recommendation(income):
    """Provide recommendations based on income level for new tax regime"""
    if income <= 500000:
        return (
            "• Your income is below ₹5L - you're likely in the zero-tax bracket<br>"
            "• Focus on building emergency fund and basic investments<br>"
            "• Consider PPF and EPF for long-term wealth building"
        )
    elif income <= 1000000:
        return (
            "• Consider the New Tax Regime for simplicity<br>"
            "• Focus on standard deduction (₹75,000) and rebate benefits<br>"
            "• Build a diversified investment portfolio<br>"
            "• Consider ELSS mutual funds for wealth creation"
        )
    elif income <= 1500000:
        return (
            "• Compare both tax regimes carefully<br>"
            "• New regime may be beneficial due to higher standard deduction<br>"
            "• Consider tax-saving investments like NPS<br>"
            "• Plan for retirement with systematic investments"
        )
    else:
        return (
            "• Higher income - tax planning is crucial<br>"
            "• Consider professional tax advice<br>"
            "• Diversify investments across asset classes<br>"
            "• Plan for long-term wealth preservation<br>"
            "• Consider tax-efficient investment vehicles"
        )

def calculate_new_regime_tax(income):
    """Calculate tax under the new regime (2024-25)"""
    # Apply standard deduction
    taxable_income = max(0, income - 75000)
    
    # Calculate tax based on new slabs
    tax = 0
    if taxable_income > 400000:
        # 5% on income from 4L to 8L
        tax += min(400000, taxable_income - 400000) * 0.05
    if taxable_income > 800000:
        # 10% on income from 8L to 12L
        tax += min(400000, taxable_income - 800000) * 0.10
    if taxable_income > 1200000:
        # 15% on income from 12L to 16L
        tax += min(400000, taxable_income - 1200000) * 0.15
    if taxable_income > 1600000:
        # 20% on income from 16L to 20L
        tax += min(400000, taxable_income - 1600000) * 0.20
    if taxable_income > 2000000:
        # 25% on income from 20L to 24L
        tax += min(400000, taxable_income - 2000000) * 0.25
    if taxable_income > 2400000:
        # 30% on income above 24L
        tax += (taxable_income - 2400000) * 0.30
    
    # Apply Section 87A rebate (up to ₹60,000) for income up to ₹12 lakh
    if income <= 1200000:
        tax = max(0, tax - 60000)
    
    return tax

def calculate_old_regime_tax(income):
    """Calculate tax under the old regime for comparison"""
    # Basic exemption limit
    taxable_income = max(0, income - 250000)
    
    tax = 0
    if taxable_income > 0:
        # 5% on income from 2.5L to 5L
        tax += min(250000, taxable_income) * 0.05
    if taxable_income > 250000:
        # 20% on income from 5L to 10L
        tax += min(500000, taxable_income - 250000) * 0.20
    if taxable_income > 750000:
        # 30% on income above 10L
        tax += (taxable_income - 750000) * 0.30
    
    # Apply Section 87A rebate (up to ₹12,500) for income up to ₹5 lakh
    if income <= 500000:
        tax = max(0, tax - 12500)
    
    return tax

@strategies.route('/strategies', methods=['GET', 'POST'])
@login_required
@tier_required('PRO')
def strategies_page():
    plan = None
    ai_recommendation = None
    user_input = {}
    if request.method == 'POST':
        # For demo, use session or a dummy user_id
        user_id = session.get('user_id', 1)
        income = int(request.form.get('income', 0))
        user_input = {'income': income}
        
        # Calculate taxes under both regimes
        new_regime_tax = calculate_new_regime_tax(income)
        old_regime_tax = calculate_old_regime_tax(income)
        
        # Save simplified data to CSV
        save_user_tax_data_new(user_id, income)
        
        # AI/ML recommendation based on income level
        ai_recommendation = get_income_based_recommendation(income)
        
        # Determine which regime is better
        better_regime = "New Regime" if new_regime_tax < old_regime_tax else "Old Regime"
        savings = abs(new_regime_tax - old_regime_tax)
        
        # Build a personalized plan
        plan = (
            f"<h3>Tax Calculation Results (2024-25)</h3>"
            f"<strong>Annual Income:</strong> ₹{income:,}<br><br>"
            f"<strong>New Regime Tax:</strong> ₹{new_regime_tax:,.0f}<br>"
            f"<strong>Old Regime Tax:</strong> ₹{old_regime_tax:,.0f}<br><br>"
            f"<strong>Recommended:</strong> {better_regime}<br>"
            f"<strong>Tax Savings:</strong> ₹{savings:,.0f}<br><br>"
            f"<em>Note: Under the new regime, traditional deductions like 80C and 80D are not available, "
            f"but you get a higher standard deduction of ₹75,000 and a rebate of ₹60,000 for income up to ₹12 lakh.</em>"
        )
        
        if ai_recommendation:
            plan += "<br><strong>AI Recommendations:</strong><br>"
            plan += ai_recommendation
            
    return render_template('strategies.html', plan=plan, ai_recommendation=ai_recommendation, user_input=user_input) 