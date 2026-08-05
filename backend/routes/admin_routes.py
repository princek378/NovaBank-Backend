from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from database import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from datetime import datetime
import uuid

admin_bp = Blueprint("admin", __name__)


def parse_date(value):
    if not value:
        return None
    try:
        # accepts "2026-08-05" or full ISO
        return datetime.fromisoformat(str(value).replace("Z", ""))
    except Exception:
        return None


# =====================================
# DASHBOARD STATS
# =====================================
@admin_bp.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    customers = User.query.filter(User.role != "Admin").count()
    accounts = Account.query.count()
    balance = db.session.query(db.func.sum(Account.balance)).scalar() or 0
    return jsonify({
        "customers": customers,
        "accounts": accounts,
        "balance": balance,
    })


# =====================================
# GET ALL CUSTOMERS
# =====================================
@admin_bp.route("/api/admin/customers", methods=["GET"])
def get_customers():
    users = User.query.filter(User.role != "Admin").all()
    result = []
    for user in users:
        account = Account.query.filter_by(user_id=user.id).first()
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "status": getattr(user, "status", "Active"),
            "account_number": account.account_number if account else "N/A",
            "balance": account.balance if account else 0,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    return jsonify(result)


# =====================================
# GET CUSTOMER PROFILE (+ transactions)
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>", methods=["GET"])
def get_customer_profile(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404

    account = Account.query.filter_by(user_id=user.id).first()
    transactions = []
    if account:
        txs = (
            Transaction.query.filter_by(account_id=account.id)
            .order_by(Transaction.date.desc())
            .all()
        )
        for tx in txs:
            transactions.append({
                "id": tx.id,
                "reference": tx.transaction_reference,
                "description": tx.description,
                "amount": tx.amount,
                "type": tx.transaction_type,
                "related_account": tx.related_account,
                "balance_after": tx.balance_after,
                "status": tx.status,
                "created_by": tx.created_by,
                "date": tx.date.isoformat() if tx.date else None,
            })

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "role": user.role,
        "status": getattr(user, "status", "Active"),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "account": {
            "id": account.id if account else None,
            "account_number": account.account_number if account else "N/A",
            "account_type": account.account_type if account else "Savings",
            "balance": account.balance if account else 0,
            "currency": account.currency if account else "USD",
            "status": account.status if account else "Active",
            "created_at": account.created_at.isoformat() if account and account.created_at else None,
        },
        "transactions": transactions,
    })


# =====================================
# UPDATE CUSTOMER + ACCOUNT DETAILS
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"]:
        user.name = data["name"].strip()
    if "email" in data and data["email"]:
        email = data["email"].strip().lower()
        exists = User.query.filter(User.email == email, User.id != user.id).first()
        if exists:
            return jsonify({"message": "Email already in use"}), 400
        user.email = email
    if "phone" in data:
        user.phone = data["phone"]
    if "address" in data:
        user.address = data["address"]
    if "status" in data and data["status"]:
        user.status = data["status"]
    if "created_at" in data:
        parsed = parse_date(data["created_at"])
        if parsed:
            user.created_at = parsed
    if data.get("password"):
        user.password = generate_password_hash(data["password"])

    account = Account.query.filter_by(user_id=user.id).first()
    if account:
        if "account_number" in data and data["account_number"]:
            new_num = str(data["account_number"]).strip()
            taken = Account.query.filter(
                Account.account_number == new_num, Account.id != account.id
            ).first()
            if taken:
                return jsonify({"message": "Account number already in use"}), 400
            account.account_number = new_num
        if "account_type" in data and data["account_type"]:
            account.account_type = data["account_type"]
        if "currency" in data and data["currency"]:
            account.currency = data["currency"]
        if "account_status" in data and data["account_status"]:
            account.status = data["account_status"]
        if "account_created_at" in data:
            parsed = parse_date(data["account_created_at"])
            if parsed:
                account.created_at = parsed
        if "balance" in data and data["balance"] is not None:
            try:
                account.balance = float(data["balance"])
            except (TypeError, ValueError):
                pass

    db.session.commit()
    return jsonify({"message": "Customer updated successfully"})


