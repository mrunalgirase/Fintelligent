import os
import sys
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
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

import pytesseract
from PIL import Image
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

def extract_amount(text):
    lines = text.split('\n')
    amounts = []
    for line in lines:
        if any(keyword in line.lower() for keyword in ['total', 'amount', 'pay', 'due']):
             matches = re.findall(r'(\d+[,\d]*\.\d{2})', line)
             if matches:
                 amounts.extend([float(m.replace(',', '')) for m in matches])
    if not amounts:
        matches = re.findall(r'(\d+[,\d]*\.\d{2})', text)
        amounts = [float(m.replace(',', '')) for m in matches]
    if amounts:
        return max(amounts)
    return 0.0

def extract_date(text):
    date_patterns = [
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return datetime.now().strftime('%Y-%m-%d')

def extract_merchant(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        if lines[0].lower() in ['receipt', 'tax invoice', 'invoice', 'welcome']:
            return lines[1] if len(lines) > 1 else "Unknown Merchant"
        return lines[0]
    return "Unknown Merchant"


@receipts.route('/receipts')
@login_required
def receipts_history():
    """Dedicated view for scanned receipts history"""
    from fintelligent.auth.models import Expense
    scanned_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('receipts_view.html', expenses=scanned_expenses)

def configure_tesseract():
    common_paths = [
        '/opt/homebrew/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/usr/bin/tesseract'
    ]
    import subprocess
    try:
        subprocess.run(['tesseract', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True 
    except FileNotFoundError:
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
    return False

TESSERACT_AVAILABLE = configure_tesseract()

@receipts.route('/api/scan-receipt', methods=['POST'])
@login_required
def scan_receipt():
    if not current_user.is_premium:
        return jsonify({
            'error': 'Premium Feature',
            'solution': 'Scan Receipt is a Pro feature. Upgrade to unlock!'
        }), 403

    global TESSERACT_AVAILABLE
    if not TESSERACT_AVAILABLE:
        if configure_tesseract():
            TESSERACT_AVAILABLE = True
        else:
            return jsonify({
                'error': 'Tesseract OCR engine not found.',
                'solution': 'Please install it using: brew install tesseract'
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
            text = pytesseract.image_to_string(Image.open(filepath))
            amount = extract_amount(text)
            date = extract_date(text)
            merchant = extract_merchant(text)
            os.remove(filepath)
            return jsonify({
                'success': True,
                'merchant': merchant,
                'date': date,
                'amount': amount,
                'raw_text': text[:200] + '...'
            })
        except pytesseract.TesseractNotFoundError:
            return jsonify({
                'error': 'Tesseract OCR binary not found in your system.',
                'solution': 'Run "brew install tesseract" and restart the app.'
            }), 503
        except Exception as e:
            if os.path.exists(filepath): os.remove(filepath)
            return jsonify({'error': f"OCR Processing Failed: {str(e)}"}), 500
    return jsonify({'error': 'Invalid file type'}), 400
