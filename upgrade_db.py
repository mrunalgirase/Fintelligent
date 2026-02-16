import sqlite3
import os
import random
import string

db_path = os.path.join('instance', 'fintelligent.db')

def generate_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}. Run the app to create it.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check columns
cursor.execute("PRAGMA table_info(user)")
columns = [info[1] for info in cursor.fetchall()]

print(f"Current columns: {columns}")

if 'is_premium' not in columns:
    print("Adding is_premium column...")
    cursor.execute("ALTER TABLE user ADD COLUMN is_premium BOOLEAN DEFAULT 0")

if 'referral_code' not in columns:
    print("Adding referral_code column...")
    cursor.execute("ALTER TABLE user ADD COLUMN referral_code VARCHAR(10)")
    # SQLite workaround for unique constraint: we can create a unique index instead
    try:
        cursor.execute("CREATE UNIQUE INDEX idx_user_referral_code ON user(referral_code)")
    except Exception as e:
        print(f"Index creation warning: {e}")

if 'referred_by' not in columns:
    print("Adding referred_by column...")
    cursor.execute("ALTER TABLE user ADD COLUMN referred_by VARCHAR(10)")

if 'is_student' not in columns:
    print("Adding is_student column...")
    cursor.execute("ALTER TABLE user ADD COLUMN is_student BOOLEAN DEFAULT 1")

if 'upi_id' not in columns:
    print("Adding upi_id column...")
    cursor.execute("ALTER TABLE user ADD COLUMN upi_id VARCHAR(100)")

if 'monthly_budget' not in columns:
    print("Adding monthly_budget column...")
    cursor.execute("ALTER TABLE user ADD COLUMN monthly_budget FLOAT DEFAULT 20000.0")

# Create Expense Table
print("Creating expense table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS expense (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    merchant VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR(100) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
""")

conn.commit()

# Update Expense Table for Bills
cursor.execute("PRAGMA table_info(expense)")
exp_columns = [info[1] for info in cursor.fetchall()]

if 'is_bill' not in exp_columns:
    print("Adding is_bill column...")
    cursor.execute("ALTER TABLE expense ADD COLUMN is_bill BOOLEAN DEFAULT 0")

if 'due_date' not in exp_columns:
    print("Adding due_date column...")
    cursor.execute("ALTER TABLE expense ADD COLUMN due_date DATETIME")

if 'is_paid' not in exp_columns:
    print("Adding is_paid column...")
    cursor.execute("ALTER TABLE expense ADD COLUMN is_paid BOOLEAN DEFAULT 1")

if 'source' not in exp_columns:
    print("Adding source column...")
    cursor.execute("ALTER TABLE expense ADD COLUMN source VARCHAR(50) DEFAULT 'receipt'")

if 'matched_with_id' not in exp_columns:
    print("Adding matched_with_id column...")
    cursor.execute("ALTER TABLE expense ADD COLUMN matched_with_id INTEGER")

conn.commit()

# Update UserChallenge Table
print("Checking user_challenge table...")
try:
    cursor.execute("PRAGMA table_info(user_challenge)")
    chal_columns = [info[1] for info in cursor.fetchall()]
    
    if chal_columns: # Only if table exists
        if 'progress_data' not in chal_columns:
            print("Adding progress_data column to user_challenge...")
            cursor.execute("ALTER TABLE user_challenge ADD COLUMN progress_data TEXT DEFAULT '{}'")
    else:
        print("user_challenge table does not exist yet. It will be created by SQLAlchemy if not present.")
        
    conn.commit()
except Exception as e:
    print(f"Error updating user_challenge: {e}")

# Backfill referral codes
print("Backfilling referral codes...")
cursor.execute("SELECT id, username FROM user WHERE referral_code IS NULL")
users = cursor.fetchall()

for user_id, username in users:
    code = generate_code()
    # Simple collision check loop could be added here but unlikely for small userbase
    cursor.execute("UPDATE user SET referral_code = ? WHERE id = ?", (code, user_id))
    print(f"Generated code {code} for user {username}")

conn.commit()
conn.close()
print("Database upgrade complete!")
