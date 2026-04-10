from fastapi import APIRouter
from operations_layer.operations_engine import (
    get_all_incidents,
    acknowledge_incident,
    resolve_incident,
    get_incident_summary
)

router = APIRouter(prefix="/operations", tags=["Incident Operations"])


@router.get("/incidents")
def all_incidents():
    return get_all_incidents()


@router.post("/acknowledge/{incident_id}")
def acknowledge(incident_id: int):
    return acknowledge_incident(incident_id)


@router.post("/resolve/{incident_id}")
def resolve(incident_id: int):
    return resolve_incident(incident_id)


@router.get("/incident-summary")
def incident_summary():
    return get_incident_summary()
