from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from flask_login import current_user, login_required
from fintelligent.utils.decorators import tier_required
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
import json
import base64
import re
from fintelligent.extensions import db
from fintelligent.auth.models import Expense

recommendation = Blueprint('recommendation', __name__)

CSV_PATH = 'user_tax_history.csv'


def build_analytics_from_db(user_id):
    """Build analytics page data from stored expenses (no CSV upload required)."""
    from fintelligent.main.routes import get_dashboard_data
    from fintelligent.utils.analytics_engine import cluster_stats_to_details

    base = get_dashboard_data(user_id)
    if not base.get('has_data'):
        return None

    cluster_details, cluster_list = cluster_stats_to_details(
        base.get('cluster_stats', {}),
        base.get('n_clusters', 0),
    )
    cat_dist = base.get('category_distribution', {})
    overspending = {
        str(k): float(v) for k, v in cat_dist.items() if float(v) > 5000
    }
    string_insights = [i['message'] for i in base.get('insights', []) if i.get('message')]

    return {
        'financial_category': 'Balanced Spender',
        'category_color': '#3b82f6',
        'category_icon': '⚖️',
        'total_spent': base['total_spent'],
        'transaction_count': base['transaction_count'],
        'category_distribution': cat_dist,
        'monthly_trend': base['monthly_trend'],
        'budget': base['budget'],
        'health_score': base['health_score'],
        'pca_points': base.get('pca_points', []),
        'cluster_details': cluster_details,
        'cluster_list': cluster_list,
        'cluster_colors': base.get('cluster_colors', []),
        'n_clusters': base.get('n_clusters', 0),
        'insights': string_insights,
        'overspending_areas': overspending,
        'source': 'database',
    }

def save_user_tax_data(user_id, income, invested_80c, premium_80d, home_principal, home_interest):
    # Append to CSV
    df = pd.DataFrame([{
        'user_id': user_id,
        'income': income,
        'invested_80c': invested_80c,
        'premium_80d': premium_80d,
        'home_principal': home_principal,
        'home_interest': home_interest
    }])
    if not os.path.exists(CSV_PATH):
        df.to_csv(CSV_PATH, index=False)
    else:
        df.to_csv(CSV_PATH, mode='a', header=False, index=False)

def get_regression_recommendation(user_input):
    if not os.path.exists(CSV_PATH):
        return None  # Not enough data yet
    df = pd.read_csv(CSV_PATH)
    features = ['income', 'premium_80d', 'home_principal', 'home_interest']
    X = df[features]
    recommendations = {}
    for target in ['invested_80c', 'premium_80d', 'home_principal', 'home_interest']:
        if target in df.columns:
            y = df[target]
            model = LinearRegression()
            model.fit(X, y)
            pred = model.predict([[user_input['income'], user_input['premium_80d'], user_input['home_principal'], user_input['home_interest']]])[0]
            recommendations[target] = max(0, int(pred))
    return recommendations

@recommendation.route('/dashboard')
@login_required
def financial_dashboard():
    """High-level summary dashboard using database data"""
    from fintelligent.main.routes import get_dashboard_data
    from fintelligent.auth.models import Expense
    from fintelligent.gamification.models import GamificationProfile
    from fintelligent.utils.analytics_engine import get_market_snapshot

    dashboard_data = get_dashboard_data(current_user.id)
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.date.desc()
    ).limit(10).all()
    profile = GamificationProfile.query.filter_by(user_id=current_user.id).first()
    market = get_market_snapshot()

    return render_template(
        'dashboard.html',
        dashboard_data=dashboard_data,
        expenses=expenses,
        streak=profile.streak_count if profile else 0,
        market=market,
    )

def _normalize_csv_columns(df):
    """Normalize column names for flexible CSV upload (date, category, amount required)."""
    col_map = {}
    for c in df.columns:
        lower = str(c).strip().lower()
        if lower in ('date', 'transaction_date', 'txn_date'):
            col_map[c] = 'date'
        elif lower in ('category', 'categories', 'type', 'transaction_type'):
            col_map[c] = 'category'
        elif lower in ('amount', 'debit', 'credit', 'value', 'transaction_amount'):
            col_map[c] = 'amount'
        elif lower in ('merchant', 'description', 'details', 'narration', 'payee'):
            col_map[c] = 'merchant'
        elif lower in ('transaction_id', 'id', 'ref', 'reference'):
            col_map[c] = 'transaction_id'
    df = df.rename(columns=col_map)
    if 'merchant' not in df.columns:
        df['merchant'] = 'Unknown'
    if 'transaction_id' not in df.columns:
        df['transaction_id'] = range(len(df))
    return df


