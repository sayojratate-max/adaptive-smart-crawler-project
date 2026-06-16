import sqlite3
import os
from pathlib import Path

# Connect to the database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "smart_deep_web_crawler" / "output" / "auth.db"

if not db_path.exists():
    print(f"Database not found at: {db_path}")
    print("Please make sure the app has been run at least once.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all users
    try:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        
        if not rows:
            print("--- USERS TABLE IS EMPTY ---")
        else:
            print("--- USERS TABLE (" + str(len(rows)) + " user(s)) ---")
            print(f"{'ID':<5} | {'Username':<20} | {'Password Hash'}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<5} | {row[1]:<20} | {row[2]}")
                
    except sqlite3.OperationalError as e:
        print(f"Error reading from database: {e}")
        
    finally:
        conn.close()
