import sqlite3

conn = sqlite3.connect("recoverai.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM webhook_events")

events = cursor.fetchall()

for event in events:
    print(event)

conn.close()