@recommendation.route('/analytics', methods=['GET', 'POST'])
@login_required
@tier_required(['STUDENT', 'PRO'])
def financial_analytics():
    """Deep dive analytics using uploaded CSV data"""
    error = None
    dashboard_data = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "Please select a file to upload"
        else:
            file = request.files['file']
            if file.filename == '':
                error = "No file selected"
            else:
                try:
                    user_df = pd.read_csv(file)
                    user_df = _normalize_csv_columns(user_df)
                    
                    required_cols = ['date', 'category', 'amount']
                    if not all(col in user_df.columns for col in required_cols):
                        error = "Invalid CSV format. Required columns: date, category, amount (or similar names like transaction_date, type, debit)."
                    else:
                        # Preprocessing
                        user_df['date'] = pd.to_datetime(user_df['date'], errors='coerce')
                        user_df = user_df.dropna(subset=['date'])
                        user_df['amount'] = pd.to_numeric(user_df['amount'], errors='coerce').fillna(0)
                        user_df = user_df[user_df['amount'] != 0]
                        if len(user_df) == 0:
                            error = "No valid rows found. Ensure date and amount columns have valid values."
                        else:
                            total_spending = float(user_df['amount'].sum())
                            category_totals = user_df.groupby('category')['amount'].sum().to_dict()
                            
                            user_df['month'] = user_df['date'].dt.strftime('%b %Y')
                            monthly_spending = user_df.groupby('month')['amount'].sum()
                            monthly_labels = list(monthly_spending.index)
                            _vals = np.atleast_1d(np.asarray(monthly_spending.values)).flatten()
                            monthly_data = [float(v) for v in _vals]
                            
                            # PCA & KMeans on category-level features
                            user_features = user_df.groupby('category')['amount'].agg(['mean', 'sum', 'count'])
                            n_categories = len(user_features)
                            n_clusters = min(max(1, n_categories), 6)
                            pca_points = []
                            cluster_names = ["Dining & Food", "Shopping", "Grocery & Essentials", "Transport", "Entertainment", "Others"]
                            cluster_colors = ["#f43f5e", "#8b5cf6", "#10b981", "#3b82f6", "#f59e0b", "#64748b"]
                            cluster_icons = ["fa-utensils", "fa-bag-shopping", "fa-cart-shopping", "fa-bus", "fa-film", "fa-microchip"]
                            financial_category, category_color, category_icon = "Balanced Spender", "#3b82f6", "⚖️"
                            cluster_details = {}
                            
                            scaler = StandardScaler()
                            features_scaled = scaler.fit_transform(user_features)
                            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                            clusters = np.atleast_1d(np.asarray(kmeans.fit_predict(features_scaled)).flatten())
                            if n_categories >= 2:
                                pca = PCA(n_components=min(2, n_categories - 1))
                                pca_res = pca.fit_transform(features_scaled)
                                if pca_res.shape[1] == 1:
                                    pca_res = np.column_stack([pca_res[:, 0], np.zeros(len(pca_res))])
                            else:
                                pca_res = np.array([[0.0, 0.0]])
                            for i, (p, c) in enumerate(zip(pca_res, clusters)):
                                pca_points.append({
                                    'x': float(p[0]),
                                    'y': float(p[1]) if len(p) > 1 else 0.0,
                                    'cluster': int(c),
                                    'label': str(user_features.index[i])
                                })
                            
                            # Classification logic: Spender, Saver, or Investor
                            investment_cats = ['Investment', 'Stocks', 'SIP', 'Mutual Fund', 'Gold', 'Savings']
                            discretionary_cats = ['Food', 'Dining', 'Shopping', 'Entertainment', 'OTT', 'Travel']
                            
                            investment_total = sum(float(v) for k, v in category_totals.items() if any(ich in str(k) for ich in investment_cats))
                            discretionary_total = sum(float(v) for k, v in category_totals.items() if any(dch in str(k) for dch in discretionary_cats))
                            
                            if investment_total > (total_spending * 0.3):
                                financial_category, category_color, category_icon = "Elite Investor", "#8b5cf6", "🚀"
                            elif discretionary_total > (total_spending * 0.5):
                                financial_category, category_color, category_icon = "Active Spender", "#f43f5e", "🛍️"
                            else:
                                financial_category, category_color, category_icon = "Disciplined Saver", "#10b981", "🛡️"
                            
                            category_to_cluster = dict(zip(list(user_features.index), clusters))
                            user_df['cluster'] = user_df['category'].map(category_to_cluster)
                            
                            # Ensure every cluster 0..n_clusters-1 has an entry (so all clusters appear in UI)
                            for cluster_id in range(n_clusters):
                                cluster_df = user_df[user_df['cluster'] == cluster_id]
                                if len(cluster_df) > 0:
                                    total_amount = float(cluster_df['amount'].sum())
                                    avg_amount = float(cluster_df['amount'].mean())
                                    count = len(cluster_df)
                                    frequency_score = min(10.0, (count / len(user_df)) * 15)
                                    spend_ratio = (total_amount / total_spending) * 100
                                    top_categories = [str(x) for x in list(cluster_df.groupby('category')['amount'].sum().nlargest(3).index)]
                                    merchants = [str(x) for x in (cluster_df['merchant'].value_counts().head(3).index.tolist() if 'merchant' in cluster_df.columns else ["—"])]
                                    cluster_details[cluster_id] = {
                                        'name': cluster_names[cluster_id] if cluster_id < len(cluster_names) else f"Cluster {cluster_id + 1}",
                                        'color': cluster_colors[cluster_id] if cluster_id < len(cluster_colors) else "#64748b",
                                        'icon': cluster_icons[cluster_id] if cluster_id < len(cluster_icons) else "fa-cube",
                                        'count': count,
                                        'avg_amount': avg_amount,
                                        'total_amount': total_amount,
                                        'frequency_score': frequency_score,
                                        'spend_ratio': spend_ratio,
                                        'top_categories': top_categories,
                                        'top_merchants': merchants,
                                        'payment_methods': cluster_df['payment_method'].value_counts().head(3).to_dict() if 'payment_method' in cluster_df.columns else {"—": count}
                                    }
                                else:
                                    cluster_details[cluster_id] = {
                                        'name': cluster_names[cluster_id] if cluster_id < len(cluster_names) else f"Cluster {cluster_id + 1}",
                                        'color': cluster_colors[cluster_id] if cluster_id < len(cluster_colors) else "#64748b",
                                        'icon': cluster_icons[cluster_id] if cluster_id < len(cluster_icons) else "fa-cube",
                                        'count': 0,
                                        'avg_amount': 0.0,
                                        'total_amount': 0.0,
                                        'frequency_score': 0.0,
                                        'spend_ratio': 0.0,
                                        'top_categories': [],
                                        'primary_categories': [],
                                        'top_merchants': ["—"],
                                        'payment_methods': {}
                                    }
                            
                            # Assign each category to exactly one cluster (where it has highest share) — no repetition
                            category_per_cluster = {cid: [] for cid in range(n_clusters)}
                            for cat in category_totals:
                                amounts_per_cluster = {}
                                for cid in range(n_clusters):
                                    cluster_df = user_df[user_df['cluster'] == cid]
                                    amt = float(cluster_df[cluster_df['category'] == cat]['amount'].sum()) if len(cluster_df) > 0 else 0
                                    amounts_per_cluster[cid] = amt
                                best_cluster = max(amounts_per_cluster, key=amounts_per_cluster.get)
                                if amounts_per_cluster[best_cluster] > 0:
                                    category_per_cluster[best_cluster].append(cat)
                            for cid in range(n_clusters):
                                cluster_details[cid]['primary_categories'] = category_per_cluster.get(cid, [])
                            
                            health_score = min(100, max(40, 70 + (n_clusters * 3) - int(total_spending / 15000)))
                            health_score_data = {
                                'score': int(health_score),
                                'level': 'Elite' if health_score > 90 else 'Prime' if health_score > 70 else 'Standard',
                                'color': '#10b981' if health_score > 70 else '#f59e0b' if health_score > 50 else '#ef4444',
                                'message': "Your financial genome shows stable resource allocation." if health_score > 50 else "Neural analysis suggests budget optimization."
                            }
                            
                            budget_limit = getattr(current_user, 'monthly_budget', 20000.0) or 20000.0
                            now = datetime.now()
                            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                            spent_this_month = float(user_df.loc[user_df['date'] >= first_day, 'amount'].sum())
                            import calendar
                            days_in_month = calendar.monthrange(now.year, now.month)[1]
                            forecast = (spent_this_month / max(1, now.day)) * days_in_month
                            
                            top_cat = max(category_totals, key=category_totals.get) if category_totals else "N/A"
                            top_cat_val = float(category_totals.get(top_cat, 0)) if category_totals else 0
                            insights = list([
                                f"Top spending category: {top_cat} (₹{top_cat_val:,.0f}).",
                                "Spending velocity is stable." if total_spending < budget_limit * 1.2 else "Consider reducing high-velocity categories.",
                                f"{n_clusters} behavioral cluster(s) detected from {n_categories} categories."
                            ])
                            overspending_areas = dict((str(k), float(v)) for k, v in category_totals.items() if float(v) > 10000)
                            
                            # Ensure ALL template/serialized data is native Python (no numpy/pandas)
                            def _to_native(val):
                                if isinstance(val, (list, tuple)):
                                    return [_to_native(x) for x in val]
                                if isinstance(val, dict):
                                    return {str(k): _to_native(v) for k, v in val.items()}
                                if hasattr(val, 'item'):  # numpy scalar
                                    return val.item()
                                if hasattr(val, 'tolist'):
                                    return val.tolist()
                                return val

                            cluster_list = []
                            cluster_details_safe = {}
                            for cid, det in sorted(cluster_details.items()):
                                tc = det.get('top_categories')
                                tm = det.get('top_merchants')
                                pc = det.get('primary_categories', [])
                                safe_det = {
                                    'name': str(det.get('name', '')),
                                    'color': str(det.get('color', '#64748b')),
                                    'icon': str(det.get('icon', 'fa-cube')),
                                    'count': int(det.get('count', 0)),
                                    'avg_amount': float(det.get('avg_amount', 0)),
                                    'total_amount': float(det.get('total_amount', 0)),
                                    'frequency_score': float(det.get('frequency_score', 0)),
                                    'spend_ratio': float(det.get('spend_ratio', 0)),
                                    'top_categories': [str(x) for x in (list(tc) if isinstance(tc, (list, tuple)) else (list(tc) if tc is not None and hasattr(tc, '__iter__') and not isinstance(tc, str) else []))],
                                    'primary_categories': [str(x) for x in (list(pc) if isinstance(pc, (list, tuple)) else (list(pc) if pc is not None and hasattr(pc, '__iter__') and not isinstance(pc, str) else []))],
                                    'top_merchants': [str(x) for x in (list(tm) if isinstance(tm, (list, tuple)) else (list(tm) if tm is not None and hasattr(tm, '__iter__') and not isinstance(tm, str) else ['—']))],
                                    'payment_methods': _to_native(det.get('payment_methods', {})) if isinstance(det.get('payment_methods'), dict) else {},
                                }
                                cluster_list.append((int(cid), safe_det))
                                cluster_details_safe[int(cid)] = safe_det

                            dashboard_data = {
                                'financial_category': str(financial_category),
                                'category_color': str(category_color),
                                'category_icon': str(category_icon),
                                'total_spent': float(total_spending),
                                'category_distribution': dict((str(k), float(v)) for k, v in category_totals.items()),
                                'monthly_trend': {'labels': [str(x) for x in monthly_labels], 'data': [float(x) for x in monthly_data]},
                                'budget': {
                                    'limit': float(budget_limit),
                                    'spent': float(spent_this_month),
                                    'forecast': float(forecast),
                                    'status': 'healthy' if forecast < budget_limit else 'broke_alert',
                                    'days_remaining': max(0, days_in_month - now.day)
                                },
                                'health_score': {
                                    'score': int(health_score_data.get('score', 0)),
                                    'level': str(health_score_data.get('level', '')),
                                    'color': str(health_score_data.get('color', '#10b981')),
                                    'message': str(health_score_data.get('message', '')),
                                },
                                'pca_points': [{'x': float(p['x']), 'y': float(p['y']), 'cluster': int(p['cluster']), 'label': str(p.get('label', ''))} for p in pca_points],
                                'cluster_details': cluster_details_safe,
                                'cluster_list': cluster_list,
                                'cluster_colors': [str(c) for c in cluster_colors[:n_clusters]],
                                'n_clusters': int(n_clusters),
                                'insights': [str(s) for s in (insights if isinstance(insights, (list, tuple)) else [])],
                                'overspending_areas': dict((str(k), float(v)) for k, v in overspending_areas.items()),
                                'transaction_count': int(len(user_df)),
                                'source': 'csv_upload',
                                'transactions_sample': [
                                    {
                                        'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                                        'category': str(row['category']),
                                        'amount': float(row['amount']),
                                        'merchant': str(row.get('merchant', 'Unknown')),
                                    }
                                    for _, row in user_df.sort_values('date', ascending=False).head(25).iterrows()
                                ],
                            }

                            # Persist CSV rows for AI Coach & dashboard (replace prior CSV upload)
                            Expense.query.filter_by(
                                user_id=current_user.id, source='csv_upload'
                            ).delete()
                            for _, row in user_df.iterrows():
                                try:
                                    tx_date = row['date']
                                    if pd.isna(tx_date):
                                        tx_date = datetime.now()
                                except Exception:
                                    tx_date = datetime.now()
                                db.session.add(Expense(
                                    user_id=current_user.id,
                                    merchant=str(row.get('merchant', 'Unknown'))[:200],
                                    amount=float(row['amount']),
                                    category=str(row['category'])[:100],
                                    date=tx_date,
                                    source='csv_upload',
                                ))
                            db.session.commit()

                            session['analytics_data'] = dashboard_data
                            flash("Neural Synthesis Complete! Redirecting to behavioral clusters.", "success")
                            return redirect(url_for('recommendation.all_clusters'))

                except Exception as e:
                    db.session.rollback()
                    error = f"Error processing file: {str(e)}"

    dashboard_data = session.get('analytics_data') or build_analytics_from_db(current_user.id)
    return render_template('analytics.html', error=error, dashboard_data=dashboard_data)

