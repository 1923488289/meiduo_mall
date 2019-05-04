from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.MyClass.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserView.as_view()),
    url(r'^mobiles/(?P<phone>1[3-9]\d{9})/count/$', views.MobilView.as_view()),
    url(r'^login/$', views.LoginView.as_view()),
    # url(r'^/$', views.IndexView.as_view()),
    url(r'^logout/$', views.LogoutView.as_view()),
    url(r'^info/$', views.InfoView.as_view()),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.JFEmailView.as_view()),
    url(r'^addresses/$',views.AddressView.as_view()),
    url(r'^addresses/create/$',views.AddressCreateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$',views.UpdateAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$',views.DefaultAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$',views.UpdateTitleAddressView.as_view()),
    url(r'^password/$',views.ChangePasswordView.as_view()),
]
