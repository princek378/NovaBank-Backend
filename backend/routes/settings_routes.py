from flask import Blueprint, jsonify, request
from database import db
from models.admin_settings import AdminSettings

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


def get_or_create_settings():
    settings = AdminSettings.query.first()
    if not settings:
        settings = AdminSettings(
            admin_name="Administrator",
            email="admin@novabank.com",
            bank_name="NovaBank",
            currency="USD",
            imf_code="IMF-0000",
            cot_code="COT-0000",
            require_imf=True,
            require_cot=True,
        )
        db.session.add(settings)
        db.session.commit()
    return settings


@settings_bp.route("", methods=["GET"])
def get_settings():
    settings = get_or_create_settings()
    return jsonify({
        "admin_name": settings.admin_name,
        "email": settings.email,
        "bank_name": settings.bank_name,
        "currency": settings.currency,
        "imf_code": getattr(settings, "imf_code", "IMF-0000") or "IMF-0000",
        "cot_code": getattr(settings, "cot_code", "COT-0000") or "COT-0000",
        "require_imf": bool(getattr(settings, "require_imf", True)),
        "require_cot": bool(getattr(settings, "require_cot", True)),
    })


@settings_bp.route("/transfer-rules", methods=["GET"])
def transfer_rules():
    """Public rules for customer transfer form (no secret codes)."""
    settings = get_or_create_settings()
    return jsonify({
        "require_imf": bool(getattr(settings, "require_imf", True)),
        "require_cot": bool(getattr(settings, "require_cot", True)),
        "bank_name": settings.bank_name or "NovaBank",
    })


@settings_bp.route("", methods=["PUT"])
def update_settings():
    data = request.get_json() or {}
    settings = get_or_create_settings()

    if "admin_name" in data:
        settings.admin_name = data["admin_name"]
    if "email" in data:
        settings.email = data["email"]
    if "bank_name" in data:
        settings.bank_name = data["bank_name"]
    if "currency" in data:
        settings.currency = data["currency"]
    if "imf_code" in data:
        settings.imf_code = str(data["imf_code"]).strip()
    if "cot_code" in data:
        settings.cot_code = str(data["cot_code"]).strip()
    if "require_imf" in data:
        settings.require_imf = bool(data["require_imf"])
    if "require_cot" in data:
        settings.require_cot = bool(data["require_cot"])

    db.session.commit()
    return jsonify({"message": "Settings updated"})
