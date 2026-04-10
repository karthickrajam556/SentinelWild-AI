def calculate_risk_score(event):
    """
    Rule-Based Risk Calculation Engine
    """

    animal = event["animal_type"]
    count = event["count"]
    time_of_day = event["time_of_day"]
    zone = event["zone"]

    # =========================
    # 1️⃣ Base Risk by Animal
    # =========================
    base_risk_map = {
        "Elephant": 60,
        "Wild_boar": 45,
        "Deer": 30,
        "Cow": 20,
        "Human": 25
    }

    risk = base_risk_map.get(animal, 0)

    # =========================
    # 2️⃣ Count Multiplier
    # =========================
    risk += count * 10

    # =========================
    # 3️⃣ Night Bonus
    # =========================
    if time_of_day == "Night":
        risk += 15

    # =========================
    # 4️⃣ Zone Multiplier
    # =========================
    zone_bonus = {
        "Forest_Border": 25,
        "Road": 15,
        "Farm": 10
    }

    risk += zone_bonus.get(zone, 0)

    # Clamp risk
    risk = min(risk, 100)

    return risk


def classify_alert(risk_score):
    """
    Convert risk score to alert level
    """

    if risk_score <= 20:
        return "NO_ALERT"
    elif 21 <= risk_score <= 40:
        return "LOW"
    elif 41 <= risk_score <= 60:
        return "MEDIUM"
    elif 61 <= risk_score <= 80:
        return "HIGH"
    else:
        return "CRITICAL"


def determine_alert_type(animal):
    """
    Determine alert type category
    """

    if animal in ["Elephant", "Wild_boar", "Deer"]:
        return "True Wildlife Alert"

    elif animal == "Cow":
        return "Domestic Animal Presence"

    elif animal == "Human":
        return "Human Activity Alert"

    return "False Alert"


def decision_engine(enriched_events):
    """
    Process enriched events and return decision output
    """

    if not enriched_events:
        return []

    final_decisions = []

    for event in enriched_events:

        if event["animal_type"] is None:
            continue

        risk_score = calculate_risk_score(event)
        alert_level = classify_alert(risk_score)

        animal_type = event.get("animal_type")
        count = event.get("count", 0)

        # Ensure count is integer
        if not isinstance(count, int):
            try:
                count = int(count)
            except (ValueError, TypeError):
                count = 0

        if animal_type in ["Elephant", "Wild_boar"] and count >= 3:
            alert_level = "CRITICAL"
        alert_type = determine_alert_type(event["animal_type"])

        from database.db import get_connection
        from datetime import datetime

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO risk_assessments
            (animal_type, risk_score, alert_level, created_at)
            VALUES (?, ?, ?, ?)""",
            (
                event["animal_type"],
                risk_score,
                alert_level,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

        requires_action = alert_level in ["HIGH", "CRITICAL"]
        decision_output = {
            **event,
            "risk_score": risk_score,
            "alert_level": alert_level,
            "alert_type": alert_type,
            "requires_immediate_action": requires_action
        }

        final_decisions.append(decision_output)

    return final_decisions
