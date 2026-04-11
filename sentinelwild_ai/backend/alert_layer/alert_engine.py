from datetime import datetime
import requests
import time
import os
from dotenv import load_dotenv
import threading

try:
    import pygame
except ImportError:
    pygame = None

if pygame:
    pygame.mixer.init()


SOUND_PATH = os.path.join(os.getcwd(), "Alert Sound.mp3")


# Cooldown storage
LAST_ALERT_TIME = {}
ALERT_COOLDOWN_SECONDS = 10

WEB_ALERTS = []


# ==========================================
# TELEGRAM CONFIGURATION
# ==========================================
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ==========================================
# SMS CONFIGURATION
# ==========================================
SMS_API_KEY = os.getenv("SMS_API_KEY")

FOREST_OFFICER_NUMBERS = [
    "7904551128",
    "8870374621",
    "9344349881"
]


# ==========================================
# SOUND ALERT FUNCTION
# ==========================================
def play_alarm(level):
    def sound():
        try:
            if not pygame.mixer.get_init():
                return
            pygame.mixer.music.load(SOUND_PATH)
            pygame.mixer.music.play()
        except Exception as e:
            print("Sound Error:", e)
    threading.Thread(target=sound).start()


# ==========================================
# TELEGRAM ALERT FUNCTION
# ==========================================
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)


# ==========================================
# SMS ALERT FUNCTION
# ==========================================


def send_sms_alert(message):
    print("Sending SMS Alert...")
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"

        payload = {
            "message": message,
            "numbers": ",".join(FOREST_OFFICER_NUMBERS),
            "route": "q",
            "sender_id": "ALERTS"
        }

        headers = {
            "authorization": SMS_API_KEY
        }

        response = requests.post(url, data=payload, headers=headers)

        print("SMS Response:", response.text)

    except Exception as e:
        print("SMS Error:", e)


# ==========================================
# MAIN ALERT ORCHESTRATION ENGINE
# ==========================================
def generate_alert(decision_output):

    alerts = []

    for event in decision_output:

        animal = event["animal_type"]
        level = event["alert_level"]

        # ===============================
        # 1️⃣ If nothing detected → skip
        # ===============================
        if animal is None:
            continue

        # ===============================
        # 2️⃣ Human never CRITICAL
        # ===============================
        if animal == "Human" and level == "CRITICAL":
            level = "HIGH"

        alert_data = {
            "animal_type": animal,
            "camera_id": event.get("camera_id"),
            "zone": event["zone"],
            "risk_score": event["risk_score"],
            "alert_level": level,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        alerts.append(alert_data)
        WEB_ALERTS.append(alert_data)

        # ===============================
        # Commercial Message Format
        # ===============================
        if animal in ["Elephant", "Wild_boar", "Deer"]:

            message = f"""
🚨 SentinelWild AI - Wildlife Intrusion Alert 🚨

Animal Detected : {animal}
Total Count     : {event['count']}
Risk Score      : {event['risk_score']}
Alert Level     : {level}
Zone            : {event['zone']}
Camera ID       : {event['camera_id']}
GPS Location    : {event['gps_location']['latitude']}, \
{event['gps_location']['longitude']}
Detected Time   : {event['timestamp']}

⚠ Immediate Attention Recommended.
"""

        elif animal == "Human":

            message = f"""
🔔 SentinelWild AI - Human Activity Detected

Person Count    : {event['count']}
Risk Score      : {event['risk_score']}
Zone            : {event['zone']}
Camera ID       : {event['camera_id']}
GPS Location    : {event['gps_location']['latitude']}, \
{event['gps_location']['longitude']}
Detected Time   : {event['timestamp']}

Monitoring Recommended.
"""

        else:
            # Domestic animals like Cow → Optional alert
            message = f"""
ℹ SentinelWild AI - Domestic Animal Presence

Animal          : {animal}
Count           : {event['count']}
Zone            : {event['zone']}
Camera ID       : {event['camera_id']}
GPS Location    : {event['gps_location']['latitude']}, \
{event['gps_location']['longitude']}
Detected Time   : {event['timestamp']}

Monitoring Recommended.
"""

        # ===============================
        # Cooldown Protection
        # ===============================
        current_time = time.time()
        alert_key = f"{animal}_{level}"

        if alert_key not in LAST_ALERT_TIME or \
           (current_time - LAST_ALERT_TIME[alert_key]) \
           > ALERT_COOLDOWN_SECONDS:

            LAST_ALERT_TIME[alert_key] = current_time

            # 🔊 Sound only for Wild Animals
            if animal in ["Elephant", "Wild_boar", "Deer"]:
                play_alarm(level)

            # 📲 Telegram for all valid detections
            send_telegram_alert(message)
            send_sms_alert(message)

            from database.db import get_connection

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO incidents
            (animal_type, alert_level, zone, camera_id,
                           latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                animal,
                level,
                event["zone"],
                event["camera_id"],
                event["gps_location"]["latitude"],
                event["gps_location"]["longitude"],
                event["timestamp"]
            ))

            conn.commit()
            conn.close()

    return alerts
