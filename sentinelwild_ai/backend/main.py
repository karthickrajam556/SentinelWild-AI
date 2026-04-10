from fastapi import FastAPI
from input_layer.routes import router as input_router
from alert_layer.alert_routes import router as alert_router
from database.models import create_tables
from analytics_layer.analytics_routes import router as analytics_router
from feedback_layer.feedback_routes import router as feedback_router
from operations_layer.operations_routes import router as operations_router
from auth_layer.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="SentinelWild AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(input_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(feedback_router)
app.include_router(operations_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "SentinelWild AI Backend Running"}
