from django.shortcuts import render
from django.views.generic import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants
from django import http


# uuid 唯一识别码
class ImageView(View):
    def get(self, request, uuid):
        # 随机字符串  验证码 图片
        text, code, image = captcha.generate_captcha()
        # 找到对应的数据库 将信息写入进去
        redis_cli = get_redis_connection('verificat_code')
        redis_cli.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
        # 响应数据格式。
        return http.HttpResponse(image, content_type='image/png')
