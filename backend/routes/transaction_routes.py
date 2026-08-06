from flask import Blueprint, jsonify, request
from database import db
from models.account import Account
from models.transaction import Transaction
from models.user import User
from models.admin_settings import AdminSettings
import uuid
from datetime import datetime

transaction_bp = Blueprint("transaction", __name__)


def get_owner_status(account):
    if not account:
        return None
    user = User.query.get(account.user_id)
    if not user:
        return None
    return getattr(user, "status", "Active") or "Active"


def is_frozen(account):
    status = get_owner_status(account)
    return status and status.lower() == "frozen"


def get_settings():
    s = AdminSettings.query.first()
    if not s:
        s = AdminSettings(
            imf_code="IMF-0000",
            cot_code="COT-0000",
            require_imf=True,
            require_cot=True,
        )
        db.session.add(s)
        db.session.commit()
    return s


def validate_codes(data):
    settings = get_settings()
    if getattr(settings, "require_imf", True):
        imf = (data.get("imf_code") or "").strip()
        if not imf or imf != (settings.imf_code or "").strip():
            return "Invalid IMF code"
    if getattr(settings, "require_cot", True):
        cot = (data.get("cot_code") or "").strip()
        if not cot or cot != (settings.cot_code or "").strip():
            return "Invalid COT code"
    return None


@transaction_bp.route("/api/transactions/<int:account_id>", methods=["GET"])
def get_transactions(account_id):
    transactions = (
        Transaction.query.filter_by(account_id=account_id)
        .order_by(Transaction.date.desc())
        .all()
    )
    result = []
    for tx in transactions:
        result.append({
            "id": tx.id,
            "reference": tx.transaction_reference,
            "description": tx.description,
            "amount": tx.amount,
            "type": tx.transaction_type,
            "related_account": tx.related_account,
            "balance_after": tx.balance_after,
            "status": tx.status,
            "date": tx.date.isoformat() if tx.date else None,
        })
    return jsonify(result)


@transaction_bp.route("/api/admin/transactions", methods=["GET"])
def admin_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    result = []
    for tx in transactions:
        account = Account.query.get(tx.account_id)
        customer = None
        account_number = None
        if account:
            account_number = account.account_number
            user = User.query.get(account.user_id)
            if user:
                customer = user.name
        result.append({
            "id": tx.id,
            "reference": tx.transaction_reference,
            "customer": customer or "Unknown",
            "account_number": account_number or "N/A",
            "description": tx.description,
            "type": tx.transaction_type,
            "amount": tx.amount,
            "status": tx.status,
            "date": tx.date.isoformat() if tx.date else None,
        })
    return jsonify(result)


@transaction_bp.route("/api/transactions/deposit", methods=["POST"])
def deposit():
    data = request.json or {}
    account_number = data.get("account_number")
    amount = float(data.get("amount", 0) or 0)
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return jsonify({"message": "Account not found"}), 404
    if is_frozen(account):
        return jsonify({"message": "This account is frozen. Transactions are not allowed."}), 403
    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400
    account.balance += amount
    reference = str(uuid.uuid4())[:12].upper()
    tx = Transaction(
        account_id=account.id,
        transaction_reference=reference,
        description="Cash Deposit",
        amount=amount,
        transaction_type="Deposit",
        balance_after=account.balance,
        created_by="Customer",
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"message": "Deposit successful", "reference": reference, "balance": account.balance})


@transaction_bp.route("/api/transactions/withdraw", methods=["POST"])
def withdraw():
    data = request.json or {}
    account_number = data.get("account_number")
    amount = float(data.get("amount", 0) or 0)
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return jsonify({"message": "Account not found"}), 404
    if is_frozen(account):
        return jsonify({"message": "This account is frozen. Transactions are not allowed."}), 403
    if amount <= 0 or account.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    account.balance -= amount
    reference = str(uuid.uuid4())[:12].upper()
    tx = Transaction(
        account_id=account.id,
        transaction_reference=reference,
        description="Cash Withdrawal",
        amount=amount,
        transaction_type="Withdrawal",
        balance_after=account.balance,
        created_by="Customer",
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"message": "Withdrawal successful", "balance": account.balance, "reference": reference})


