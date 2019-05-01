from django.utils.six import wraps
from django import http
from meiduo_mall.utils.response_code import RETCODE


def login_required_json(view_func):
    # 恢复view_func 的名字和文档
    @wraps(view_func)
    def wrapper(request, **kwargs):
        if not request.user.is_authenticated():
            return http.JsonResponse({
                'code': RETCODE.SESSIONERR,
                'errmsg': '用户为登录'
            })
        else:
            return view_func(request,**kwargs)

    return wrapper


class LoginRequiredJSONMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        view = login_required_json(view)
        return view

