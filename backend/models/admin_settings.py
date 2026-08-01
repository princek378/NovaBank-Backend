from database import db
from datetime import datetime


class AdminSettings(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    admin_name = db.Column(
        db.String(100),
        default="Administrator"
    )


    email = db.Column(
        db.String(120),
        default="admin@novabank.com"
    )


    bank_name = db.Column(
        db.String(100),
        default="NovaBank"
    )


    currency = db.Column(
        db.String(10),
        default="USD"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )