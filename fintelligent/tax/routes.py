from flask import Blueprint, render_template, request, jsonify
import math

tax = Blueprint('tax', __name__)

def calculate_new_regime_tax(income, deductions=None):
    """Calculate tax under the new regime (2024-25)"""
    if deductions is None:
        deductions = {}
    
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

def calculate_old_regime_tax(income, deductions=None):
    """Calculate tax under the old regime for comparison"""
    if deductions is None:
        deductions = {}
    
    # Basic exemption limit
    taxable_income = max(0, income - 250000)
    
    # Apply deductions (simplified for demo)
    total_deductions = sum(deductions.values()) if deductions else 0
    taxable_income = max(0, taxable_income - total_deductions)
    
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

def calculate_tds(income, frequency='monthly'):
    """Calculate TDS based on income and frequency"""
    annual_income = income
    if frequency == 'monthly':
        annual_income = income * 12
    elif frequency == 'quarterly':
        annual_income = income * 4
    elif frequency == 'daily':
        annual_income = income * 365
    
    # Calculate annual tax
    new_regime_tax = calculate_new_regime_tax(annual_income)
    
    # Return monthly TDS
    if frequency == 'monthly':
        return new_regime_tax / 12
    elif frequency == 'quarterly':
        return new_regime_tax / 4
    elif frequency == 'daily':
        return new_regime_tax / 365
    else:
        return new_regime_tax

def calculate_advance_tax(income, current_quarter=1):
    """Calculate advance tax liability"""
    annual_tax = calculate_new_regime_tax(income)
    
    # Advance tax schedule
    advance_tax_schedule = {
        1: 0.15,  # 15% by June 15
        2: 0.45,  # 45% by September 15
        3: 0.75,  # 75% by December 15
        4: 1.00   # 100% by March 15
    }
    
    due_amount = annual_tax * advance_tax_schedule.get(current_quarter, 1.00)
    return due_amount

def calculate_hra_exemption(basic_salary, hra_received, rent_paid, city_type='metro'):
    """Calculate HRA exemption (for old regime comparison)"""
    # HRA exemption is minimum of:
    # 1. Actual HRA received
    # 2. Rent paid - 10% of basic salary
    # 3. 50% of basic salary (metro) or 40% (non-metro)
    
    if city_type == 'metro':
        limit_percentage = 0.50
    else:
        limit_percentage = 0.40
    
    exemption1 = hra_received
    exemption2 = max(0, rent_paid - (basic_salary * 0.10))
    exemption3 = basic_salary * limit_percentage
    
    return min(exemption1, exemption2, exemption3)

def calculate_lta_exemption(income, lta_claimed=0):
    """Calculate LTA exemption (for old regime comparison)"""
    # LTA exemption is limited to actual amount claimed or ₹40,000 per year
    return min(lta_claimed, 40000)

@tax.route('/tax')
def tax_home():
    return render_template('tax_calculator.html')

@tax.route('/tax/tds-calculator')
def tds_calculator():
    return render_template('tds_calculator.html')

@tax.route('/tax/hra-calculator')
def hra_calculator():
    return render_template('hra_calculator.html')

@tax.route('/tax/advance-tax-calculator')
def advance_tax_calculator():
    return render_template('advance_tax_calculator.html')

@tax.route('/tax/calculate', methods=['POST'])
def calculate_tax():
    try:
        data = request.get_json()
        income = int(data.get('income', 0))
        deductions = data.get('deductions', {})
        
        if income <= 0:
            return jsonify({'error': 'Income must be greater than 0'}), 400
        
        # Calculate taxes
        new_regime_tax = calculate_new_regime_tax(income, deductions)
        old_regime_tax = calculate_old_regime_tax(income, deductions)
        
        # Calculate additional metrics
        monthly_tds = calculate_tds(income / 12, 'monthly')
        advance_tax_q1 = calculate_advance_tax(income, 1)
        advance_tax_q2 = calculate_advance_tax(income, 2)
        advance_tax_q3 = calculate_advance_tax(income, 3)
        advance_tax_q4 = calculate_advance_tax(income, 4)
        
        # Determine which regime is better
        better_regime = "New Regime" if new_regime_tax < old_regime_tax else "Old Regime"
        savings = abs(new_regime_tax - old_regime_tax)
        
        result = {
            'income': income,
            'new_regime_tax': round(new_regime_tax, 2),
            'old_regime_tax': round(old_regime_tax, 2),
            'recommended_regime': better_regime,
            'savings': round(savings, 2),
            'effective_rate_new': round((new_regime_tax / income) * 100, 2),
            'effective_rate_old': round((old_regime_tax / income) * 100, 2),
            'monthly_tds': round(monthly_tds, 2),
            'advance_tax': {
                'q1': round(advance_tax_q1, 2),
                'q2': round(advance_tax_q2, 2),
                'q3': round(advance_tax_q3, 2),
                'q4': round(advance_tax_q4, 2)
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax.route('/tax/tds', methods=['POST'])
def calculate_tds_endpoint():
    try:
        data = request.get_json()
        income = int(data.get('income', 0))
        frequency = data.get('frequency', 'monthly')
        
        if income <= 0:
            return jsonify({'error': 'Income must be greater than 0'}), 400
        
        tds_amount = calculate_tds(income, frequency)
        
        result = {
            'income': income,
            'frequency': frequency,
            'tds_amount': round(tds_amount, 2),
            'annual_income': income * (12 if frequency == 'monthly' else 4 if frequency == 'quarterly' else 365)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax.route('/tax/hra', methods=['POST'])
def calculate_hra_endpoint():
    try:
        data = request.get_json()
        basic_salary = int(data.get('basic_salary', 0))
        hra_received = int(data.get('hra_received', 0))
        rent_paid = int(data.get('rent_paid', 0))
        city_type = data.get('city_type', 'metro')
        
        if basic_salary <= 0:
            return jsonify({'error': 'Basic salary must be greater than 0'}), 400
        
        hra_exemption = calculate_hra_exemption(basic_salary, hra_received, rent_paid, city_type)
        
        result = {
            'basic_salary': basic_salary,
            'hra_received': hra_received,
            'rent_paid': rent_paid,
            'city_type': city_type,
            'hra_exemption': round(hra_exemption, 2),
            'taxable_hra': round(hra_received - hra_exemption, 2)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 