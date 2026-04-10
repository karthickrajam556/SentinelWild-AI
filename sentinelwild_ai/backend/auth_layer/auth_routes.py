from fastapi import APIRouter
from pydantic import BaseModel
from auth_layer.auth_engine import register_user, login_user
from captcha.image import ImageCaptcha
import random
import string
from fastapi.responses import StreamingResponse
import re


router = APIRouter(prefix="/auth", tags=["Authentication"])
# Temporary in-memory store (demo level)
CAPTCHA_STORE = {}


# ===============================
# Signup Model
# ===============================
class SignupRequest(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    confirm_password: str
    role: str  # e.g., "Admin", "Ranger", "Researcher"


# ===============================
# Login Model
# ===============================
class LoginRequest(BaseModel):
    email: str
    password: str
    captcha: str
    role: str  # e.g., "Admin", "Ranger", "Researcher"


# ===============================
# Simple Captcha Validation
# ===============================
def validate_captcha(captcha):
    # simple demo captcha logic
    return captcha == "1234"


@router.get("/generate-captcha")
def generate_captcha():
    image = ImageCaptcha(width=150, height=50)
    current_captcha = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )
    CAPTCHA_STORE["current"] = current_captcha
    data = image.generate(current_captcha)

    return StreamingResponse(data, media_type="image/png")

# ===============================
# Password Strength Validation
# ===============================


def validate_password(password: str):

    if len(password) < 8:
        return "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"

    return None

# ===============================
# Signup Endpoint
# ===============================


@router.post("/signup")
def signup(data: SignupRequest):

    if data.password != data.confirm_password:
        return {"error": "Passwords do not match"}

    # 🔒 Password security validation
    password_error = validate_password(data.password)

    if password_error:
        return {"error": password_error}

    return register_user(data.dict())

# ===============================
# Login Endpoint
# ===============================


@router.post("/login")
def login(data: LoginRequest):

    stored_captcha = CAPTCHA_STORE.get("current")

    if not stored_captcha or data.captcha.upper() != stored_captcha:
        return {"error": "Invalid captcha"}
    CAPTCHA_STORE.pop("current", None)  # Clear used captcha

    return login_user(data.email, data.password, data.role)
