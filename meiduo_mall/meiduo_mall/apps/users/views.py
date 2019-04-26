from django.shortcuts import render
from django.views.generic import View
from django import http
import re
from django.contrib.auth import login
from django_redis import get_redis_connection

# from pymysql import DatabaseError

from users.models import User


class MyClass(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        allow = request.POST.get('allow')
        sms_code = request.POST.get('msg_code')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow, sms_code]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if User.objects.filter(username=username).count() > 0:
            return http.HttpResponseForbidden('用户名已经存在')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        if User.objects.filter(mobile=mobile).count() > 0:
            return http.HttpResponseForbidden('手机号已经存在')
        #获取链接对象
        redis_conn = get_redis_connection('verificat_code')
        #取出值
        redis_server_m = redis_conn.get('sms_' + mobile)
        # print(redis_server_m+'redis')

        if redis_server_m is None:
            return http.HttpResponseBadRequest('验证码过期')
        if sms_code !=redis_server_m.decode():
            return http.HttpResponseBadRequest('验证码不正确')
        redis_conn.delete('sms_' + mobile)

        # cc创建对象写数据库，create_user 的作用都密码加密，且能写入数据库。
        # 他和create的区别是crate_user 继承了AbstractUser，这里面有加密的方法，
        # 而create 集成的models没有加密的方法，create_user继承了认证类
        user = User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )
        # 状态保持 将注册的信息临时性保存在session中将session保存在缓冲中，
        # 将缓冲保存在redis数据库中，
        login(request, user)
        return http.HttpResponse('注册成功，重定向到首页')


class UserView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        # Jsonresponse 1、已经将数据转为json字符串了2、content-type 已经转为applicattion/json
        return http.JsonResponse({'count': count})


class MobilView(View):
    def get(self, request, phone):
        count = User.objects.filter(mobile=phone).count()
        return http.JsonResponse(
            {'count': count}
        )
