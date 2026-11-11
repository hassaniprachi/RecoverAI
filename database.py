
import sqlite3


def create_database():
    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    # Create webhook events table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            event_type TEXT,
            subscription_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(webhook_events)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add resource_json if missing
    if "resource_json" not in columns:
        cursor.execute("""
            ALTER TABLE webhook_events
            ADD COLUMN resource_json TEXT
        """)

    # Add recovery_status if missing
    if "recovery_status" not in columns:
        cursor.execute("""
            ALTER TABLE webhook_events
            ADD COLUMN recovery_status TEXT DEFAULT 'Pending'
        """)

    # Add recovery message tracking timestamp
    if "contacted_at" not in columns:
        cursor.execute("""
            ALTER TABLE webhook_events
            ADD COLUMN contacted_at TIMESTAMP
        """)

    # Add payment recovery timestamp
    if "recovered_at" not in columns:
        cursor.execute("""
            ALTER TABLE webhook_events
            ADD COLUMN recovered_at TIMESTAMP
        """)

    conn.commit()
    conn.close()

    print("RecoverAI Database Updated Successfully!")
    print("Recovery tracking columns are ready.")


if __name__ == "__main__":
    create_database()
