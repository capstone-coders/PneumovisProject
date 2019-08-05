from django.shortcuts import render
from PneumoAcc import views
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth import views as auth_views
from django.db import models
from django.urls import reverse
from django.contrib.auth.views import PasswordChangeView

class Post(models.Model):
    pic = models.ImageField(default = "logo.png")



class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse('login')


#class CustomPasswordChangeView(PasswordChangeView):
    success_url = '/dashboard' # <- choose your URL
#
def ToDashboard(request):
    return render(request, 'dashboard.html')
    # Create your views here.
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
