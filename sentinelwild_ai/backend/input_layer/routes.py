from fastapi import APIRouter, UploadFile, File
import ai.inference_engine as inference_engine
from fastapi.responses import JSONResponse
import shutil
import os
#   import threading

from fastapi.responses import StreamingResponse
from ai.inference_engine import stream_video_with_detection
from input_layer.camera_manager import CameraManager
from event_layer.event_generator import generate_wildlife_event
from context_layer.context_engine import enrich_event
from decision_layer.decision_engine import decision_engine
from alert_layer.alert_engine import generate_alert
from analytics_layer.analytics_engine import set_system_status


from ai.inference_engine import (
    detect_from_image,
    detect_from_frame
)

router = APIRouter(prefix="/input", tags=["Input Layer"])

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

camera_manager = CameraManager()


# =====================================================
# 1️⃣ IMAGE UPLOAD + AI DETECTION
# =====================================================
def run_alerts_safe(decision_output):
    try:
        generate_alert(decision_output)
    except Exception as e:
        print("Alert Engine Error:", e)


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), zone: str = None):

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        detections = detect_from_image(file_path)

        event = generate_wildlife_event(detections)
        enriched_event = enrich_event(event, zone)
        decision_output = decision_engine(enriched_event)
        alerts = generate_alert(decision_output)

        return {
            "status": "success",
            "type": "image",
            "decision": decision_output,
            "alerts": alerts
        }

    except Exception as e:
        print("Upload Image Error:", e)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =====================================================
# 2️⃣ VIDEO UPLOAD + AI DETECTION
# =====================================================
uploaded_video_path = None


@router.post("/upload-video-stream")
async def upload_video_stream(file: UploadFile = File(...)):
    global uploaded_video_path

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_video_path = file_path

    return {"status": "uploaded"}


@router.get("/video-stream")
def video_stream(zone: str = None):

    global uploaded_video_path

    if not uploaded_video_path:
        return {"error": "No video uploaded"}

    return StreamingResponse(
        stream_video_with_detection(uploaded_video_path, zone),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# =====================================================
# 3️⃣ START WEBCAM (Manual Trigger)
# =====================================================
@router.post("/start-webcam")
def start_webcam():
    try:
        camera_manager.start_camera(0)
        return {"status": "Webcam started successfully"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# =====================================================
# 4️⃣ STOP WEBCAM
# =====================================================
@router.post("/stop-webcam")
def stop_webcam():
    inference_engine.STREAM_ACTIVE = False
    camera_manager.stop_camera()
    set_system_status("Idle")
    return {"status": "Webcam stopped successfully"}


@router.get("/webcam-stream")
def webcam_stream(zone: str = None):
    return StreamingResponse(
        stream_video_with_detection(0, zone),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/stop-stream")
def stop_stream():
    inference_engine.STREAM_ACTIVE = False
    set_system_status("Idle")
    return {"message": "Stream stopped successfully"}


# =====================================================
# 5️⃣ WEBCAM LIVE DETECTION
# =====================================================
@router.get("/webcam-detect")
def webcam_detect(zone: str = None):
    frame = camera_manager.get_frame()

    if frame is None:
        return {"error": "Webcam not started or frame not available"}

    # 1️⃣ Detect
    detections = detect_from_frame(frame)

    # 2️⃣ Event generation
    event = generate_wildlife_event(detections)

    # 3️⃣ Context enrichment
    enriched_event = enrich_event(event, zone)

    # 4️⃣ Decision engine
    decision_output = decision_engine(enriched_event)
    alerts = generate_alert(decision_output)

    return {
        "status": "success",
        "decision": decision_output,
        "alerts": alerts
    }
