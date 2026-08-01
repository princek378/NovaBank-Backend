from flask import Blueprint, request, jsonify

from database import db

from models.message import Message


chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)



# =====================================
# SEND MESSAGE
# =====================================

@chat_bp.route("/send", methods=["POST"])
def send_message():

    try:

        data = request.json


        msg = Message(

            user_id=data["user_id"],

            sender=data["sender"],

            message=data["message"],

            status="Sent",

            is_read=False

        )


        db.session.add(msg)

        db.session.commit()



        return jsonify({

            "message": "Message sent successfully"

        }), 201



    except Exception as e:


        print(e)


        return jsonify({

            "message": "Failed to send message"

        }), 500





# =====================================
# GET USER MESSAGES
# =====================================

@chat_bp.route("/<int:user_id>", methods=["GET"])
def get_messages(user_id):

    try:


        messages = Message.query.filter_by(

            user_id=user_id

        ).order_by(

            Message.created_at.asc()

        ).all()



        return jsonify([


            {

                "id": msg.id,

                "sender": msg.sender,

                "message": msg.message,

                "time":
                (
                    msg.created_at.strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    if msg.created_at

                    else ""

                ),

                "status": msg.status

            }


            for msg in messages


        ])




    except Exception as e:


        print(e)


        return jsonify({

            "message": "Could not load messages"

        }), 500







# =====================================
# UNREAD MESSAGE COUNT
# =====================================

@chat_bp.route("/unread", methods=["GET"])
def unread_messages():
    try:
        count = Message.query.filter_by(
            sender="Customer",
            is_read=False
        ).count()
        return jsonify({"unread": count})
    except Exception as e:
        print("unread error:", e)
        # Fallback: count all customer messages if is_read column issues
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

            is_read=False

        ).all()



        for msg in messages:

            msg.is_read = True



        db.session.commit()



        return jsonify({

            "message": "Messages marked as read"

        })



    except Exception as e:


        print(e)


        return jsonify({

            "message": "Failed to update messages"

        }),500