# =====================================
# CREATE CUSTOMER
# =====================================
@admin_bp.route("/api/admin/customers", methods=["POST"])
def create_customer():
    data = request.get_json() or {}
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    address = data.get("address")
    account_type = data.get("account_type", "Savings")
    balance = float(data.get("balance", 0) or 0)

    if not first_name or not last_name or not email or not password:
        return jsonify({"message": "Required fields missing"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(
        name=f"{first_name} {last_name}",
        email=email,
        password=generate_password_hash(password),
        phone=phone,
        address=address,
        role="Customer",
        status="Active",
    )
    db.session.add(user)
    db.session.commit()

    account_number = "NB" + str(uuid.uuid4().int)[:10]
    account = Account(
        user_id=user.id,
        account_number=account_number,
        account_type=account_type,
        balance=balance,
    )
    db.session.add(account)
    db.session.commit()

    return jsonify({
        "message": "Customer created successfully",
        "account_number": account_number,
    }), 201


# =====================================
# ADMIN DEPOSIT
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>/deposit", methods=["POST"])
def admin_deposit(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    account = Account.query.filter_by(user_id=user.id).first()
    if not account:
        return jsonify({"message": "Account not found"}), 404

    data = request.get_json() or {}
    amount = float(data.get("amount", 0) or 0)
    description = (data.get("description") or "Admin Deposit").strip()
    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400

    account.balance += amount
    ref = str(uuid.uuid4())[:12].upper()
    tx = Transaction(
        account_id=account.id,
        transaction_reference=ref,
        description=description,
        amount=amount,
        transaction_type="Deposit",
        balance_after=account.balance,
        created_by="Admin",
        status="Completed",
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"message": "Deposit successful", "balance": account.balance, "reference": ref})


# =====================================
# ADMIN WITHDRAW
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>/withdraw", methods=["POST"])
def admin_withdraw(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    account = Account.query.filter_by(user_id=user.id).first()
    if not account:
        return jsonify({"message": "Account not found"}), 404

    data = request.get_json() or {}
    amount = float(data.get("amount", 0) or 0)
    description = (data.get("description") or "Admin Withdrawal").strip()
    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400
    if account.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

    account.balance -= amount
    ref = str(uuid.uuid4())[:12].upper()
    tx = Transaction(
        account_id=account.id,
        transaction_reference=ref,
        description=description,
        amount=amount,
        transaction_type="Withdrawal",
        balance_after=account.balance,
        created_by="Admin",
        status="Completed",
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"message": "Withdrawal successful", "balance": account.balance, "reference": ref})


# =====================================
# ADMIN TRANSFER (from this customer to another account)
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>/transfer", methods=["POST"])
def admin_transfer(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    sender = Account.query.filter_by(user_id=user.id).first()
    if not sender:
        return jsonify({"message": "Account not found"}), 404

    data = request.get_json() or {}
    to_account = (data.get("to_account") or "").strip()
    amount = float(data.get("amount", 0) or 0)
    description = (data.get("description") or "Admin Transfer").strip()

    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400
    receiver = Account.query.filter_by(account_number=to_account).first()
    if not receiver:
        return jsonify({"message": "Receiver account not found"}), 404
    if sender.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

    sender.balance -= amount
    receiver.balance += amount
    out_ref = str(uuid.uuid4())[:12].upper()
    in_ref = str(uuid.uuid4())[:12].upper()

    db.session.add_all([
        Transaction(
            account_id=sender.id,
            transaction_reference=out_ref,
            description=description or "Transfer Out",
            amount=amount,
            transaction_type="Transfer Out",
            related_account=receiver.account_number,
            balance_after=sender.balance,
            created_by="Admin",
        ),
        Transaction(
            account_id=receiver.id,
            transaction_reference=in_ref,
            description="Transfer In",
            amount=amount,
            transaction_type="Transfer In",
            related_account=sender.account_number,
            balance_after=receiver.balance,
            created_by="Admin",
        ),
    ])
    db.session.commit()
    return jsonify({
        "message": "Transfer successful",
        "sender_balance": sender.balance,
        "receiver_balance": receiver.balance,
    })


# =====================================
# UPDATE TRANSACTION
# =====================================
@admin_bp.route("/api/admin/transactions/<int:tx_id>", methods=["PUT"])
def update_transaction(tx_id):
    tx = Transaction.query.get(tx_id)
    if not tx:
        return jsonify({"message": "Transaction not found"}), 404

    data = request.get_json() or {}
    if "description" in data:
        tx.description = data["description"]
    if "amount" in data and data["amount"] is not None:
        tx.amount = float(data["amount"])
    if "type" in data and data["type"]:
        tx.transaction_type = data["type"]
    if "status" in data and data["status"]:
        tx.status = data["status"]
    if "related_account" in data:
        tx.related_account = data["related_account"]
    if "balance_after" in data and data["balance_after"] is not None:
        tx.balance_after = float(data["balance_after"])
    if "reference" in data and data["reference"]:
        tx.transaction_reference = data["reference"]
    if "date" in data:
        parsed = parse_date(data["date"])
        if parsed:
            tx.date = parsed
    if "created_by" in data:
        tx.created_by = data["created_by"]

    db.session.commit()
    return jsonify({"message": "Transaction updated"})


# =====================================
# DELETE TRANSACTION
# =====================================
@admin_bp.route("/api/admin/transactions/<int:tx_id>", methods=["DELETE"])
def delete_transaction(tx_id):
    tx = Transaction.query.get(tx_id)
    if not tx:
        return jsonify({"message": "Transaction not found"}), 404
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})


# =====================================
# FREEZE / UNFREEZE
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>/freeze", methods=["PUT"])
def freeze_customer(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    user.status = "Frozen"
    db.session.commit()
    return jsonify({"message": "Customer frozen"})


@admin_bp.route("/api/admin/customers/<int:id>/unfreeze", methods=["PUT"])
def unfreeze_customer(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    user.status = "Active"
    db.session.commit()
    return jsonify({"message": "Customer unfrozen"})


# =====================================
# DELETE CUSTOMER
# =====================================
@admin_bp.route("/api/admin/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    from sqlalchemy import text as sql_text

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({"message": "Customer not found"}), 404
    if (getattr(user, "role", None) or "") == "Admin":
        return jsonify({"message": "Cannot delete admin account"}), 400

    try:
        accounts = Account.query.filter_by(user_id=user.id).all()
        account_ids = [a.id for a in accounts]
        if account_ids:
            for aid in account_ids:
                db.session.execute(
                    sql_text('DELETE FROM "transaction" WHERE account_id = :aid'),
                    {"aid": aid},
                )
            for aid in account_ids:
                db.session.execute(
                    sql_text("DELETE FROM account WHERE id = :aid"),
                    {"aid": aid},
                )
        try:
            db.session.execute(
                sql_text("DELETE FROM message WHERE user_id = :uid"),
                {"uid": user.id},
            )
        except Exception:
            pass
        try:
            db.session.execute(
                sql_text("DELETE FROM notification WHERE user_id = :uid"),
                {"uid": user.id},
            )
        except Exception:
            pass
        db.session.execute(
            sql_text('DELETE FROM "user" WHERE id = :uid'),
            {"uid": user.id},
        )
        db.session.commit()
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete customer", "error": str(e)}), 500