@transaction_bp.route("/api/transactions/transfer", methods=["POST"])
def transfer():
    data = request.json or {}
    sender_number = data.get("from_account")
    receiver_number = (data.get("to_account") or "").strip()
    amount = float(data.get("amount", 0) or 0)
    transfer_type = (data.get("transfer_type") or "local").lower()  # local | international
    bank_name = (data.get("bank_name") or "").strip()
    beneficiary_name = (data.get("beneficiary_name") or "").strip()

    sender = Account.query.filter_by(account_number=sender_number).first()
    if not sender:
        return jsonify({"message": "Sender account not found"}), 404

    if is_frozen(sender):
        return jsonify({"message": "Your account is frozen. Transactions are not allowed."}), 403

    code_error = validate_codes(data)
    if code_error:
        return jsonify({"message": code_error}), 403

    if amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400
    if sender.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400

    sender_user = User.query.get(sender.user_id)
    out_ref = str(uuid.uuid4())[:12].upper()
    now = datetime.utcnow()

    # ---------- LOCAL (NovaBank → NovaBank) ----------
    if transfer_type == "local":
        receiver = Account.query.filter_by(account_number=receiver_number).first()
        if not receiver:
            return jsonify({"message": "Receiver NovaBank account not found"}), 404
        if is_frozen(receiver):
            return jsonify({"message": "Receiver account is frozen. Transfer not allowed."}), 403

        sender.balance -= amount
        receiver.balance += amount
        in_ref = str(uuid.uuid4())[:12].upper()

        db.session.add_all([
            Transaction(
                account_id=sender.id,
                transaction_reference=out_ref,
                description=f"Local transfer to {receiver.account_number}",
                amount=amount,
                transaction_type="Transfer Out",
                related_account=receiver.account_number,
                balance_after=sender.balance,
                created_by="Customer",
                status="Completed",
            ),
            Transaction(
                account_id=receiver.id,
                transaction_reference=in_ref,
                description=f"Local transfer from {sender.account_number}",
                amount=amount,
                transaction_type="Transfer In",
                related_account=sender.account_number,
                balance_after=receiver.balance,
                created_by="Customer",
                status="Completed",
            ),
        ])
        db.session.commit()

        return jsonify({
            "message": "Transfer successful",
            "status": "Completed",
            "transfer_type": "local",
            "reference": out_ref,
            "amount": amount,
            "from_account": sender.account_number,
            "to_account": receiver.account_number,
            "bank_name": "NovaBank",
            "beneficiary_name": None,
            "sender_name": sender_user.name if sender_user else None,
            "sender_balance": sender.balance,
            "date": now.isoformat(),
        })

    # ---------- INTERNATIONAL ----------
    if not bank_name:
        return jsonify({"message": "Select a destination bank / service"}), 400
    if not receiver_number:
        return jsonify({"message": "Enter beneficiary account / wallet ID"}), 400

    sender.balance -= amount
    desc = f"International transfer via {bank_name} to {receiver_number}"
    if beneficiary_name:
        desc += f" ({beneficiary_name})"

    db.session.add(
        Transaction(
            account_id=sender.id,
            transaction_reference=out_ref,
            description=desc,
            amount=amount,
            transaction_type="International Transfer",
            related_account=f"{bank_name}:{receiver_number}",
            balance_after=sender.balance,
            created_by="Customer",
            status="Completed",
        )
    )
    db.session.commit()

    return jsonify({
        "message": "Transfer successful",
        "status": "Completed",
        "transfer_type": "international",
        "reference": out_ref,
        "amount": amount,
        "from_account": sender.account_number,
        "to_account": receiver_number,
        "bank_name": bank_name,
        "beneficiary_name": beneficiary_name or None,
        "sender_name": sender_user.name if sender_user else None,
        "sender_balance": sender.balance,
        "date": now.isoformat(),
    })
