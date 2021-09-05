from django.conf.urls import url
# from django.conf.urls import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    url("^profile-(?P<slug>[\w-]+)/update/$", views.profileUpdate, name="profile_update", ),

]
