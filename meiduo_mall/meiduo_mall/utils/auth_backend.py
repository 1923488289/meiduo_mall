import re
from django.contrib.auth.backends import ModelBackend
from users.models import User


class Meiduobackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r'1[3-9]\d{9}', username):
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(mobile=username)
        except:
            return None
        else:
            user.check_password(user)
