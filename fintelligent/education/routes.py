from flask import Blueprint, render_template, request, jsonify

education = Blueprint('education', __name__)

@education.route('/education')
def education_home():
    return render_template('education.html')


@education.route('/education/students')
def education_students():
    return render_template('students.html')


@education.route('/education/glossary')
def education_glossary():
    return render_template('glossary.html')


@education.route('/api/sip-goal', methods=['POST'])
def api_sip_goal():
    data = request.get_json(force=True)
    target_amount = float(data.get('target', 0))
    years = float(data.get('years', 0))
    annual_rate = float(data.get('rate', 12)) / 100.0
    if target_amount <= 0 or years <= 0:
        return jsonify({"error": "Invalid inputs"}), 400
    monthly_rate = (1 + annual_rate) ** (1/12) - 1
    months = int(years * 12)
    if monthly_rate == 0:
        sip = target_amount / months
    else:
        sip = target_amount * monthly_rate / (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate))
    return jsonify({"monthly_sip": round(sip, 2)})


@education.route('/api/budget-advice', methods=['POST'])
def api_budget_advice():
    data = request.get_json(force=True)
    income = float(data.get('income', 0))
    if income <= 0:
        return jsonify({"error": "Invalid income"}), 400
    needs = round(income * 0.5, 2)
    wants = round(income * 0.3, 2)
    savings = round(income * 0.2, 2)
    return jsonify({"needs": needs, "wants": wants, "savings": savings})


@education.route('/api/pizza-sip', methods=['POST'])
def api_pizza_sip():
    data = request.get_json(force=True)
    monthly_investment = float(data.get('amount', 500)) # Default ₹500
    years = float(data.get('years', 10))
    annual_rate = float(data.get('rate', 12)) / 100.0
    
    months = int(years * 12)
    monthly_rate = (1 + annual_rate) ** (1/12) - 1
    
    # FV = P * [((1 + r)^n - 1) / r] * (1 + r)
    future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    total_invested = monthly_investment * months
    wealth_gained = future_value - total_invested
    
    return jsonify({
        "future_value": round(future_value, 2),
        "total_invested": round(total_invested, 2),
        "wealth_gained": round(wealth_gained, 2),
        "pizzas_sacrificed": months
    })