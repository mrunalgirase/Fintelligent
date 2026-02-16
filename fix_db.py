from app import app, db
from fintelligent.auth.models import User
from fintelligent.gamification.models import GamificationProfile, UserBadge, UserChallenge

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # Optional: Debug check
    import sqlite3
    conn = sqlite3.connect('instance/fintelligent.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", [t[0] for t in tables])
    conn.close()
