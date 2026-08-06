from flask import Blueprint, request, jsonify
from database import db
from models.message import Message
from models.user import User
from werkzeug.security import generate_password_hash
import secrets

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


# =====================================
# SEND MESSAGE (logged-in customer / admin)
# =====================================
@chat_bp.route("/send", methods=["POST"])
def send_message():
    try:
        data = request.json or {}
        user_id = data.get("user_id")
        sender = data.get("sender")
        text = data.get("message")

        if not user_id or not sender or not text:
            return jsonify({"message": "user_id, sender and message are required"}), 400

        msg = Message(
            user_id=user_id,
            sender=sender,
            message=text,
            status="Sent",
            is_read=False,
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        print("send_message error:", e)
        db.session.rollback()
        return jsonify({"message": "Failed to send message"}), 500


# =====================================
# GUEST SUPPORT (no account required)
# =====================================
@chat_bp.route("/guest", methods=["POST"])
def guest_message():
    """Allow visitors without an account to message support."""
    try:
        data = request.json or {}
        name = (data.get("name") or "Guest").strip()
        email = (data.get("email") or "").strip().lower()
        text = (data.get("message") or "").strip()

        if not email or not text:
            return jsonify({"message": "Email and message are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(secrets.token_hex(16)),
                role="Customer",
                status="Active",
            )
            db.session.add(user)
            db.session.commit()

        msg = Message(
            user_id=user.id,
            sender="Customer",
            message=f"[Guest support] {text}",
            status="Sent",
            is_read=False,
        )
        db.session.add(msg)
        db.session.commit()

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        print("guest_message error:", e)
        db.session.rollback()
        return jsonify({"message": "Failed to send message"}), 500


# =====================================
# GET USER MESSAGES
# =====================================
@chat_bp.route("/<int:user_id>", methods=["GET"])
def get_messages(user_id):
    try:
        messages = (
            Message.query.filter_by(user_id=user_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        return jsonify([
            {
                "id": msg.id,
                "sender": msg.sender,
                "message": msg.message,
                "time": (
                    msg.created_at.strftime("%Y-%m-%d %H:%M")
                    if msg.created_at
                    else ""
                ),
                "status": msg.status,
            }
            for msg in messages
        ])
    except Exception as e:
        print("get_messages error:", e)
        return jsonify({"message": "Could not load messages"}), 500


# =====================================
# UNREAD MESSAGE COUNT
# =====================================
@chat_bp.route("/unread", methods=["GET"])
def unread_messages():
    try:
        count = Message.query.filter_by(
            sender="Customer",
            is_read=False,
        ).count()
        return jsonify({"unread": count})
    except Exception as e:
        print("unread error:", e)
        try:
            count = Message.query.filter_by(sender="Customer").count()
            return jsonify({"unread": count})
        except Exception as e2:
            print(e2)
            return jsonify({"unread": 0})


# =====================================
# MARK MESSAGES AS READ
# =====================================
@chat_bp.route("/read/<int:user_id>", methods=["PUT"])
def mark_messages_read(user_id):
    try:
        messages = Message.query.filter_by(
            user_id=user_id,
            sender="Customer",
            is_read=False,
        ).all()
        for msg in messages:
            msg.is_read = True
        db.session.commit()
        return jsonify({"message": "Messages marked as read"})
    except Exception as e:
        print("mark_messages_read error:", e)
        return jsonify({"message": "Failed to update messages"}), 500
