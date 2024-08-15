# To handle the secret keys
from decouple import config


def get_secret_key(key_name):
    """
    Get the secret key from environment variable or prompt user input.
    """
    key = config(key_name, default=None)
    if not key:
        key = input(f"Enter {key_name}: ")
    return key

class secrets:
    def __init__(self):
        self.variables = [
            'BOT_TOKEN',
            'DB_USERNAME',
            'DB_PASSWORD',
            'BHARATPE_TOKEN',
            'COOK_API_TOKEN'
        ]

        for i in self.variables:
            setattr(self, i, get_secret_key(i))

secrets = secrets()
