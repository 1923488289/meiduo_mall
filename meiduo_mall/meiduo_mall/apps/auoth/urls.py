from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/login/$', views.QQcodeView.as_view()),
    url(r'^oauth_callback/$', views.OpendidView.as_view()),
    # url(r'^oauth/$',views.OauthView.as_view())
]
