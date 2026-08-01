from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.account import Account
from models.transaction import Transaction

customer_bp = Blueprint("customer", __name__)

@customer_bp.route("/api/customer/profile", methods=["GET"])
@jwt_required()
def customer_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    account = Account.query.filter_by(user_id=user.id).first()
    transactions = []
    if account:
        txs = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.date.desc()).limit(20).all()
        for tx in txs:
            transactions.append({
                "id": tx.id,
                "description": tx.description,
                "amount": tx.amount,
                "type": tx.transaction_type,
                "status": tx.status,
                "date": tx.date.isoformat() if tx.date else None,
                "reference": getattr(tx, "transaction_reference", None),
            })

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "role": user.role,
        "status": getattr(user, "status", "Active"),
        "account": {
            "account_number": account.account_number if account else None,
            "balance": account.balance if account else 0,
            "account_type": account.account_type if account else "Savings",
            "currency": account.currency if account else "USD",
            "status": account.status if account else "Active",
        },
        "transactions": transactions,
    })
