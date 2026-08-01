from database import db
from datetime import datetime


class User(db.Model):

    __tablename__ = "user"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(100),
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )


    password = db.Column(
        db.String(255),
        nullable=False
    )


    role = db.Column(
        db.String(50),
        default="Customer"
    )


    phone = db.Column(
        db.String(20),
        nullable=True
    )


    address = db.Column(
        db.String(255),
        nullable=True
    )


    status = db.Column(
        db.String(20),
        default="Active"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



    # ================================
    # USER ACCOUNTS
    # ================================

    accounts = db.relationship(
        "Account",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan"
    )



    # ================================
    # USER MESSAGES
    # ================================

    messages = db.relationship(
        "Message",
        backref="user",
        lazy=True
    )