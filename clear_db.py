import sqlite3

conn = sqlite3.connect("saw_monitor.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM ping_log")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='ping_log'")
conn.commit()
conn.close()

print("ping_log tomoch id omsatt")