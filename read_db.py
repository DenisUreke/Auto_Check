import sqlite3

conn = sqlite3.connect("saw_monitor.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT id, target_name, checked_at, response_time_ms, success, status_code, response_text, error_text
    FROM ping_log
    ORDER BY id ASC
    LIMIT 20
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()