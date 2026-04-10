from fastapi import APIRouter
from analytics_layer.analytics_engine import (
    get_zone_heatmap,
    get_animal_frequency,
    get_time_pattern,
    get_monthly_report,
    get_risk_trend,
    get_zone_vulnerability,
    get_system_threat_level,
    get_prediction
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/heatmap")
def heatmap():
    return get_zone_heatmap()


@router.get("/animal-frequency")
def animal_frequency():
    return get_animal_frequency()


@router.get("/time-pattern")
def time_pattern():
    return get_time_pattern()


@router.get("/monthly-report")
def monthly_report():
    return get_monthly_report()


@router.get("/risk-trend")
def risk_trend():
    return get_risk_trend()


@router.get("/zone-vulnerability")
def zone_vulnerability():
    return get_zone_vulnerability()


@router.get("/threat-level")
def threat():
    return get_system_threat_level()


@router.get("/prediction")
def prediction():
    return get_prediction()


@router.get("/system-status")
def system_status():
    from analytics_layer.analytics_engine import get_system_status
    return get_system_status()