@recommendation.route('/analytics/clusters')
@login_required
@tier_required(['STUDENT', 'PRO'])
def all_clusters():
    """Detailed view of behavioral clusters after synthesis"""
    dashboard_data = session.get('analytics_data')
    if not dashboard_data:
        flash("Please upload a CSV file to generate neural analytics.", "info")
        return redirect(url_for('recommendation.financial_analytics'))
    
    return render_template('all_clusters.html', dashboard_data=dashboard_data, now=datetime.now())

@recommendation.route('/api/analytics/bank-statement', methods=['POST'])
@login_required
@tier_required(['STUDENT', 'PRO'])
def analyze_bank_statement():
    """Process bank statement image/PDF and extract insights"""
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({'error': 'Groq API Key missing'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    import groq
    try:
        # Read and encode image
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        client = groq.Groq(api_key=api_key)
        
        prompt = """
        ACT AS A PROFESSIONAL FINANCIAL ANALYST. Analyze this SBI Bank Statement image.
        Extract the transactions into a JSON array. 
        Each object MUST have:
        - date: YYYY-MM-DD
        - description: Clean merchant/payment name
        - amount: Float (Debit value)
        - category: One of [Food, Shopping, Travel, Rent, Utilities, Entertainment, Investment, Others]
        - type: 'DEBIT' or 'CREDIT'
        
        ONLY return the JSON array. Do not include markdown or explanations.
        """
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ],
            temperature=0.1,
        )
        
        raw_result = response.choices[0].message.content.strip()
        json_match = re.search(r'\[.*\]', raw_result, re.DOTALL)
        if not json_match:
             raise ValueError("No transaction data found in AI response")
        
        transactions = json.loads(json_match.group(0))
        
        # Save to DB and prepare chart data
        saved_count = 0
        total_debit = 0
        category_map = {}
        
        for tx in transactions:
            if tx.get('type') == 'DEBIT':
                amount = float(tx.get('amount', 0))
                total_debit += amount
                cat = tx.get('category', 'Others')
                category_map[cat] = category_map.get(cat, 0) + amount
                
                # Save to Expense model for AI Coach
                try:
                    dt = datetime.strptime(tx.get('date'), '%Y-%m-%d')
                except:
                    dt = datetime.now()

                expense = Expense(
                    user_id=current_user.id,
                    merchant=tx.get('description', 'Unknown'),
                    amount=amount,
                    category=cat,
                    date=dt,
                    source='bank_statement'
                )
                db.session.add(expense)
                saved_count += 1
        
        db.session.commit()
        
        statement_data = {
            'transactions': transactions,
            'summary': {
                'total_debit': total_debit,
                'count': saved_count,
                'categories': category_map
            },
            'insights': [
                f"Extracted {saved_count} transactions.",
                f"Peak spending in {max(category_map, key=category_map.get) if category_map else 'N/A'}.",
                "Data synchronized with AI Chat."
            ]
        }
        
        # Save to session for the new dedicated results page
        session['statement_data'] = statement_data
        
        return jsonify({
            'success': True,
            'redirect': url_for('recommendation.statement_results')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"AI Analysis Error: {str(e)}"}), 500

