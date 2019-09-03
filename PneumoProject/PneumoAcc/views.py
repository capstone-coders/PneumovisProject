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
from .models import database

class Post(models.Model):
    pic = models.ImageField(default = "logo.png")

class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse('login')

#class CustomPasswordChangeView(PasswordChangeView):
    success_url = '/dashboard' # <- choose your URL
def ToDashboard(request):
	patients = database.objects.using('mysql').raw('SELECT COUNT(DISTINCT Patient_ID) as id from PneumoVis')[0]
	presence = database.objects.using('mysql').raw('SELECT COUNT(Presence) as id from PneumoVis WHERE Presence="Yes"')[0]
	samples = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM PneumoVis')[0]
	majority = database.objects.using('mysql').raw('SELECT Serotype as id, COUNT(*) as count FROM PneumoVis WHERE Serotype!="" GROUP BY Serotype ORDER BY count DESC LIMIT 1')[0]
	hiv = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM (SELECT DISTINCT(Patient_ID), HIVexpose FROM PneumoVis WHERE HIVexpose="Yes") as totals')[0]
	content = {"patients":patients.id, "presence":presence.id, "samples": samples.id, "majority":majority.id, "HIV":hiv.id}
	return render(request, 'dashboard.html', content)

def ToData(request):
    table = database.objects.using('mysql').raw('SELECT * FROM PneumoVis where Patient_ID = "PT5" ORDER BY DateCollection ASC')
    content = { "t":table }
    return render(request, "data.html", content)

from django.shortcuts import render
from django.http import HttpResponse

# Include the `fusioncharts.py` file that contains functions to embed the charts.
from .fusioncharts import FusionCharts

#from models import *

# The `chart` function is defined to generate Column 2D chart from database.
def chart(request):
    # Create an object for the column2d chart using the FusionCharts class constructor
    column2d = FusionCharts("column2d", "ex1" , "600", "400", "chart-1", "json",
         # The data is passed as a string in the `dataSource` as parameter.
        """{
               "chart": {
                  "caption":"Harry\'s SuperMart",
                  "subCaption":"Top 5 stores in last month by revenue",
                  "numberPrefix":"$",
                  "theme":"ocean"
               },
               "data": [
                    {"label":"Bakersfield Central", "value":"880000"},
                    {"label":"Garden Groove harbour", "value":"730000"},
                    {"label":"Los Angeles Topanga", "value":"590000"},
                    {"label":"Compton-Rancho Dom", "value":"520000"},
                    {"label":"Daly City Serramonte", "value":"330000"}
                ]
            }""")

    # returning complete JavaScript and HTML code,
    # which is used to generate chart in the browsers.
    return  render(request, 'query.html', {'output' : column2d.render()})

def ToQuery(request):
    return render(request, 'query.html')
    # Create your views here.
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
