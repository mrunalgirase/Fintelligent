from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from fintelligent.utils.decorators import tier_required
from . import statements
import os
import pdfplumber
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def categorize_transaction(description, amount):
    """
    Categorizes a transaction based on its description.
    Student-focused keywords.
    """
    desc = description.lower()
    
    # Categories
    if any(k in desc for k in ['swiggy', 'zomato', 'pizza', 'burger', 'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'kfc', 'dominos', 'food', 'tea', 'chai', 'baker']):
        return 'Food & Dining'
    elif any(k in desc for k in ['uber', 'ola', 'rapido', 'metro', 'rail', 'irctc', 'train', 'bus', 'fuel', 'petrol', 'pump', 'shell', 'hpcl', 'bpcl']):
        return 'Transport'
    elif any(k in desc for k in ['amazon', 'flipkart', 'myntra', 'ajio', 'zara', 'h&m', 'shopping', 'store', 'mall', 'mart', 'retail', 'clothing', 'nike', 'adidas']):
        return 'Shopping'
    elif any(k in desc for k in ['netflix', 'prime', 'spotify', 'youtube', 'movie', 'cinema', 'theatre', 'bookmyshow', 'steam', 'playstation', 'game', 'entertainment', 'hotstar', 'sony']):
        return 'Entertainment'
    elif any(k in desc for k in ['university', 'college', 'school', 'fee', 'tuition', 'book', 'stationery', 'course', 'udemy', 'coursera', 'learning', 'exam']):
        return 'Education'
    elif any(k in desc for k in ['recharge', 'jio', 'airtel', 'vi', 'vodafone', 'bsnl', 'broadband', 'wifi', 'bill']):
        return 'Utilities'
    elif any(k in desc for k in ['upi', 'transfer', 'neft', 'imps', 'rtgs', 'sent to']):
        return 'Transfers/UPI'
    else:
        return 'Others'

def get_student_insights(category_totals, total_debit):
    """
    Generates fun, student-oriented insights based on spending.
    """
    insights = []
    
    # Sort categories by spend
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    if not sorted_cats:
        return insights
        
    top_cat, top_amount = sorted_cats[0]
    
    if total_debit > 0:
        top_pct = (top_amount / total_debit) * 100
    else:
        top_pct = 0
        
    # Insight 1: Vibe Check
    if top_cat == 'Food & Dining':
        insights.append({
            'title': 'Certified Foodie 🍔',
            'text': f"Wow! You spent {top_pct:.1f}% of your money on food. Maybe try the college canteen more often?",
            'icon': 'fa-utensils',
            'color': 'var(--warning)'
        })
    elif top_cat == 'Shopping':
        insights.append({
            'title': 'Retail Therapy 🛍️',
            'text': f"Looks like you treated yourself! {top_pct:.1f}% went to shopping. Hope you got some good deals!",
            'icon': 'fa-bag-shopping',
            'color': 'var(--primary)'
        })
    elif top_cat == 'Entertainment':
        insights.append({
            'title': 'Living the Life 🎬',
            'text': f"Netflix & Chill? {top_pct:.1f}% spent on entertainment. Don't forget to study!",
            'icon': 'fa-film',
            'color': 'var(--danger)'
        })
    elif top_cat == 'Transport':
        insights.append({
            'title': 'On the Move 🚕',
            'text': f"You're going places! {top_pct:.1f}% spent on travel.",
            'icon': 'fa-car',
            'color': 'var(--secondary)'
        })
        
    # Insight 2: Saving Tip
    if 'Transfers/UPI' in category_totals and category_totals['Transfers/UPI'] > (total_debit * 0.5):
        insights.append({
            'title': 'UPI Warrior 💸',
            'text': "Heavy UPI usage detected. Small transfers add up quickly!",
            'icon': 'fa-mobile-screen',
            'color': 'var(--accent)'
        })
        
    return insights

def parse_bank_statement(filepath):
    """
    Parses a bank statement PDF and extracts transaction details.
    """
    transactions = []
    
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    # Check if table has relevant headers
                    # Heuristic: look for Date, Credit, Debit, Balance in the first row
                    if not table:
                        continue
                        
                    header = [str(col).lower() if col else '' for col in table[0]]
                    
                    # Basic validation of header
                    if any('date' in h for h in header) and \
                       (any('credit' in h for h in header) or any('debit' in h for h in header)):
                        
                        # Identify column indices
                        date_idx = next((i for i, h in enumerate(header) if 'date' in h), -1)
                        desc_idx = next((i for i, h in enumerate(header) if 'particulars' in h or 'description' in h or 'details' in h or 'narration' in h or 'transaction' in h), -1)
                        ref_idx = next((i for i, h in enumerate(header) if 'ref' in h or 'cheque' in h), -1)
                        credit_idx = next((i for i, h in enumerate(header) if 'credit' in h or 'deposit' in h), -1)
                        debit_idx = next((i for i, h in enumerate(header) if 'debit' in h or 'withdrawal' in h), -1)
                        balance_idx = next((i for i, h in enumerate(header) if 'balance' in h), -1)
                        
                        # Process rows (skip header)
                        for row in table[1:]:
                            # Skip empty rows or rows that look like summaries/page footers
                            if not row or all(c is None or c == '' for c in row):
                                continue
                                
                            try:
                                txn = {
                                    'date': row[date_idx].replace('\n', ' ') if date_idx != -1 and row[date_idx] else '',
                                    'description': row[desc_idx].replace('\n', ' ') if desc_idx != -1 and row[desc_idx] else '',
                                    'ref_no': row[ref_idx].replace('\n', ' ') if ref_idx != -1 and row[ref_idx] else '',
                                    'credit': row[credit_idx].replace('\n', '').replace(',', '') if credit_idx != -1 and row[credit_idx] else '0',
                                    'debit': row[debit_idx].replace('\n', '').replace(',', '') if debit_idx != -1 and row[debit_idx] else '0',
                                    'balance': row[balance_idx].replace('\n', '').replace(',', '') if balance_idx != -1 and row[balance_idx] else '0'
                                }
                                
                                # Basic cleanup and filtering
                                if txn['date']: # Only add if date is present
                                    transactions.append(txn)
                            except IndexError:
                                continue

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

    return transactions

@statements.route('/statements', methods=['GET', 'POST'])
@login_required
@tier_required('PRO')
def index():
    analysis = None
    
    if request.method == 'POST':
        if 'statement' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['statement']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
                file.save(temp.name)
                temp_path = temp.name
                
            try:
                # Parse
                txns = parse_bank_statement(temp_path)
                
                if not txns:
                    flash('Could not extract transactions. Please ensure the PDF is a valid bank statement.', 'error')
                else:
                    total_credit_val = sum(float(t['credit']) for t in txns if t['credit'].replace('.', '', 1).isdigit())
                    total_debit_val = sum(float(t['debit']) for t in txns if t['debit'].replace('.', '', 1).isdigit())
                    net_flow_val = total_credit_val - total_debit_val
                    
                    # 1. Categorize Debits
                    category_totals = {}
                    processed_txns = []
                    
                    for t in txns:
                        # Convert values
                        try:
                            debit_val = float(t['debit']) if t['debit'].replace('.', '', 1).isdigit() else 0.0
                        except:
                            debit_val = 0.0
                            
                        # Assign category for all, but only sum positive debits for spending chart
                        cat = categorize_transaction(t['description'], debit_val)
                        t['category'] = cat
                        
                        if debit_val > 0:
                            category_totals[cat] = category_totals.get(cat, 0) + debit_val
                            
                        processed_txns.append(t)
                        
                    # 2. Prepare Chart Data
                    chart_labels = list(category_totals.keys())
                    chart_values = [round(val, 2) for val in category_totals.values()]
                    
                    # 3. Get Insights
                    insights = get_student_insights(category_totals, total_debit_val)
                    
                    analysis = {
                        'transactions': processed_txns,
                        'total_credit': f"{total_credit_val:,.2f}",
                        'total_debit': f"{total_debit_val:,.2f}",
                        'net_flow_val': net_flow_val,
                        'net_flow': f"{net_flow_val:,.2f}",
                        'transaction_count': len(txns),
                        'chart_labels': chart_labels,
                        'chart_values': chart_values,
                        'insights': insights
                    }
                    flash('Statement analyzed successfully!', 'success')
                    
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            flash('Invalid file type. Please upload a PDF.', 'error')

    return render_template('statements.html', analysis=analysis)
