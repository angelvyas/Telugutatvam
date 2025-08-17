import sqlite3

# Connect to your local database
conn = sqlite3.connect("responses.db")
cursor = conn.cursor()

# Fetch the latest submissions
cursor.execute("""
    SELECT id, timestamp, category, prompt, text_response 
    FROM responses
    ORDER BY id DESC
""")
rows = cursor.fetchall()

# Print them nicely
for row in rows:
    print(f"ID: {row[0]}")
    print(f"Timestamp: {row[1]}")
    print(f"Category: {row[2]}")
    print(f"Prompt: {row[3]}")
    print(f"Response/File: {row[4]}")
    print("-" * 50)

conn.close()
