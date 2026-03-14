import sqlite3
import os

db_path = os.path.join('instance', 'fintelligent.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}. Run the app to create it.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update User Table
cursor.execute("PRAGMA table_info(user)")
columns = [info[1] for info in cursor.fetchall()]

if 'plan' not in columns:
    print("Adding 'plan' column to user table...")
    cursor.execute("ALTER TABLE user ADD COLUMN plan VARCHAR(20) DEFAULT 'FREE'")

if 'subscription_expiry' not in columns:
    print("Adding 'subscription_expiry' column to user table...")
    cursor.execute("ALTER TABLE user ADD COLUMN subscription_expiry DATETIME")

# Create Transaction Table
print("Creating payment_transaction table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS payment_transaction (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    razorpay_order_id VARCHAR(100) UNIQUE NOT NULL,
    razorpay_payment_id VARCHAR(100) UNIQUE,
    razorpay_signature VARCHAR(200),
    amount FLOAT NOT NULL,
    plan VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
""")

conn.commit()
conn.close()
print("Subscription database update complete!")
