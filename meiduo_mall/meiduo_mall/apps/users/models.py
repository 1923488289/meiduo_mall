from django.db import models
from django.contrib.auth.models import AbstractUser
from meiduo_mall.utils.models import BaseModel
# from areas.models import Area
import areas


# Create your models here.

class User(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    user = models.ForeignKey('User', related_name='addresses')
    title = models.CharField(max_length=20)  # 标题
    receiver = models.CharField(max_length=20)  # 收件人
    province = models.ForeignKey('areas.Area', related_name='provinces')  # 省
    city = models.ForeignKey('areas.Area', related_name='cities')  # 市
    district = models.ForeignKey('areas.Area', related_name='districts')  # 县
    detail = models.CharField(max_length=100)  # 详细信息
    mobile = models.CharField(max_length=11)  # 收件人手机号
    tel = models.CharField(max_length=20, null=True)  # 固定电话，选填
    email = models.CharField(max_length=50, null=True)  # 邮箱地址，选填
    is_delete = models.BooleanField(default=False)  # 逻辑删除

    class Meta:
        db_table = 'tb_addresses'

    def dict_s(self):
        return {
            'id': self.id,
            'title': self.title,
            'receiver': self.receiver,
            'province_id': self.province_id,
            'province': self.province.name,
            'city_id': self.city_id,
            'city': self.city.name,
            'district_id': self.district_id,
            'district': self.district.name,
            'place': self.detail,
            'mobile': self.mobile,
            'tel': self.tel,
            'email': self.email,
        }
