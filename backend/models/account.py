from database import db
from datetime import datetime


class Account(db.Model):

    __tablename__ = "account"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


    account_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )


    account_type = db.Column(
        db.String(50),
        default="Personal"
    )


    balance = db.Column(
        db.Float,
        default=0
    )


    currency = db.Column(
        db.String(10),
        default="USD"
    )


    status = db.Column(
        db.String(20),
        default="Active"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    user = db.relationship(
        "User",
        back_populates="accounts"
    )


    transactions = db.relationship(
        "Transaction",
        backref="account",
        lazy=True
    )