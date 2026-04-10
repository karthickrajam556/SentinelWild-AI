from fastapi import APIRouter
from pydantic import BaseModel
from feedback_layer.feedback_engine import (
    submit_feedback,
    get_all_feedback,
    get_ai_accuracy
)

router = APIRouter(prefix="/feedback", tags=["Human Feedback"])


# ===============================
# Feedback Request Model
# ===============================
class FeedbackRequest(BaseModel):
    incident_id: int
    ai_animal_type: str
    corrected_animal_type: str
    feedback_type: str
    reviewer_name: str
    comment: str


# ===============================
# Submit Feedback
# ===============================
@router.post("/submit")
def submit(data: FeedbackRequest):
    return submit_feedback(data.dict())


# ===============================
# Get All Feedback
# ===============================
@router.get("/")
def all_feedback():
    return get_all_feedback()


# ===============================
# AI Accuracy
# ===============================
@router.get("/accuracy")
def accuracy():
    return get_ai_accuracy()
