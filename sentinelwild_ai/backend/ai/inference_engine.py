import cv2
from ultralytics import YOLO

from database.db import get_connection
from datetime import datetime
import time


MODEL_PATH = "models/best.pt"

model = YOLO(MODEL_PATH)
# =============================
# STREAM CONTROL FLAG
# =============================
STREAM_ACTIVE = False


def detect_from_image(image_path):
    results = model(image_path, conf=0.4)

    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO detection_logs
            (animal_type, confidence, detected_at)
            VALUES (?, ?, ?)
            """, (
                label,
                confidence,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

            detections.append({
                "label": label,
                "confidence": round(confidence, 2)
            })

    return detections


def detect_from_frame(frame):
    results = model(frame, conf=0.4)

    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO detection_logs
            (animal_type, confidence, detected_at)
            VALUES (?, ?, ?)
            """, (
                label,
                confidence,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

            detections.append({
                "label": label,
                "confidence": round(confidence, 2)
            })

    return detections


def detect_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    all_detections = []

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_detections = detect_from_frame(frame)
        all_detections.extend(frame_detections)

    cap.release()

    return all_detections


def stream_video_with_detection(source, zone=None):

    from analytics_layer.analytics_engine import set_system_status
    set_system_status("Active")

    global STREAM_ACTIVE
    STREAM_ACTIVE = True

    import cv2
    from datetime import datetime
    from database.db import get_connection

    from event_layer.event_generator import generate_wildlife_event
    from context_layer.context_engine import enrich_event
    from decision_layer.decision_engine import decision_engine
    from alert_layer.alert_engine import generate_alert

    cap = cv2.VideoCapture(source)

    frame_count = 0

    while STREAM_ACTIVE and cap.isOpened():

        success, frame = cap.read()

        if not success:
            print("Video finished. Stopping stream.")
            break

        # ✅ Resize for speed
        frame = cv2.resize(frame, (480, 360))

        frame_count += 1

        # ✅ Skip more frames for speed
        if frame_count % 4 != 0:
            continue

        results = model(frame, conf=0.4)

        detections = []

        for r in results:
            for box in r.boxes:

                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "label": label,
                    "confidence": confidence
                })

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                text = f"{label} {confidence:.2f}"
                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # ==============================
        # DECISION + ALERT + DB INSERT
        # ==============================
        if detections:

            # 🔥 Insert to DB ONCE per frame, not per box
            conn = get_connection()
            cursor = conn.cursor()

            for det in detections:
                cursor.execute("""
                    INSERT INTO detection_logs
                    (animal_type, confidence, detected_at)
                    VALUES (?, ?, ?)
                """, (
                    det["label"],
                    det["confidence"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

            conn.commit()
            conn.close()

            event = generate_wildlife_event(detections)
            enriched_event = enrich_event(event, zone)
            decision_output = decision_engine(enriched_event)

            generate_alert(decision_output)

        # Encode frame
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

        time.sleep(0.03)

    cap.release()
    set_system_status("Idle")
    STREAM_ACTIVE = False
    print("Stream stopped cleanly.")
