from flask import Blueprint, request, jsonify
from database import db
from models.message import Message
from models.user import User
from werkzeug.security import generate_password_hash
import secrets
import os

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# Change this PIN in Render Environment if you want
SUPPORT_PIN = os.environ.get("SUPPORT_PIN", "novabank123")


def serialize_msg(msg):
    return {
        "id": msg.id,
        "sender": msg.sender,
        "message": msg.message,
        "time": msg.created_at.strftime("%Y-%m-%d %H:%M") if msg.created_at else "",
        "status": msg.status,
    }


# =====================================
# START / RESUME GUEST CHAT (no login)
# =====================================
@chat_bp.route("/guest/start", methods=["POST"])
def guest_start():
    try:
        data = request.json or {}
        name = (data.get("name") or "Guest").strip()
        email = (data.get("email") or "").strip().lower()

        if not email:
            return jsonify({"message": "Email is required"}), 400

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
        else:
            # update name if provided
            if name and name != "Guest":
                user.name = name
                db.session.commit()

        return jsonify({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
        })
    except Exception as e:
        print("guest_start error:", e)
        db.session.rollback()
        return jsonify({"message": "Could not start chat"}), 500


# =====================================
# GUEST SEND MESSAGE
# =====================================
@chat_bp.route("/guest/send", methods=["POST"])
def guest_send():
    try:
        data = request.json or {}
        user_id = data.get("user_id")
        text = (data.get("message") or "").strip()
        if not user_id or not text:
            return jsonify({"message": "user_id and message required"}), 400

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"message": "Chat session not found"}), 404

        msg = Message(
            user_id=user.id,
            sender="Customer",
            message=text,
            status="Sent",
            is_read=False,
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"message": "sent", "data": serialize_msg(msg)}), 201
    except Exception as e:
        print("guest_send error:", e)
        db.session.rollback()
        return jsonify({"message": "Failed to send"}), 500


# =====================================
# GET MESSAGES (guest or admin desk)
# =====================================
@chat_bp.route("/<int:user_id>", methods=["GET"])
def get_messages(user_id):
    try:
        messages = (
            Message.query.filter_by(user_id=user_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        return jsonify([serialize_msg(m) for m in messages])
    except Exception as e:
        print("get_messages error:", e)
        return jsonify({"message": "Could not load messages"}), 500


# =====================================
# NORMAL SEND (customer portal / admin panel)
# =====================================
@chat_bp.route("/send", methods=["POST"])
def send_message():
    try:
        data = request.json or {}
        user_id = data.get("user_id")
        sender = data.get("sender")
        text = data.get("message")
        if not user_id or not sender or not text:
            return jsonify({"message": "user_id, sender and message required"}), 400

        msg = Message(
            user_id=user_id,
            sender=sender,
            message=text,
            status="Sent",
            is_read=False if sender == "Customer" else True,
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        print("send_message error:", e)
        db.session.rollback()
        return jsonify({"message": "Failed to send message"}), 500


# =====================================
# SUPPORT DESK — unlock with PIN (no admin login)
# =====================================
@chat_bp.route("/desk/unlock", methods=["POST"])
def desk_unlock():
    data = request.json or {}
    pin = (data.get("pin") or "").strip()
    if pin != SUPPORT_PIN:
        return jsonify({"message": "Wrong support PIN"}), 403
    return jsonify({"ok": True, "message": "Unlocked"})


@chat_bp.route("/desk/conversations", methods=["GET"])
def desk_conversations():
    """List users who have messages (for support desk)."""
    try:
        pin = request.args.get("pin") or ""
        if pin != SUPPORT_PIN:
            return jsonify({"message": "Unauthorized"}), 403

        # Distinct user_ids that have messages
        rows = db.session.query(Message.user_id).distinct().all()
        user_ids = [r[0] for r in rows]
        result = []
        for uid in user_ids:
            user = User.query.get(uid)
            if not user:
                continue
            last = (
                Message.query.filter_by(user_id=uid)
                .order_by(Message.created_at.desc())
                .first()
            )
            unread = Message.query.filter_by(
                user_id=uid, sender="Customer", is_read=False
            ).count()
            result.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "last_message": last.message if last else "",
                "last_time": last.created_at.strftime("%Y-%m-%d %H:%M") if last and last.created_at else "",
                "unread": unread,
            })
        # newest first
        result.sort(key=lambda x: x["last_time"] or "", reverse=True)
        return jsonify(result)
    except Exception as e:
        print("desk_conversations error:", e)
        return jsonify({"message": "Failed to load"}), 500


@chat_bp.route("/desk/reply", methods=["POST"])
def desk_reply():
    try:
        data = request.json or {}
        pin = (data.get("pin") or "").strip()
        if pin != SUPPORT_PIN:
            return jsonify({"message": "Unauthorized"}), 403

        user_id = data.get("user_id")
        text = (data.get("message") or "").strip()
        if not user_id or not text:
            return jsonify({"message": "user_id and message required"}), 400

        msg = Message(
            user_id=int(user_id),
            sender="Admin",
            message=text,
            status="Sent",
            is_read=True,
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"message": "Reply sent", "data": serialize_msg(msg)}), 201
    except Exception as e:
        print("desk_reply error:", e)
        db.session.rollback()
        return jsonify({"message": "Failed to reply"}), 500


@chat_bp.route("/unread", methods=["GET"])
def unread_messages():
    try:
        count = Message.query.filter_by(sender="Customer", is_read=False).count()
        return jsonify({"unread": count})
    except Exception:
        return jsonify({"unread": 0})


@chat_bp.route("/read/<int:user_id>", methods=["PUT"])
def mark_messages_read(user_id):
    try:
        messages = Message.query.filter_by(
            user_id=user_id, sender="Customer", is_read=False
        ).all()
        for msg in messages:
            msg.is_read = True
        db.session.commit()
        return jsonify({"message": "Messages marked as read"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to update messages"}), 500
