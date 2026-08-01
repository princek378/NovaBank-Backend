from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from database import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.message import Message
from models.notification import Notification
import uuid



admin_bp = Blueprint(
    "admin",
    __name__
)





# =====================================
# DASHBOARD STATS
# =====================================

@admin_bp.route(
    "/api/admin/stats",
    methods=["GET"]
)
def admin_stats():


    customers = User.query.count()


    accounts = Account.query.count()



    balance = db.session.query(
        db.func.sum(Account.balance)
    ).scalar() or 0



    return jsonify({

        "customers": customers,

        "accounts": accounts,

        "balance": balance

    })









# =====================================
# GET ALL CUSTOMERS
# =====================================

@admin_bp.route(
    "/api/admin/customers",
    methods=["GET"]
)
def get_customers():


    users = User.query.all()


    result=[]



    for user in users:


        account = Account.query.filter_by(
            user_id=user.id
        ).first()



        result.append({

            "id":
            user.id,


            "name":
            user.name,


            "email":
            user.email,


            "phone":
            user.phone,


            "status":
            getattr(
                user,
                "status",
                "Active"
            ),


            "account_number":
            account.account_number
            if account
            else "N/A"



        })



    return jsonify(result)









# =====================================
# GET CUSTOMER PROFILE
# =====================================

@admin_bp.route(
    "/api/admin/customers/<int:id>",
    methods=["GET"]
)
def get_customer_profile(id):


    user = User.query.get(id)



    if not user:


        return jsonify({

            "message":
            "Customer not found"

        }),404






    account = Account.query.filter_by(
        user_id=user.id
    ).first()






    return jsonify({


        "id":
        user.id,


        "name":
        user.name,


        "email":
        user.email,


        "phone":
        user.phone,


        "address":
        user.address,


        "role":
        user.role,


        "status":
        getattr(
            user,
            "status",
            "Active"
        ),



        "account":{


            "account_number":
            account.account_number
            if account
            else "N/A",


            "account_type":
            account.account_type
            if account
            else "Savings",


            "balance":
            account.balance
            if account
            else 0,


            "currency":
            account.currency
            if account
            else "USD"


        }


    })









# =====================================
# CREATE CUSTOMER
# =====================================

@admin_bp.route(
    "/api/admin/customers",
    methods=["POST"]
)
def create_customer():


    data=request.get_json()



    first_name=data.get(
        "first_name"
    )


    last_name=data.get(
        "last_name"
    )


    email=data.get(
        "email"
    )


    password=data.get(
        "password"
    )


    phone=data.get(
        "phone"
    )


    address=data.get(
        "address"
    )


    account_type=data.get(
        "account_type",
        "Savings"
    )


    balance=float(
        data.get(
            "balance",
            0
        )
    )





    if not first_name or not last_name or not email or not password:


        return jsonify({

            "message":
            "Required fields missing"

        }),400






    exists = User.query.filter_by(
        email=email
    ).first()



    if exists:


        return jsonify({

            "message":
            "Email already exists"

        }),400






    user = User(

        name=
        first_name+" "+last_name,

        email=email,

        password=generate_password_hash(password),

        phone=phone,

        address=address,

        role="Customer"

    )



    if hasattr(user,"status"):

        user.status="Active"




    db.session.add(user)

    db.session.commit()







    account_number = (

        "NB"

        +

        str(uuid.uuid4().int)[:10]

    )






    account = Account(

        user_id=user.id,

        account_number=account_number,

        account_type=account_type,

        balance=balance

    )



    db.session.add(account)

    db.session.commit()





    return jsonify({

        "message":
        "Customer created successfully",

        "account_number":
        account_number

    }),201







# =====================================
# FREEZE CUSTOMER
# =====================================

@admin_bp.route(
    "/api/admin/customers/<int:id>/freeze",
    methods=["PUT"]
)
def freeze_customer(id):


    user=User.query.get(id)



    if not user:

        return jsonify({

            "message":
            "Customer not found"

        }),404



    if hasattr(user,"status"):

        user.status="Frozen"



    db.session.commit()



    return jsonify({

        "message":
        "Customer frozen"

    })









# =====================================
# UNFREEZE CUSTOMER
# =====================================

@admin_bp.route(
    "/api/admin/customers/<int:id>/unfreeze",
    methods=["PUT"]
)
def unfreeze_customer(id):


    user=User.query.get(id)



    if not user:

        return jsonify({

            "message":
            "Customer not found"

        }),404



    if hasattr(user,"status"):

        user.status="Active"



    db.session.commit()



    return jsonify({

        "message":
        "Customer unfrozen"

    })



# =====================================
# DELETE CUSTOMER
# =====================================

@admin_bp.route("/api/admin/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    """Remove a customer and all related banking data."""
    from sqlalchemy import text as sql_text

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({"message": "Customer not found"}), 404

    if (getattr(user, "role", None) or "") == "Admin":
        return jsonify({"message": "Cannot delete admin account"}), 400

    try:
        # Use raw deletes for reliability with SQLite FK constraints
        accounts = Account.query.filter_by(user_id=user.id).all()
        account_ids = [a.id for a in accounts]

        if account_ids:
            # delete transactions linked to these accounts
            for aid in account_ids:
                db.session.execute(
                    sql_text("DELETE FROM \"transaction\" WHERE account_id = :aid"),
                    {"aid": aid},
                )
            for aid in account_ids:
                db.session.execute(
                    sql_text("DELETE FROM account WHERE id = :aid"),
                    {"aid": aid},
                )

        # messages table name is usually "message"
        try:
            db.session.execute(
                sql_text("DELETE FROM message WHERE user_id = :uid"),
                {"uid": user.id},
            )
        except Exception as e:
            print("message delete skip:", e)

        try:
            db.session.execute(
                sql_text("DELETE FROM notifications WHERE user_id = :uid"),
                {"uid": user.id},
            )
        except Exception as e:
            print("notifications delete skip:", e)

        try:
            db.session.execute(
                sql_text("DELETE FROM notification WHERE user_id = :uid"),
                {"uid": user.id},
            )
        except Exception as e:
            print("notification delete skip:", e)

        db.session.execute(
            sql_text("DELETE FROM user WHERE id = :uid"),
            {"uid": user.id},
        )
        db.session.commit()

        return jsonify({"message": "Customer deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print("Delete error:", repr(e))
        return jsonify({
            "message": "Failed to delete customer",
            "error": str(e)
        }), 500
