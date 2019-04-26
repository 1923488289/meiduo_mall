from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        views.ImageView.as_view()),
    url(r'^sms_codes/(?P<mobile>1[345789]\d{9})/$', views.SMSCodeView.as_view()),

]
