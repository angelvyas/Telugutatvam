import sqlite3

conn = sqlite3.connect("responses.db")
cursor = conn.cursor()

file_path = "user_uploads/rohitbitla/Video_20250801_104328.mp4"

cursor.execute("""
    UPDATE responses
    SET text_response = ?
    WHERE swecha_username = 'rohitbitla'
    AND timestamp = '2025-08-01 10:43:28'
""", (f"File uploaded: {file_path}",))

conn.commit()
conn.close()
print("✅ Repaired entry.")
