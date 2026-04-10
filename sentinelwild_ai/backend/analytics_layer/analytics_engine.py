from database.db import get_connection


SYSTEM_STATUS = "Idle"


def set_system_status(status: str):
    global SYSTEM_STATUS
    SYSTEM_STATUS = status


def get_system_status():
    return {"status": SYSTEM_STATUS}


# ===============================
# 1️⃣ Heatmap (Zone Intrusion Count)
# ===============================
def get_zone_heatmap():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT zone, COUNT(*) as total
    FROM context_data
    GROUP BY zone
    """)

    data = cursor.fetchall()
    conn.close()

    return {row["zone"]: row["total"] for row in data}


# ===============================
# 2️⃣ Animal Frequency
# ===============================
def get_animal_frequency():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT animal_type, COUNT(*) as total
    FROM wildlife_events
    GROUP BY animal_type
    """)

    data = cursor.fetchall()
    conn.close()

    return {row["animal_type"]: row["total"] for row in data}


# ===============================
# 3️⃣ Time Pattern Analysis
# ===============================
def get_time_pattern():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT strftime('%H', timestamp) as hour,
           animal_type,
           COUNT(*) as total
    FROM wildlife_events
    GROUP BY hour, animal_type
    ORDER BY hour
    """)

    data = cursor.fetchall()
    conn.close()

    result = []

    for row in data:
        result.append({
            "hour": row["hour"],
            "animal": row["animal_type"],
            "count": row["total"]
        })

    return result


# ===============================
# 4️⃣ Monthly Report
# ===============================
def get_monthly_report():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        strftime('%Y-%m', created_at) as month,
        COUNT(*) as total_incidents,
        SUM(CASE WHEN alert_level='CRITICAL' THEN 1 ELSE 0 END)
                   as critical_cases,
        SUM(CASE WHEN alert_level='HIGH' THEN 1 ELSE 0 END) as high_cases,
        AVG(risk_score) as avg_risk
    FROM risk_assessments
    GROUP BY month
    ORDER BY month
    """)

    monthly_data = cursor.fetchall()

    report = []

    for row in monthly_data:

        month = row["month"]

        # Animal distribution
        cursor.execute("""
        SELECT animal_type, COUNT(*) as total
        FROM risk_assessments
        WHERE strftime('%Y-%m', created_at)=?
        GROUP BY animal_type
        """, (month,))
        animals = cursor.fetchall()

        # Zone distribution
        cursor.execute("""
        SELECT zone, COUNT(*) as total
        FROM context_data
        WHERE strftime('%Y-%m', created_at)=?
        GROUP BY zone
        """, (month,))
        zones = cursor.fetchall()

        report.append({
            "month": month,
            "total_incidents": row["total_incidents"],
            "critical_cases": row["critical_cases"],
            "high_cases": row["high_cases"],
            "average_risk": round(row["avg_risk"], 2) if row["avg_risk"]
            else 0,
            "animal_distribution": [
                {"animal": a["animal_type"], "count": a["total"]}
                for a in animals
            ],
            "zone_distribution": [
                {"zone": z["zone"], "count": z["total"]}
                for z in zones
            ]
        })

    conn.close()
    return report


# ===============================
# 5️⃣ Risk Trend (Last 7 Days)
# ===============================
def get_risk_trend():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            strftime('%Y-%m-%d %H:%M', created_at) as time_slot,
            AVG(risk_score) as avg_risk
        FROM risk_assessments
        GROUP BY strftime('%Y-%m-%d %H', created_at),
                 (CAST(strftime('%M', created_at) AS INTEGER) / 30)
        ORDER BY time_slot
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "timestamps": [row[0] for row in rows],
        "risk_scores": [round(row[1], 2) for row in rows]
    }


# ===============================
# 6️⃣ Zone Vulnerability Index
# ===============================
def get_zone_vulnerability():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT zone,
           COUNT(*) as total_incidents
    FROM incidents
    GROUP BY zone
    """)

    data = cursor.fetchall()
    conn.close()

    vulnerability = {}

    for row in data:
        vulnerability[row["zone"]] = row["total_incidents"] * 10

    return vulnerability


def get_system_threat_level():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT alert_level
        FROM incidents
        WHERE status = 'Pending'
    """)

    levels = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not levels:
        return {"level": "LOW", "description": "No Active Threat"}

    if "CRITICAL" in levels:
        return {"level": "CRITICAL", "description": "Severe Threat"}
    elif "HIGH" in levels:
        return {"level": "HIGH", "description": "High Risk"}
    elif "MEDIUM" in levels:
        return {"level": "MEDIUM", "description": "Moderate Risk"}
    else:
        return {"level": "LOW", "description": "Low Risk"}


# ===============================
# 7️⃣ Prediction Engine
# ===============================
def get_prediction():

    conn = get_connection()
    cursor = conn.cursor()

    # Get recent 24-hour average risk
    cursor.execute("""
        SELECT AVG(risk_score) as avg_risk
        FROM risk_assessments
        WHERE datetime(created_at) >= datetime('now', '-1 day')
    """)

    avg_risk = cursor.fetchone()["avg_risk"] or 0

    # Most frequent animal in last 24 hours
    cursor.execute("""
        SELECT animal_type, COUNT(*) as total
        FROM risk_assessments
        WHERE datetime(created_at) >= datetime('now', '-1 day')
        GROUP BY animal_type
        ORDER BY total DESC
        LIMIT 1
    """)

    animal = cursor.fetchone()

    # Most active zone in last 24 hours
    cursor.execute("""
        SELECT zone, COUNT(*) as total
        FROM context_data
        WHERE datetime(created_at) >= datetime('now', '-1 day')
        GROUP BY zone
        ORDER BY total DESC
        LIMIT 1
    """)

    zone = cursor.fetchone()

    conn.close()

    if not animal or not zone:
        return {"prediction": "Not enough recent data for prediction."}

    # Determine severity dynamically
    if avg_risk >= 85:
        severity = "CRITICAL"
    elif avg_risk >= 65:
        severity = "HIGH"
    elif avg_risk >= 40:
        severity = "MODERATE"
    else:
        severity = "LOW"

    return {
        "prediction": f"⚠ Forecast: {severity} probability of "
                      f"{animal['animal_type']} intrusion in "
                      f"{zone['zone']} zone within next 24 hours. "
                      f"(Based on recent average risk score: "
                      f"{round(avg_risk, 2)})"
    }
