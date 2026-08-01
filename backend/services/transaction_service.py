from models.transaction import Transaction



def get_transactions(account_id):

    return Transaction.query.filter_by(

        account_id=account_id

    ).all()