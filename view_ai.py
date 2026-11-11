import sqlite3

conn = sqlite3.connect("recoverai.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT event_id, recommendation, created_at
    FROM ai_recommendations
""")

results = cursor.fetchall()

if not results:
    print("No AI recommendations found yet.")

for result in results:
    print("\nEvent ID:", result[0])
    print("AI Recommendation:\n", result[1])
    print("Created At:", result[2])

conn.close()