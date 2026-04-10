from database.db import get_connection


# Get all incidents
def get_all_incidents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, animal_type, alert_level, zone, camera_id,
               latitude, longitude, timestamp, status
        FROM incidents
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    incidents = []

    for row in rows:
        incident = dict(row)

        # prepare GPS structure for map
        incident["gps_location"] = {
            "latitude": row["latitude"],
            "longitude": row["longitude"]
        }

        incidents.append(incident)

    return incidents


# Acknowledge incident
def acknowledge_incident(incident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE incidents
    SET status = 'Acknowledged'
    WHERE id = ?
    """, (incident_id,))

    conn.commit()
    conn.close()

    return {"message": "Incident acknowledged"}


# Resolve incident
def resolve_incident(incident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE incidents
    SET status = 'Resolved'
    WHERE id = ?
    """, (incident_id,))

    conn.commit()
    conn.close()

    return {"message": "Incident resolved"}


def get_incident_summary():

    conn = get_connection()
    cursor = conn.cursor()

    # Total incidents
    cursor.execute("SELECT COUNT(*) as total FROM incidents")
    total = cursor.fetchone()["total"]

    # Active incidents
    cursor.execute("""
        SELECT COUNT(*) as active
        FROM incidents
        WHERE status = 'Pending' OR status = 'Acknowledged'
    """)
    active = cursor.fetchone()["active"]

    # Resolved incidents
    cursor.execute("""
        SELECT COUNT(*) as resolved
        FROM incidents
        WHERE status = 'Resolved'
    """)
    resolved = cursor.fetchone()["resolved"]

    conn.close()

    return {
        "total": total,
        "active": active,
        "resolved": resolved
    }
