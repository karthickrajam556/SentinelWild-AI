from database.db import get_connection
from datetime import datetime


# ===============================
# Submit Feedback
# ===============================
def submit_feedback(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO human_feedback (
        incident_id,
        ai_animal_type,
        corrected_animal_type,
        feedback_type,
        reviewer_name,
        comment,
        reviewed_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["incident_id"],
        data["ai_animal_type"],
        data["corrected_animal_type"],
        data["feedback_type"],
        data["reviewer_name"],
        data["comment"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return {"message": "Feedback submitted successfully"}


# ===============================
# Get All Feedback
# ===============================
def get_all_feedback():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM human_feedback ORDER BY reviewed_at DESC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ===============================
# AI Accuracy Calculation
# ===============================
def get_ai_accuracy():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM human_feedback")
    total = cursor.fetchone()["total"]

    if total == 0:
        conn.close()
        return {"accuracy": 0}

    cursor.execute("""
        SELECT COUNT(*) as correct
        FROM human_feedback
        WHERE LOWER(TRIM(ai_animal_type)) =
              LOWER(TRIM(corrected_animal_type))
    """)

    correct = cursor.fetchone()["correct"]

    conn.close()

    accuracy = round((correct / total) * 100, 2)

    return {"accuracy": accuracy}
