# test_db.py

import db

try:
    conn = db.get_connection()
    print(" Connected to Oracle DB!")

    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM user_tables")
    for row in cursor.fetchall():
        print("📄", row[0])
    
    conn.close()
except Exception as e:
    print(" Connection failed:", e)
