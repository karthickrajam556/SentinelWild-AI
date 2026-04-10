from collections import Counter
from datetime import datetime
import uuid

VALID_CLASSES = ["Elephant", "Wild_boar", "Deer", "Human", "Cow"]


def generate_camera_id():
    return f"CAM-{uuid.uuid4().hex[:6].upper()}"


def generate_wildlife_event(detections):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    camera_id = generate_camera_id()

    if not detections:
        return []

    labels = [d["label"] for d in detections if d["label"] in VALID_CLASSES]

    if not labels:
        return []

    counter = Counter(labels)

    events = []

    from database.db import get_connection

    for animal, count in counter.items():
        event = {
            "animal_type": animal,
            "count": count,
            "timestamp": timestamp,
            "camera_id": camera_id
        }

    events.append(event)

    # ===============================
    # 🗄 INSERT INTO wildlife_events TABLE
    # ===============================
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO wildlife_events (animal_type, count, timestamp, camera_id)
    VALUES (?, ?, ?, ?)
    """, (
        animal,
        count,
        timestamp,
        camera_id
    ))

    conn.commit()
    conn.close()

    return events