@recommendation.route('/analytics/statement', methods=['GET'])
@login_required
@tier_required(['STUDENT', 'PRO'])
def statement_results():
    statement_data = session.get('statement_data')
    if not statement_data:
        flash("Please upload a bank statement first.", "info")
        return redirect(url_for('recommendation.financial_analytics'))
    
    # Generate Advanced AI Tips
    summary = statement_data['summary']
    cat_map = summary['categories']
    total = summary['total_debit']
    
    ai_tips = []
    if total > 0:
        top_cat = max(cat_map, key=cat_map.get) if cat_map else None
        if top_cat:
            ai_tips.append({
                "icon": "fa-bullseye",
                "color": "#ef4444",
                "title": "High Burn Rate Detected",
                "text": f"Your highest expenditure was in <strong>{top_cat}</strong> (₹{cat_map[top_cat]:,.2f}). Standard protocol suggests capping this category."
            })
        
        if cat_map.get('Food', 0) / total > 0.3:
            ai_tips.append({
                "icon": "fa-utensils",
                "color": "#f59e0b",
                "title": "Dining Anomaly",
                "text": "Food expenses exceed 30% of total burn. We recommend substituting 3 weekly restaurant visits with home cooking to recover capital."
            })
        elif cat_map.get('Shopping', 0) / total > 0.2:
            ai_tips.append({
                "icon": "fa-bag-shopping",
                "color": "#ec4899",
                "title": "Retail Dependency",
                "text": "Frequent retail shopping detected. Enforce a 48-hour neural cooling off period before non-essential checkout."
            })
            
        if 'Investment' not in cat_map or (cat_map.get('Investment', 0) < total * 0.1):
            ai_tips.append({
                "icon": "fa-seedling",
                "color": "#10b981",
                "title": "Wealth Deficit",
                "text": "Your investment allocations are critically low (<10%). Automate SIPs to ensure compounding capital generation."
            })

    statement_data['ai_tips'] = ai_tips
            
    return render_template('statement_results.html', statement_data=statement_data, now=datetime.now())
