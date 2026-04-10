from database.db import get_connection
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# ===============================
# Password Hashing
# ===============================
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ===============================
# Register User
# ===============================
def register_user(data):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(data["password"])

    try:
        cursor.execute("""
        INSERT INTO users (name, surname, email, password, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["surname"],
            data["email"],
            hashed_pw,
            data["role"],   # ✅ Now correct
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        return {"message": "User registered successfully"}

    except Exception as e:
        return {"error": str(e)}  # temporarily show real error

    finally:
        conn.close()


# ===============================
# Login User
# ===============================
def login_user(email, password, role):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND role = ?",
                   (email, role))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return {"error": "Invalid email or password"}

    if not verify_password(password, user["password"]):
        return {"error": "Invalid email or password"}

    return {
        "message": "Login successful",
        "role": user["role"],
        "name": user["name"],
        }
