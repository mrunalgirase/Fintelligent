import os
import sys
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from fintelligent.utils.decorators import tier_required
from werkzeug.utils import secure_filename

# Dynamic venv path discovery
def find_site_packages():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    venv_base = os.path.join(root, '.venv', 'lib')
    if os.path.exists(venv_base):
        for py_dir in os.listdir(venv_base):
            if py_dir.startswith('python'):
                site_path = os.path.join(venv_base, py_dir, 'site-packages')
                if os.path.exists(site_path):
                    return site_path
    return None

_site_path = find_site_packages()
if _site_path and _site_path not in sys.path:
    sys.path.insert(0, _site_path)

import base64
import json
import re
from datetime import datetime
from fintelligent.auth.models import Expense
from fintelligent.extensions import db

receipts = Blueprint('receipts', __name__)

@receipts.route('/api/save-expense', methods=['POST'])
@login_required
def save_scanned_expense():
    data = request.get_json()
    try:
        new_expense = Expense(
            user_id=current_user.id,
            merchant=data.get('merchant', 'Unknown'),
            amount=float(data.get('amount', 0)),
            category=data.get('category', 'Other'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else datetime.now(),
            is_bill=data.get('is_bill', False),
            due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d') if data.get('due_date') else None,
            is_paid=data.get('is_paid', True)
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Expense/Bill saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@receipts.route('/receipts')
@login_required
def receipts_history():
    """Dedicated view for scanned receipts history"""
    from fintelligent.auth.models import Expense
    scanned_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('receipts_view.html', expenses=scanned_expenses)

@receipts.route('/api/delete-receipt/<int:id>', methods=['DELETE'])
@login_required
def delete_receipt(id):
    from fintelligent.auth.models import Expense
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receipt deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipts.route('/api/update-receipt/<int:id>', methods=['PUT'])
@login_required
def update_receipt(id):
    from fintelligent.auth.models import Expense
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    try:
        if 'merchant' in data: expense.merchant = data['merchant']
        if 'amount' in data: expense.amount = float(data['amount'])
        if 'category' in data: expense.category = data['category']
        if 'date' in data: expense.date = datetime.strptime(data['date'], '%Y-%m-%d')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receipt updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@receipts.route('/api/scan-receipt', methods=['POST'])
@login_required
def scan_receipt():
    # Manual tier check for JSON response
    if current_user.plan not in ['PRO', 'STUDENT']:
         return jsonify({
            'error': 'This feature requires a STUDENT or PRO subscription.',
            'solution': 'Upgrade your plan to use AI receipt scanning.'
        }), 403

    import groq
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({
            'error': 'Groq API Key not configured.',
            'solution': 'Please add GROQ_API_KEY to your .env file.'
        }), 503

    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            # Prepare image for Groq
            with open(filepath, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            client = groq.Groq(api_key=api_key)
            
            prompt = """
            Analyze this receipt/bill image (which may be handwritten) and extract the following details into a pure JSON object:
            - merchant: Name of the store, person, or cafe. If not readable, put "Unknown Merchant".
            - date: Date of the transaction in YYYY-MM-DD format based on the image text. If not found, output today's date.
            - amount: The total numerical amount float (e.g., 25.50). Ensure no currency symbols, just the number. If no number is found, return 0.0.
            
            Return ONLY a valid JSON string. Ensure keys are exactly 'merchant', 'date', and 'amount'.
            """
            
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.1,
            )
            
            raw_result = response.choices[0].message.content.strip()
            
            # Robust extraction of JSON from response
            json_match = re.search(r'\{.*\}', raw_result, re.DOTALL)
            if json_match:
                raw_json = json_match.group(0)
                data = json.loads(raw_json)
            else:
                raise ValueError("AI did not return valid JSON format.")
                
            if os.path.exists(filepath): os.remove(filepath)
            
            return jsonify({
                'success': True,
                'merchant': data.get('merchant', 'Unknown Merchant'),
                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'amount': float(data.get('amount', 0.0)),
                'raw_text': "(AI Vision Processed)"
            })
            
        except Exception as e:
            if os.path.exists(filepath): os.remove(filepath)
            return jsonify({'error': f"Processing Failed: {str(e)}"}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400
