from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import url
from django.views.generic.base import TemplateView
from PneumoAcc import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#Define url patterns for different html pages
urlpatterns =[
    path('', auth_views.LoginView.as_view(), name='login'),
    url(r'data', views.ToData, name='data'),
    url(r'query', views.ToQuery, name='query'),

    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),]

urlpatterns += staticfiles_urlpatterns()
