import sys
import os

# Dynamic venv path discovery for IDE Debuggers
def find_site_packages():
    root = os.path.dirname(os.path.abspath(__file__))
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

import warnings

# Suppress sklearn feature name warnings (harmless - occurs when using DataFrames)
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

from flask import Flask
from fintelligent.main.routes import main
from fintelligent.auth.routes import auth
from fintelligent.strategies.routes import strategies
from fintelligent.stocks.routes import stocks
from fintelligent.tax.routes import tax
from fintelligent.education.routes import education
from fintelligent.monitoring.routes import monitoring
from fintelligent.extensions import db, login_manager, csrf, limiter, talisman
# Import models to ensure they are registered
from fintelligent.auth.models import User
from fintelligent.gamification.models import GamificationProfile
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from flask import Blueprint, request, jsonify
import os
from fintelligent.recommendation.routes import recommendation
from fintelligent.cards.routes import cards
from fintelligent.gamification.routes import gamification
from fintelligent.statements.routes import statements

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-local-only-replace-in-prod')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'fintelligent.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf.init_app(app)
limiter.init_app(app)

# Talisman for security headers (content security policy)
# Allowing CDNs for FontAwesome and Chart.js
csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
        'https://kit.fontawesome.com',
        'https://cdnjs.cloudflare.com',
        '\'unsafe-inline\'' # Needed for some existing inline scripts
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://cdnjs.cloudflare.com',
        '\'unsafe-inline\''
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com',
        'https://ka-p.fontawesome.com',
        'https://cdnjs.cloudflare.com'
    ],
    'img-src': ['\'self\'', 'data:']
}
talisman.init_app(app, content_security_policy=csp)

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(strategies)
app.register_blueprint(stocks)
app.register_blueprint(tax)
app.register_blueprint(education)
app.register_blueprint(monitoring)
app.register_blueprint(recommendation)
app.register_blueprint(cards)
app.register_blueprint(gamification)
app.register_blueprint(statements)

from fintelligent.receipts.routes import receipts
app.register_blueprint(receipts)

from fintelligent.ai_coach.routes import ai_coach
app.register_blueprint(ai_coach)

# Initialize Flask-Login
login_manager.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Example: Load user history
df = pd.DataFrame([
    {'user_id': 1, 'income': 800000, 'invested_80c': 120000, 'premium_80d': 20000, 'home_principal': 50000, 'home_interest': 150000},
    {'user_id': 2, 'income': 600000, 'invested_80c': 80000, 'premium_80d': 25000, 'home_principal': 0, 'home_interest': 0},
    # ... more users
])

# Cluster users
features = ['income', 'invested_80c', 'premium_80d', 'home_principal', 'home_interest']
# Clustering
n_clusters = min(len(df), 3)  # Use fewer clusters if not enough data
if n_clusters > 1:
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df[features])
    df['cluster'] = kmeans.labels_
else:
    df['cluster'] = 0  # Single cluster if only one sample

# For a new user, find their cluster and recommend the average allocation
def recommend_allocation(user_input):
    # Convert to DataFrame to match the format used for fitting (avoids feature name warnings)
    user_vec = pd.DataFrame([{
        'income': user_input['income'],
        'invested_80c': user_input['invested_80c'],
        'premium_80d': user_input['premium_80d'],
        'home_principal': user_input['home_principal'],
        'home_interest': user_input['home_interest']
    }])
    cluster = kmeans.predict(user_vec[features])[0]
    cluster_df = df[df['cluster'] == cluster]
    avg_alloc = cluster_df[features].mean().to_dict()
    return avg_alloc

# Example usage:
user_input = {'income': 700000, 'invested_80c': 90000, 'premium_80d': 22000, 'home_principal': 20000, 'home_interest': 100000}
recommendation = recommend_allocation(user_input)
print(recommendation)

if __name__ == '__main__':
    import socket
    
    # Check if port is available, if not try alternative port
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    port = 5001
    if not is_port_available(port):
        print(f"Port {port} is in use. Trying alternative port...")
        port = 5002
        if not is_port_available(port):
            port = 5003
    
    print(f"Starting Flask app on port {port}")
    app.run(debug=True, port=port, host='0.0.0.0')
