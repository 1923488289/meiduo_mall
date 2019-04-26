import random

from django import http
from django.contrib.auth import login
from django.views.generic import View
from django_redis import get_redis_connection

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from . import constants
from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_tasks

# uuid 唯一识别码
class ImageView(View):
    def get(self, request, uuid):
        # 随机字符串  验证码 图片
        text, code, image = captcha.generate_captcha()
        # 获取链接redis对象 将信息写入进去
        redis_cli = get_redis_connection('verificat_code')
        redis_cli.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
        # 响应数据格式。
        return http.HttpResponse(image, content_type='image/png')


class SMSCodeView(View):
    def get(self, request, mobile):
        print(mobile)
        # 接收图片验证码
        image_code_request = request.GET.get('image_code')
        # 接收uuid
        uuid = request.GET.get('image_code_id')
        # 判断是否为空
        if not all([image_code_request, uuid]):
            return http.JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '比要参数'
            })
        # 获取链接对象
        redis_server = get_redis_connection('verificat_code')
        redis_code_server = redis_server.get(uuid)
        if redis_code_server is None:
            return http.JsonResponse(
                {
                    'code': RETCODE.IMAGECODEERR,
                    'errmsg': '图片验证码过期'
                }
            )
        if redis_code_server.decode() != image_code_request.upper():
            return http.JsonResponse(
                {
                    'code': RETCODE.IMAGECODEERR,
                    'errmsg': '图形验证码错误'
                }
            )
        # t图片验证码过期
        redis_server.delete(uuid)
        #
        if redis_server.get('sms_s_'+mobile):
            return http.JsonResponse(
                {'code':RETCODE.SMSCODERR,
                 'errmsg':'发短喜过于频繁'}

            )

        sms_code = '%06d' % random.randint(0, 999999)
        print('这是sms'+sms_code)
        # redis_server.setex('sms_' + mobile, constants.TMAGE_CODE_SMS, sms_code)
        # redis_server.setex('sms_s_' + mobile, constants.TMAGE_CODE_SMS_BF, 1)
        #优化redis
        redis_server_yh=redis_server.pipeline()
        redis_server_yh.setex('sms_' + mobile, constants.TMAGE_CODE_SMS, sms_code)
        #是否在60秒内发送过短信
        redis_server_yh.setex('sms_s_' + mobile, constants.TMAGE_CODE_SMS_BF, 1)
        redis_server_yh.execute()
        #celery
        send_tasks.delay(mobile,[sms_code, constants.TMAGE_CODE_SMS / 60], 1)
        # print(sms_code)
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, constants.TMAGE_CODE_SMS / 60], 1)
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'

        })