@recommendation.route('/api/analytics/monthly-summary', methods=['GET'])
@login_required
def get_monthly_summary():
    """Get aggregated monthly spending from DB"""
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    if not expenses:
        return jsonify({'message': 'No data available', 'monthly_data': {}, 'total': 0})

    data_list = []
    for e in expenses:
        data_list.append({
            'date': e.date,
            'amount': e.amount,
            'category': e.category
        })
    df = pd.DataFrame(data_list)
    
    df['month'] = df['date'].dt.strftime('%b %Y')
    monthly_grouped = df.groupby('month')['amount'].sum().to_dict()
    
    return jsonify({
        'monthly_data': monthly_grouped,
        'total': float(df['amount'].sum())
    })

@recommendation.route('/api/analytics/export-csv')
@login_required
def export_csv():
    """Export user expenses to CSV for Power BI consumption"""
    from flask import make_response
    import io
    
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    if not expenses:
        # Return empty CSV with headers
        output = "date,merchant,amount,category,source\n"
    else:
        df = pd.DataFrame([{
            'date': e.date.strftime('%Y-%m-%d'),
            'merchant': e.merchant,
            'amount': e.amount,
            'category': e.category,
            'source': e.source
        } for e in expenses])
        output = df.to_csv(index=False)
    
    response = make_response(output)
    response.headers["Content-Disposition"] = "attachment; filename=fintelligent_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response