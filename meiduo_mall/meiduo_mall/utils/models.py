from django.db import models
class BaseModel(models.Model):
    create_time =models.DateField(auto_now_add=True,verbose_name='创建时间')
    update_time=models.DateField(auto_now=True,verbose_name='更新时间')
    class Meta:
        abstract =True #说明是个抽象模型类，不会生成迁移文件

