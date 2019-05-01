import re
from django.contrib.auth.backends import ModelBackend
from users.models import User


# 实现多帐号登录
class Meiduobackend(ModelBackend):
    # 重写authenticate这个类
    def authenticate(self, request, username=None, password=None, **kwargs):

        try:
            if re.match(r'1[3-9]\d{9}', username):

                user = User.objects.get(mobile=username)

            else:
                user = User.objects.get(username=username)

        except:
            return None
        else:
            # 加密验证密码是否正确
            user.check_password(user)
            return user

