from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register$', views.MyClass.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserView.as_view()),
    url(r'^mobiles/(?P<phone>1[3-9]\d{9})/count/$', views.MobilView.as_view())

]
