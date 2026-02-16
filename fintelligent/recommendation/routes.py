from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_login import current_user, login_required
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime

recommendation = Blueprint('recommendation', __name__)

CSV_PATH = 'user_tax_history.csv'

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
    dashboard_data = get_dashboard_data(current_user.id)
    return render_template('dashboard.html', dashboard_data=dashboard_data)

@recommendation.route('/analytics', methods=['GET', 'POST'])
@login_required
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
                    
                    # Basic Validation
                    required_cols = ['transaction_id', 'date', 'category', 'amount']
                    if not all(col in user_df.columns for col in required_cols):
                        error = f"Invalid CSV format. Missing columns"
                    else:
                        # Preprocessing
                        user_df['date'] = pd.to_datetime(user_df['date'])
                        user_df['amount'] = pd.to_numeric(user_df['amount'])
                        
                        total_spending = user_df['amount'].sum()
                        user_income = 100000 
                        spending_rate = total_spending / user_income
                        category_totals = user_df.groupby('category')['amount'].sum().to_dict()
                        
                        user_df['month'] = user_df['date'].dt.strftime('%b %Y')
                        monthly_spending = user_df.groupby('month')['amount'].sum()
                        monthly_labels = monthly_spending.index.tolist()
                        monthly_data = monthly_spending.values.tolist()
                        
                        # PCA & KMeans Clustering
                        user_features = user_df.groupby('category')['amount'].agg(['mean', 'sum', 'count'])
                        n_clusters = min(len(user_features), 3)
                        pca_points, cluster_colors = [], ["#3b82f6", "#10b981", "#f59e0b"]
                        financial_category, category_color, category_icon = "Balanced Spender", "#3b82f6", "⚖️"
                        cluster_details = {}
                        
                        if n_clusters > 0:
                            scaler = StandardScaler()
                            features_scaled = scaler.fit_transform(user_features)
                            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                            clusters = kmeans.fit_predict(features_scaled)
                            pca = PCA(n_components=2)
                            pca_res = pca.fit_transform(features_scaled)
                            for i, (p, c) in enumerate(zip(pca_res, clusters)):
                                pca_points.append({'x': float(p[0]), 'y': float(p[1]), 'cluster': int(c)})
                            avg_spending = user_features['sum'].mean()
                            if avg_spending > 5000:
                                financial_category, category_color, category_icon = "High Velocity", "#ef4444", "🔥"
                            elif avg_spending < 2000:
                                financial_category, category_color, category_icon = "Frugal Master", "#10b981", "🌿"
                            
                            # Build detailed cluster breakdown
                            user_df['cluster'] = user_df['category'].map(dict(zip(user_features.index, clusters)))
                            
                            for cluster_id in range(n_clusters):
                                cluster_df = user_df[user_df['cluster'] == cluster_id]
                                if len(cluster_df) > 0:
                                    # Calculate statistics
                                    total_amount = float(cluster_df['amount'].sum())
                                    avg_amount = float(cluster_df['amount'].mean())
                                    count = len(cluster_df)
                                    frequency_score = count / len(user_df) * 10  # Normalized frequency
                                    spend_ratio = (total_amount / total_spending) * 100
                                    
                                    # Top categories
                                    top_categories = cluster_df.groupby('category')['amount'].sum().nlargest(3).index.tolist()
                                    
                                    # Top merchants
                                    top_merchants = cluster_df['merchant'].value_counts().head(3).index.tolist() if 'merchant' in cluster_df.columns else []
                                    
                                    # Payment methods
                                    payment_methods = {}
                                    if 'payment_method' in cluster_df.columns:
                                        payment_methods = cluster_df['payment_method'].value_counts().to_dict()
                                    else:
                                        # Mock payment methods if not available
                                        payment_methods = {
                                            'UPI': int(count * 0.4),
                                            'Debit Card': int(count * 0.35),
                                            'Credit Card': int(count * 0.25)
                                        }
                                    
                                    cluster_details[cluster_id] = {
                                        'count': count,
                                        'avg_amount': avg_amount,
                                        'total_amount': total_amount,
                                        'frequency_score': frequency_score,
                                        'spend_ratio': spend_ratio,
                                        'top_categories': top_categories,
                                        'top_merchants': top_merchants if top_merchants else ['Amazon', 'Swiggy', 'BigBasket'][:min(3, count)],
                                        'payment_methods': payment_methods
                                    }

                        health_score_data = {
                            'score': 85, 'level': 'Good', 'color': '#3b82f6', 
                            'message': 'Your financial health is strong based on this data.',
                            'factors': {}, 'recommendations': ["Keep it up!", "Review your top categories."]
                        }
                        
                        budget_limit = getattr(current_user, 'monthly_budget', 20000.0) or 20000.0
                        now = datetime.now()
                        spent_this_month = float(user_df[user_df['date'] >= now.replace(day=1, hour=0, minute=0, second=0)]['amount'].sum())
                        import calendar
                        forecast = (spent_this_month / max(1, now.day)) * calendar.monthrange(now.year, now.month)[1]
                        
                        dashboard_data = {
                            'financial_category': financial_category, 'category_color': category_color, 'category_icon': category_icon,
                            'total_spent': float(total_spending), 'category_distribution': {k: float(v) for k, v in category_totals.items()},
                            'monthly_trend': {'labels': monthly_labels, 'data': [float(v) for v in monthly_data]},
                            'budget': {
                                'limit': budget_limit, 'spent': spent_this_month, 'forecast': forecast, 
                                'status': 'healthy' if forecast < budget_limit else 'broke_alert', 
                                'days_remaining': max(0, 30-now.day)
                            },
                            'health_score': health_score_data, 'pca_points': pca_points, 
                            'cluster_details': cluster_details,
                            'insights': [f"Top category: {max(category_totals, key=category_totals.get)}", "Spending velocity is stable."],
                            'overspending_areas': {k: float(v) for k, v in category_totals.items() if v > 10000}
                        }

                except Exception as e:
                    error = f"Error processing file: {str(e)}"
    
    return render_template('analytics.html', error=error, dashboard_data=dashboard_data)