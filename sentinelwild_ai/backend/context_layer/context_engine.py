from datetime import datetime
import random

from database.db import get_connection


ZONES = ["Farm", "Road", "Forest Border"]


def get_time_context():
    current_hour = datetime.now().hour

    if 6 <= current_hour < 18:
        return "Day"
    else:
        return "Night"


def get_zone_context(user_zone=None):
    """
    If user provides zone -> use it
    Else randomly assign zone
    """
    if user_zone and user_zone in ZONES:
        return user_zone
    return random.choice(ZONES)


def generate_gps_location():
    """
    Generate simulated GPS coordinates
    (Example: Tamil Nadu forest range style coordinates)
    """
    latitude = round(random.uniform(10.0, 12.5), 6)
    longitude = round(random.uniform(76.5, 79.5), 6)

    return {
        "latitude": latitude,
        "longitude": longitude
    }


def enrich_event(events, user_zone=None):
    """
    Add time, zone, GPS to each structured event
    """

    if not events:
        return []

    enriched_events = []

    time_context = get_time_context()
    zone_context = get_zone_context(user_zone)
    gps_location = generate_gps_location()

    for event in events:
        enriched = {
            **event,
            "time_of_day": time_context,
            "zone": zone_context,
            "gps_location": gps_location
        }

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO context_data (zone, latitude, longitude,
        time_of_day, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (
            zone_context,
            gps_location["latitude"],
            gps_location["longitude"],
            time_context,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        conn.commit()
        conn.close()

        enriched_events.append(enriched)

    return enriched_events
