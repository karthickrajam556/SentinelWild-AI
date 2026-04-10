from database.db import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Detection Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detection_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_type TEXT,
        confidence REAL,
        detected_at TEXT
    )
    """)

    # Wildlife Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wildlife_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_type TEXT,
        count INTEGER,
        timestamp TEXT,
        camera_id TEXT
    )
    """)

    # Context Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS context_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone TEXT,
        latitude REAL,
        longitude REAL,
        time_of_day TEXT,
        created_at TEXT
    )
    """)

    # Risk Assessments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_type TEXT,
        risk_score INTEGER,
        alert_level TEXT,
        created_at TEXT
    )
    """)

    # Incident Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_type TEXT,
    alert_level TEXT,
    zone TEXT,
    camera_id TEXT,
    status TEXT DEFAULT 'Pending'
    )
    """)

    # Human Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS human_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER,
    ai_animal_type TEXT,
    corrected_animal_type TEXT,
    feedback_type TEXT,
    reviewer_name TEXT,
    comment TEXT,
    reviewed_at TEXT
    )
    """)

    # ===============================
    # Users Table
    # ===============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    surname TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    created_at TEXT
    )
    """)

    conn.commit()
    conn.close()
