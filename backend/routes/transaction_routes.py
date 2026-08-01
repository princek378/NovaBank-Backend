from flask import Blueprint, jsonify, request

from database import db

from models.account import Account
from models.transaction import Transaction
from models.user import User

import uuid



transaction_bp = Blueprint(
    "transaction",
    __name__
)



# =====================================
# CUSTOMER TRANSACTION HISTORY
# =====================================

@transaction_bp.route(
    "/api/transactions/<int:account_id>",
    methods=["GET"]
)
def get_transactions(account_id):


    transactions = Transaction.query.filter_by(
        account_id=account_id
    ).order_by(
        Transaction.date.desc()
    ).all()



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

            "date": tx.date.isoformat()

        })



    return jsonify(result)






# =====================================
# ADMIN ALL TRANSACTIONS
# =====================================

@transaction_bp.route(
    "/api/admin/transactions",
    methods=["GET"]
)
def admin_transactions():


    transactions = Transaction.query.order_by(
        Transaction.date.desc()
    ).all()



    result = []



    for tx in transactions:


        account = Account.query.get(
            tx.account_id
        )


        customer = None

        account_number = None



        if account:


            account_number = account.account_number


            user = User.query.get(
                account.user_id
            )


            if user:

                customer = user.name





        result.append({

            "id": tx.id,

            "reference":
            tx.transaction_reference,


            "customer":
            customer or "Unknown",


            "account_number":
            account_number or "N/A",


            "description":
            tx.description,


            "type":
            tx.transaction_type,


            "amount":
            tx.amount,


            "status":
            tx.status,


            "date":
            tx.date.isoformat()

        })




    return jsonify(result)









# =====================================
# DEPOSIT
# =====================================

@transaction_bp.route(
    "/api/transactions/deposit",
    methods=["POST"]
)
def deposit():


    data = request.json


    account_number = data.get(
        "account_number"
    )


    amount = float(
        data.get(
            "amount",
            0
        )
    )



    account = Account.query.filter_by(
        account_number=account_number
    ).first()



    if not account:

        return jsonify({

            "message":
            "Account not found"

        }),404




    if amount <= 0:

        return jsonify({

            "message":
            "Invalid amount"

        }),400




    account.balance += amount



    reference = str(
        uuid.uuid4()
    )[:12].upper()



    tx = Transaction(

        account_id=account.id,

        transaction_reference=reference,

        description="Cash Deposit",

        amount=amount,

        transaction_type="Deposit",

        balance_after=account.balance,

        created_by="Admin"

    )



    db.session.add(tx)

    db.session.commit()



    return jsonify({

        "message":
        "Deposit successful",

        "reference":
        reference,

        "balance":
        account.balance

    })









# =====================================
# WITHDRAW
# =====================================

@transaction_bp.route(
    "/api/transactions/withdraw",
    methods=["POST"]
)
def withdraw():


    data=request.json


    account_number=data.get(
        "account_number"
    )


    amount=float(
        data.get(
            "amount",
            0
        )
    )



    account=Account.query.filter_by(
        account_number=account_number
    ).first()



    if not account:

        return jsonify({

            "message":
            "Account not found"

        }),404




    if amount <=0 or account.balance < amount:


        return jsonify({

            "message":
            "Insufficient balance"

        }),400




    account.balance -= amount



    reference=str(
        uuid.uuid4()
    )[:12].upper()



    tx=Transaction(

        account_id=account.id,

        transaction_reference=reference,

        description="Cash Withdrawal",

        amount=amount,

        transaction_type="Withdrawal",

        balance_after=account.balance,

        created_by="Admin"

    )



    db.session.add(tx)

    db.session.commit()



    return jsonify({

        "message":
        "Withdrawal successful",

        "balance":
        account.balance

    })









# =====================================
# TRANSFER
# =====================================

@transaction_bp.route(
    "/api/transactions/transfer",
    methods=["POST"]
)
def transfer():


    data=request.json


    sender_number=data.get(
        "from_account"
    )


    receiver_number=data.get(
        "to_account"
    )


    amount=float(
        data.get(
            "amount",
            0
        )
    )



    sender=Account.query.filter_by(
        account_number=sender_number
    ).first()



    receiver=Account.query.filter_by(
        account_number=receiver_number
    ).first()



    if not sender or not receiver:

        return jsonify({

            "message":
            "Account not found"

        }),404




    if sender.balance < amount:

        return jsonify({

            "message":
            "Insufficient balance"

        }),400




    sender.balance -= amount

    receiver.balance += amount




    out_ref=str(
        uuid.uuid4()
    )[:12].upper()


    in_ref=str(
        uuid.uuid4()
    )[:12].upper()





    db.session.add_all([


        Transaction(

            account_id=sender.id,

            transaction_reference=out_ref,

            description="Transfer Out",

            amount=amount,

            transaction_type="Transfer Out",

            related_account=receiver.account_number,

            balance_after=sender.balance,

            created_by="Customer"

        ),



        Transaction(

            account_id=receiver.id,

            transaction_reference=in_ref,

            description="Transfer In",

            amount=amount,

            transaction_type="Transfer In",

            related_account=sender.account_number,

            balance_after=receiver.balance,

            created_by="Customer"

        )

    ])




    db.session.commit()



    return jsonify({

        "message":
        "Transfer successful",

        "sender_balance":
        sender.balance,

        "receiver_balance":
        receiver.balance

    })