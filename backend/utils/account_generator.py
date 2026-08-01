import random


def generate_account_number():

    return str(
        random.randint(
            1000000000,
            9999999999
        )
    )