import razorpay
from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from fintelligent.extensions import db
from fintelligent.auth.models import User, Transaction
import os
from datetime import datetime, timedelta

payments = Blueprint('payments', __name__)

# Razorpay Config (In real app, these come from .env)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'placeholder_secret')

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

PLAN_PRICES = {
    'STUDENT': 2900, # In paise (₹29)
    'PRO': 9900      # In paise (₹99)
}

def is_mock_mode():
    return RAZORPAY_KEY_ID == 'rzp_test_placeholder' or RAZORPAY_KEY_ID == ''

@payments.route('/payment/checkout', methods=['POST'])
@login_required
def create_order():
    plan = request.form.get('plan')
    if plan not in PLAN_PRICES:
        return jsonify({'error': 'Invalid plan'}), 400
    
    amount = PLAN_PRICES[plan]
    
    # Create Razorpay Order
    data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"receipt_{current_user.id}_{int(datetime.now().timestamp())}",
        "notes": {
            "plan": plan,
            "user_id": current_user.id
        }
    }
    
    import random
    try:
        if is_mock_mode():
             # Create Mock Order for development
             order = {
                 'id': f'order_mock_{random.randint(1000, 9999)}',
                 'amount': amount
             }
        else:
             order = client.order.create(data=data)
        
        # Log Transaction in DB
        new_tx = Transaction(
            user_id=current_user.id,
            razorpay_order_id=order['id'],
            amount=amount/100,
            plan=plan,
            status='PENDING'
        )
        db.session.add(new_tx)
        db.session.commit()
        
        return render_template('checkout.html', 
                               order=order, 
                               key_id=RAZORPAY_KEY_ID,
                               plan=plan,
                               amount=amount/100,
                               is_mock=is_mock_mode())
    except Exception as e:
        flash(f"Error initiating payment: {str(e)}", "error")
        return redirect(url_for('main.pricing'))

@payments.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    try:
        data = request.json
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not is_mock_mode():
            # Verify signature only in real mode
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
        
        # Update Transaction
        tx = Transaction.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if tx:
            tx.razorpay_payment_id = razorpay_payment_id
            tx.razorpay_signature = razorpay_signature
            tx.status = 'SUCCESS'
            
            # Update User Tier
            user = User.query.get(tx.user_id)
            user.plan = tx.plan
            user.is_premium = True # Legacy support
            user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Payment successful!'})
        
        return jsonify({'success': False, 'message': 'Transaction not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
