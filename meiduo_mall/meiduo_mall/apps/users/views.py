import json
from .models import Address
from django.shortcuts import render, redirect
from django.views.generic import View
from django import http
import re
from django.contrib.auth import login, logout, authenticate
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
from meiduo_mall.utils.LogMixin import LoginRequiredJSONMixin
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.email.tasks import send_virify_email
from django.conf import settings
from meiduo_mall.utils import itsdangerous
from . import contants
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
        # 获取链接对象
        redis_conn = get_redis_connection('verificat_code')
        # 取出值
        redis_server_m = redis_conn.get('sms_' + mobile)
        # print(redis_server_m+'redis')

        if redis_server_m is None:
            return http.HttpResponseBadRequest('短信验证码过期')
        if sms_code != redis_server_m.decode():
            return http.HttpResponseBadRequest('短信验证码不正确')
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
        response = redirect('/')
        #将信息保存在帐号保存在浏览器上
        response.set_cookie('username', username, 60 * 60 * 24 * 14)
        return response


# 帐号验证
class UserView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        # Jsonresponse 1、已经将数据转为json字符串了2、content-type 已经转为applicattion/json
        return http.JsonResponse({'count': count})


# 手机号验证 ajax
class MobilView(View):
    def get(self, request, phone):
        count = User.objects.filter(mobile=phone).count()
        return http.JsonResponse(
            {'count': count}
        )


# 登录 /login/
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        # 一个是点击登录，没有next 参数，默认为'/'，
        # 如果实在是点击用户中心登录，再有next参数，然后登录成功后再换回到用户中心
        next_url = request.GET.get('next', '/')
        if not all([pwd, username]):
            return http.HttpResponseBadRequest('缺少必填参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 帐号验证，密码加密后验证，调用的配置中的后端，直到找到方法
        user = authenticate(username=username, password=pwd)
        print(username + '=======' + pwd)
        print(user)
        if user is None:

            return render(request, 'login.html', {
                'loginerror': '用户名或者密码错误'
            })

        else:
            print('-------------------------')
            # 保持状态
            login(request, user)
            # return render(request, '/')
            # return http.HttpResponse('ok')
            response = redirect(next_url)
            # 浏览器带cookie
            response.set_cookie('username', username, 60 * 60 * 24 * 14)

            return response


# 退出 /logout
class LogoutView(View):
    def get(self, request):
        response = redirect('/login/')
        # 本质删除session
        logout(request)
        response.delete_cookie('username')
        return response


# 用户中新 判断用户是否在线如果不在线则进入登录页面验证 /info
# loginrequiredMxin 这已经封装好了，在内部判断用户是否登录，如果没有等直接转到同一个页面去，
# 直接在setting中设置
class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        # 判断用户是否登录
        # if  not request.user.is_authenticated:
        #     return redirect('/login/')
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


# 自定义装饰器，过滤掉未登录的帐号
class EmailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 转为字典,传送过来的数据为字节，所以要赚换成字符串
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        if not email:
            return http.JsonResponse(
                {
                    'code': RETCODE.DBERR,
                    'errmsg': '没有邮箱数据'
                }
            )
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse(
                {
                    'code': RETCODE.DBERR,
                    'errmsg': '邮箱格式错误'
                }
            )
        try:
            user = request.user
            user.email = email
            user.save()

        except:
            return http.JsonResponse(
                {
                    'code': RETCODE.DBERR,
                    'errmsg': '添加邮箱失败'
                }
            )
        # 加密
        token = itsdangerous.dumps({'user_id': user.id}, contants.EMAIL_ACTIVE_EXPIRES)
        # 设置 路径，激活用户的邮箱
        url = settings.EMAIL_ACTIVE_URL + '?token=%s' % token
        print(url)
        send_virify_email.delay(email, url)
        print('-------------===========')
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '添加邮箱成功'
        })


