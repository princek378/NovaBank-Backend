from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import db
from models.user import User
from models.account import Account
from models.otp import OtpCode
from utils.email_service import send_otp_email
from datetime import datetime, timedelta
import uuid
import re
import json
import random

auth_bp = Blueprint("auth", __name__)


def generate_account_number():
    return "NB" + str(uuid.uuid4().int)[:10]


def make_otp():
    return f"{random.randint(100000, 999999)}"


def save_otp(email, purpose, payload=None):
    # invalidate old codes for same email+purpose
    OtpCode.query.filter_by(email=email, purpose=purpose, used=False).update({"used": True})
    code = make_otp()
    row = OtpCode(
        email=email,
        code=code,
        purpose=purpose,
        payload=json.dumps(payload) if payload else None,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        used=False,
    )
    db.session.add(row)
    db.session.commit()
    return code


def check_otp(email, code, purpose):
    row = (
        OtpCode.query.filter_by(email=email, purpose=purpose, used=False)
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if not row:
        return None, "Invalid or expired code"
    if row.expires_at < datetime.utcnow():
        return None, "Code has expired. Request a new one."
    if row.code != str(code).strip():
        return None, "Invalid code"
    return row, None


# ---------- REGISTER: step 1 send OTP ----------
@auth_bp.route("/api/register/request-otp", methods=["POST"])
def register_request_otp():
    data = request.get_json() or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    address = (data.get("address") or "").strip()

    if not first_name or not last_name or not email or not password:
        return jsonify({"message": "First name, last name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email address"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "phone": phone,
        "address": address,
    }
    code = save_otp(email, "register", payload)
    sent = send_otp_email(email, code, purpose="register")

    return jsonify({
        "message": "Verification code sent to your email" if sent else "Code created (check server logs if email not configured)",
        "email": email,
        "email_sent": sent,
    })


# ---------- REGISTER: step 2 verify OTP & create account ----------
@auth_bp.route("/api/register/verify", methods=["POST"])
def register_verify():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("otp") or data.get("code") or "").strip()

    row, err = check_otp(email, code, "register")
    if err:
        return jsonify({"message": err}), 400

    payload = json.loads(row.payload or "{}")
    if User.query.filter_by(email=email).first():
        row.used = True
        db.session.commit()
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        name=f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip(),
        email=email,
        password=generate_password_hash(payload.get("password") or ""),
        role="Customer",
        status="Active",
        phone=payload.get("phone") or None,
        address=payload.get("address") or None,
    )
    db.session.add(user)
    db.session.commit()

    account_number = generate_account_number()
    account = Account(
        user_id=user.id,
        account_number=account_number,
        account_type="Savings",
        balance=0.0,
        currency="USD",
        status="Active",
    )
    db.session.add(account)
    row.used = True
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "account_number": account_number,
    }), 201


# Keep old endpoint blocked or redirect style message
@auth_bp.route("/api/register", methods=["POST"])
def register_legacy():
    return jsonify({
        "message": "Please use email verification. Call /api/register/request-otp first.",
    }), 400


# ---------- LOGIN (unchanged logic) ----------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"message": "Email/username and password are required"}), 400

    if email == "admin":
        user = User.query.filter_by(role="Admin").first()
        if not user:
            user = User.query.filter_by(email="admin@novabank.com").first()
    else:
        user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    password_ok = False
    stored = user.password or ""
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:") or stored.startswith("argon2"):
        password_ok = check_password_hash(stored, password)
    else:
        password_ok = stored == password
        if password_ok:
            user.password = generate_password_hash(password)
            db.session.commit()

    if not password_ok:
        return jsonify({"message": "Invalid email or password"}), 401
    if getattr(user, "status", "Active") == "Frozen":
        return jsonify({"message": "Your account has been frozen. Contact support."}), 403

    token = create_access_token(identity=str(user.id))
    account_number = None
    account_balance = 0
    if user.accounts:
        account = user.accounts[0]
        account_number = account.account_number
        account_balance = account.balance

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": getattr(user, "status", "Active"),
            "account_number": account_number,
            "balance": account_balance,
        },
    })


# ---------- FORGOT PASSWORD: send OTP ----------
@auth_bp.route("/api/password/forgot", methods=["POST"])
def password_forgot():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    # Always return success message (don't reveal if email exists)
    if user:
        code = save_otp(email, "reset")
        send_otp_email(email, code, purpose="reset")

    return jsonify({
        "message": "If that email exists, a reset code has been sent.",
        "email": email,
    })


# ---------- RESET PASSWORD with OTP ----------
@auth_bp.route("/api/password/reset", methods=["POST"])
def password_reset():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("otp") or data.get("code") or "").strip()
    new_password = data.get("password") or data.get("new_password") or ""

    if len(new_password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    row, err = check_otp(email, code, "reset")
    if err:
        return jsonify({"message": err}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.password = generate_password_hash(new_password)
    row.used = True
    db.session.commit()

    return jsonify({"message": "Password updated successfully. You can log in now."})


@auth_bp.route("/api/admin/change-credentials", methods=["PUT"])
@jwt_required()
def change_admin_credentials():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid token"}), 401

    admin = User.query.get(user_id)
    if not admin or admin.role != "Admin":
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json() or {}
    new_name = (data.get("name") or "").strip()
    new_email = (data.get("email") or "").strip().lower()
    new_password = data.get("password") or ""
    current_password = data.get("current_password") or ""

    if not check_password_hash(admin.password, current_password):
        return jsonify({"message": "Current password is incorrect"}), 400

    if new_name:
        admin.name = new_name
    if new_email:
        exists = User.query.filter(User.email == new_email, User.id != admin.id).first()
        if exists:
            return jsonify({"message": "Email already in use"}), 400
        admin.email = new_email
    if new_password:
        if len(new_password) < 6:
            return jsonify({"message": "New password must be at least 6 characters"}), 400
        admin.password = generate_password_hash(new_password)

    db.session.commit()
    return jsonify({"message": "Admin credentials updated successfully"})
