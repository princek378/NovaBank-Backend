from flask import Blueprint, jsonify, request

from database import db

from models.admin_settings import AdminSettings



settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/settings"
)





@settings_bp.route(
    "",
    methods=["GET"]
)
def get_settings():


    settings = AdminSettings.query.first()



    if not settings:


        settings = AdminSettings(

            admin_name="Administrator",

            email="admin@novabank.com",

            bank_name="NovaBank",

            currency="USD"

        )


        db.session.add(settings)

        db.session.commit()






    return jsonify({


        "admin_name":

        settings.admin_name,



        "email":

        settings.email,



        "bank_name":

        settings.bank_name,



        "currency":

        settings.currency


    })







@settings_bp.route(
    "",
    methods=["PUT"]
)
def update_settings():


    data=request.get_json()



    settings=AdminSettings.query.first()



    if not settings:


        settings=AdminSettings()

        db.session.add(settings)





    settings.admin_name = data.get(
        "admin_name",
        settings.admin_name
    )


    settings.email=data.get(
        "email",
        settings.email
    )


    settings.bank_name=data.get(
        "bank_name",
        settings.bank_name
    )


    settings.currency=data.get(
        "currency",
        settings.currency
    )



    db.session.commit()



    return jsonify({

        "message":

        "Settings updated"

    })