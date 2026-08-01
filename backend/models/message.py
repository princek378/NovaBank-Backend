from database import db
from datetime import datetime


class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    sender = db.Column(
        db.String(50),
        nullable=False
    )


    message = db.Column(
        db.Text,
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    status = db.Column(
        db.String(20),
        default="Sent"
    )
    
    is_read = db.Column(
    db.Boolean,
    default=False
)