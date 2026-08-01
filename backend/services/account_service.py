from models.account import Account



def get_account(user_id):

    return Account.query.filter_by(

        user_id=user_id

    ).first()