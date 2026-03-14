import sqlite3
import os

db_path = os.path.join('instance', 'fintelligent.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check columns for gamification_profile
cursor.execute("PRAGMA table_info(gamification_profile)")
columns = [info[1] for info in cursor.fetchall()]

print(f"Current columns in gamification_profile: {columns}")

if 'streak_count' not in columns:
    print("Adding streak_count column...")
    cursor.execute("ALTER TABLE gamification_profile ADD COLUMN streak_count INTEGER DEFAULT 0")

if 'last_activity_date' not in columns:
    print("Adding last_activity_date column...")
    cursor.execute("ALTER TABLE gamification_profile ADD COLUMN last_activity_date DATETIME")

if 'long_streak_record' not in columns:
    print("Adding long_streak_record column...")
    cursor.execute("ALTER TABLE gamification_profile ADD COLUMN long_streak_record INTEGER DEFAULT 0")

conn.commit()
conn.close()
print("Gamification database update complete!")
