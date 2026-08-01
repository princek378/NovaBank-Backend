from database import db

from models.user import User
from models.account import Account

from utils.account_generator import generate_account_number



def create_customer(data):

    user = User(

        first_name=data["first_name"],

        last_name=data["last_name"],

        email=data["email"],

        password_hash=data["password"],

        phone=data.get("phone",""),

        country=data.get("country",""),

        address=data.get("address",""),

        status="Active",

        is_verified=True

    )


    db.session.add(user)

    db.session.commit()



    account = Account(

        user_id=user.id,

        account_number=generate_account_number(),

        account_type=data.get(
            "account_type",
            "Personal"
        ),

        balance=data.get(
            "balance",
            0
        ),

        currency="USD",

        status="Active"

    )


    db.session.add(account)

    db.session.commit()


    return user, account