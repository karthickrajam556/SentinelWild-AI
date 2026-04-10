from fastapi import APIRouter
from alert_layer.alert_engine import WEB_ALERTS

router = APIRouter(prefix="/alerts", tags=["Web Alerts"])


@router.get("/")
def get_alerts():
    return {
        "total_alerts": len(WEB_ALERTS),
        "alerts": WEB_ALERTS
    }


@router.delete("/clear")
def clear_alerts():
    WEB_ALERTS.clear()
    return {"message": "All alerts cleared"}
