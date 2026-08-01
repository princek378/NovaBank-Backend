from database import db
from datetime import datetime
import uuid


class Transaction(db.Model):

    __tablename__ = "transaction"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("account.id"),
        nullable=False
    )

    transaction_reference = db.Column(
    db.String(50),
    nullable=False,
    default=lambda: str(uuid.uuid4())[:12].upper()
)

    description = db.Column(
        db.String(150),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    transaction_type = db.Column(
        db.String(30),
        nullable=False
    )

    # For transfers, stores the other account number
    related_account = db.Column(
        db.String(20),
        nullable=True
    )

    balance_after = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Completed"
    )

    created_by = db.Column(
        db.String(100),
        nullable=True
    )

    date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )