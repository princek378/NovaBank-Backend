from flask import Blueprint, jsonify
from database import db

from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.message import Message

report_bp = Blueprint(
    "reports",
    __name__
)


@report_bp.route(
    "/api/admin/reports",
    methods=["GET"]
)
def reports():

    customers = User.query.count()

    accounts = Account.query.count()

    balance = db.session.query(
        db.func.sum(Account.balance)
    ).scalar() or 0

    deposits = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type == "Deposit"
    ).scalar() or 0

    withdrawals = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type == "Withdrawal"
    ).scalar() or 0

    transfers = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type.in_(
            ["Transfer In", "Transfer Out"]
        )
    ).scalar() or 0

    messages = Message.query.count()

    return jsonify({

        "customers": customers,

        "accounts": accounts,

        "balance": balance,

        "deposits": deposits,

        "withdrawals": withdrawals,

        "transfers": transfers,

        "messages": messages

    })