import re
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from meiduo_mall.utils.response_code import RETCODE
from auoth.models import QAuthQQUser
from meiduo_mall.utils import itsdangerous
from . import constants
from django_redis import get_redis_connection
from users.models import User
from django.contrib.auth import login


# 向服务器获取qq授权地址
class QQcodeView(View):
    def get(self, request):
        # 登录成功后在回到这个页面去
        next_url = request.GET.get('next')
        # 创建工具对象
        qq_tool = OAuthQQ(
            # id,应用的唯一标识
            settings.QQ_CLIENT_ID,
            # key appid的密钥
            settings.QQ_CLIENT_SECRET,
            # 生成授权地址，包括回调地址,应用中设置好的
            settings.QQ_REDIRECT_URI,
            #
            next_url
        )

        # 调用方法，生成授权登录的url地址,
        login_url = qq_tool.get_qq_url()
        print(login_url + '------------------')
        return http.JsonResponse(
            {
                'code': RETCODE.OK,
                'errmsg': 'ok',
                # 授权地址，即qq登录扫码页面链接
                'login_url': login_url
            }
        )


class OpendidView(View):
    def get(self, request):
        # code 只能用一次，要是再用，需要重新获取
        code = request.GET.get('code')
        next_url = request.GET.get('state')
        # 创建工具对象
        qq_tool = OAuthQQ(
            # id
            settings.QQ_CLIENT_ID,
            # key
            settings.QQ_CLIENT_SECRET,
            # 回调地址
            settings.QQ_REDIRECT_URI,
            #
            next_url
        )
        try:
            # 获取token
            token = qq_tool.get_access_token(code)
            # 获取openid,对网站货应用用户的唯一标识
            openid = qq_tool.get_open_id(token)
        except:
            openid = 0
            # return http.HttpResponse(openid)
            return http.HttpResponseBadRequest('OAutg2.0认证错误')
        else:
            try:
                oauth_user = QAuthQQUser.objects.get(openid=openid)
            except:
                # openid 没有绑定到美多
                # 初次授权
                # access_token = generate_eccess_token(openid)
                # 进行加密
                token = itsdangerous.dumps({'openid': openid}, constants.OPENID_EXPIRES)
                context = {'token': token}

                return render(request, 'oauth_callback.html', context)
                pass
            else:
                # 根据外键 得到一个用户的信息
                qq_user = oauth_user.user
                # 状态保持
                login(request, qq_user)
                response = redirect('/')
                response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
                return response

    def post(self, request):
        # 接收
        mobile = request.POST.get('mobile')
        password = request.POST.get('pwd')
        token = request.POST.get('access_token')
        sms_code = request.POST.get('sms_code')
        # 验证
        print('------mobile====' + mobile)
        print('=======password++++++' + password)
        print('===========token===' + token)
        if not all([mobile, password, sms_code]):
            return http.HttpResponseBadRequest('缺少必须参数')
        if not re.match(r'^1[345789]\d{9}', mobile):
            return http.HttpResponseBadRequest('您输入的手机号格式不正确')
        if not re.match(r'[0-9A-Za-z]{8,20}', password):
            return http.HttpResponseBadRequest('密码错误')
        # 获取链接对象
        redis_cli = get_redis_connection('verificat_code')
        #
        redis_cli_request = redis_cli.get('sms_' + mobile)
        if redis_cli_request is None:
            return http.HttpResponseBadRequest('短信验证码过期')
        if redis_cli_request.decode() != sms_code:
            return http.HttpResponseBadRequest('短信验证码错误')
        # 解密
        json = itsdangerous.loads(token, constants.OPENID_EXPIRES)
        if json is None:
            return http.HttpResponse('授权信息已经过期')
        openid = json.get('openid')
        # 处理
        try:
            user = User.objects.get(mobile=mobile)
        except:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
            login(request, user)
            response = redirect('/')
            response.set_cookie('username', user.username, max_age=60 * 60 * 24 * 14)

            return response
        else:
            # 判断密码
            if not user.check_password(password):
                return http.HttpResponseBadRequest('帐号的信息失效')
            # 写道数据库
            QAuthQQUser.objects.create(openid=openid, user=user)
            login(request, user)
            response = redirect('/')
            response.set_cookie('user', user.username, max_age=60 * 60 * 24 * 14)
            return response

# class OauthView(View):
#     def get(self, request):
#         return render(request, 'oauth_callback.html')
