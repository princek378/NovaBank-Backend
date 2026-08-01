from flask import Blueprint, jsonify, request

from database import db

from models.account import Account


account_bp = Blueprint(
    "account",
    __name__,
    url_prefix="/api/account"
)


# Test account route
@account_bp.route("/test", methods=["GET"])
def test_account():

    return jsonify({
        "message": "Account route working"
    })



# Get all accounts
@account_bp.route("/", methods=["GET"])
def get_accounts():

    accounts = Account.query.all()

    account_list = []


    for account in accounts:

        account_list.append({

            "id": account.id,

            "account_number": account.account_number,

            "balance": account.balance,

            "status": getattr(account, "status", "Active")

        })


    return jsonify(account_list)



# Get single account
@account_bp.route("/<int:id>", methods=["GET"])
def get_account(id):

    account = Account.query.get(id)


    if not account:

        return jsonify({

            "message": "Account not found"

        }), 404



    return jsonify({

        "id": account.id,

        "account_number": account.account_number,

        "balance": account.balance,

        "status": getattr(account, "status", "Active")

    })



# Create account
@account_bp.route("/create", methods=["POST"])
def create_account():

    data = request.get_json()


    new_account = Account(

        account_number=data.get("account_number"),

        balance=data.get("balance", 0),

        status="Active"

    )


    db.session.add(new_account)

    db.session.commit()



    return jsonify({

        "message": "Account created successfully"

    }), 201