class JFEmailView(View):
    def get(self, request):
        token = request.GET.get('token')
        # print('=========-----------' + token)
        # 判断是否缺少参数
        if not token:
            return http.HttpResponseBadRequest('缺少参数token')
        # 进行解密
        token = itsdangerous.loads(token, contants.EMAIL_ACTIVE_EXPIRES)
        # print('==============' + token)
        if token is None:
            return http.HttpResponseBadRequest('参数已经过期')
        user_id = token.get('user_id')

        try:
            user = User.objects.get(pk=user_id)
        except:
            return http.HttpResponseBadRequest('邮箱激活失败')
        user.email_active = True
        user.save()
        return redirect('/info/')


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        address_1 = Address.objects.filter(user=user, is_delete=False)
        # if address is None:
        #     return http.JsonResponse({
        #         'code': RETCODE.PARAMERR,
        #         'errmsg': '没有设置收获地址'
        #     })
        addresses = []
        for address in address_1:
            addresses.append(address.dict_s())
        print(addresses)
        context = {
            'addresses': addresses,
            'default_address_id': user.default_address_id
        }
        print(context)
        return render(request, 'user_center_site.html', context)


class AddressCreateView(LoginRequiredMixin, View):
    def post(self, requset):
        # 登录用户是谁这个user就是谁
        user = requset.user
        if user.addresses.count() > 20:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '地址数量数量超过20'
            })
        dicts = json.loads(requset.body.decode())
        receiver = dicts.get('receiver')
        province_id = dicts.get('province_id')
        city_id = dicts.get('city_id')
        district_id = dicts.get('district_id')
        detail = dicts.get('place')
        mobile = dicts.get('mobile')
        tel = dicts.get('tel')
        email = dicts.get('email')

        if not all([receiver, province_id, city_id, district_id, detail, mobile]):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '缺少必须的参数'
            })
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '手机号格式不正确'
            })
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({
                    'code': RETCODE.PARAMERR,
                    'errmsg': '固定电话格式不正确'
                })
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({
                    'code': RETCODE.PARAMERR,
                    'errmsg': '邮箱格式不正确'
                })
        address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            detail=detail,
            mobile=mobile,
            tel=tel,
            email=email
        )
        # 如果当前地址没有默认收获地址，则将设置默认
        if user.default_address is None:
            user.default_address = address
            user.save()
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'address': address.dict_s()
        })


class UpdateAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        dicts = json.loads(request.body.decode())
        receiver = dicts.get('receiver')
        province_id = dicts.get('province_id')
        city_id = dicts.get('city_id')
        district_id = dicts.get('district_id')
        detail = dicts.get('place')
        mobile = dicts.get('mobile')
        tel = dicts.get('tel')
        email = dicts.get('email')
        if not all([receiver, province_id, city_id, district_id, detail, mobile]):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '缺少必须的参数'
            })
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '手机号格式不正确'
            })
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({
                    'code': RETCODE.PARAMERR,
                    'errmsg': '固定电话格式不正确'
                })
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({
                    'code': RETCODE.PARAMERR,
                    'errmsg': '邮箱格式不正确'
                })
        try:
            Address.objects.filter(pk=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                detail=detail,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '更新地址失败'
            })
        address = Address.objects.get(pk=address_id)
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '修改成功',
            'address': address.dict_s()
        })

    def delete(self, request, address_id):
        try:
            Address.objects.filter(pk=address_id).update(
                is_delete=True
            )
        except:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '删除失败'
            })
        else:
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '删除成功'
            })


class DefaultAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        try:
            address = Address.objects.get(pk=address_id)
            request.user.default_address = address
            request.user.save()
        except:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '设置默认地址失败'
            })
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '设置成功'
        })


class UpdateTitleAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        dicts = json.loads(request.body.decode())
        title = dicts.get('title')
        try:
            Address.objects.filter(pk=address_id).update(title=title)
        except:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '地址标签设置失败'
            })
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '地址标签设置成功'
        })


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):
        old_pwd = request.POST.get('old_pwd')
        password = request.POST.get('new_pwd')
        password1 = request.POST.get('new_cpwd')
        if not all([old_pwd, password, password1]):
            return http.HttpResponseBadRequest('缺少必要参数')
        # if not re.match(r'^[0-9A-Za-z]{8,20}$',old_pwd):
        #     return http.HttpResponseBadRequest('密码格式不正确')
        if not request.user.check_password(old_pwd):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('新密码格式不正确')
        if password != password1:
            return http.HttpResponseBadRequest('两次密码不一样')
        try:
            request.user.set_password(password)
            request.user.save()
        except:
            return http.HttpResponseBadRequest('新密码设置失败')
        logout(request)
        response=redirect('/login/')
        response.delete_cookie('username')
        return response