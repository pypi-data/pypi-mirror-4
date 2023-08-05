from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from eggplant.constants.settings import USER_TOKEN_CLASS
from eggplant.utils import import_from_string

class TokenBackend(ModelBackend):
    def authenticate(self, token=None):
        token_class_path = getattr(settings, USER_TOKEN_CLASS, 'eggplant.auth.token.UserToken')
        UserToken = import_from_string(token_class_path)

        # Check User
        user_token_handler = UserToken()
        if user_token_handler.validator(token):
            return user_token_handler.user_from_token(token)
        else:
            return None