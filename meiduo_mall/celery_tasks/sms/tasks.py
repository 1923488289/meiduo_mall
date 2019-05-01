from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.main import celery_app


# 加个装饰器就是个任务
@celery_app.task(name='send_tasks', bind=True, retry_backoff=3)
def send_tasks(self, to, datas, tempid):
    try:
        # print(datas[0])
        ccp = CCP()
        ccp.send_template_sms(to,datas,tempid)
    except Exception as e:
        self.retry(exc=e, max_retries=2)
