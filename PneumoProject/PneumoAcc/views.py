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
from django.http import HttpResponse
from .fusioncharts import FusionCharts
from collections import OrderedDict



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


# returning complete JavaScript and HTML code,
# which is used to generate chart in the browsers.
    return  render(request, 'query.html',  {'output' : column2D.render(), 'chartTitle': 'Simple Chart Using Array'})
    # Create your views here.
def ToQuery(request):
     # Create an object for the Multiseries column 2D charts using the FusionCharts class constructor
	mscol2D = FusionCharts("stackedColumn2DLine", "ex1" , "600", "400", "chart-1", "json",
            # The data is passed as a string in the `dataSource` as parameter.
    """{
            "chart": {
            "showvalues": "0",
            "caption": "Apple's Revenue & Profit",
            "subCaption": "(2013-2016)",
            "numberprefix": "$",
            "numberSuffix" : "B",
            "plotToolText" : "Sales of $seriesName in $label was <b>$dataValue</b>",
            "showhovereffect": "1",
            "yaxisname": "$ (In billions)",
            "showSum":"1",
            "theme": "fusion"
        },
        "categories": [{
            "category": [{
            "label": "2013"
            }, {
            "label": "2014"
            }, {
            "label": "2015"
            }, {
            "label": "2016"
            }]
        }],
        "dataset": [{
            "seriesname": "iPhone",
            "data": [{
            "value": "21"
            }, {
            "value": "24"
            }, {
            "value": "27"
            }, {
            "value": "30"
            }]
        }, {
            "seriesname": "iPad",
            "data": [{
            "value": "8"
            }, {
            "value": "10"
            }, {
            "value": "11"
            }, {
            "value": "12"
            }]
        }, {
            "seriesname": "Macbooks",
            "data": [{
            "value": "2"
            }, {
            "value": "4"
            }, {
            "value": "5"
            }, {
            "value": "5.5"
            }]
        }, {
            "seriesname": "Others",
            "data": [{
            "value": "2"
            }, {
            "value": "4"
            }, {
            "value": "9"
            }, {
            "value": "11"
            }]
        }, {
            "seriesname": "Profit",
            "plotToolText" : "Total profit in $label was <b>$dataValue</b>",
            "renderas": "Line",
            "data": [{
            "value": "17"
            }, {
            "value": "19"
            }, {
            "value": "13"
            }, {
            "value": "18"
            }]
        }]
    }""")

	return render(request, 'query.html', {'output': mscol2D.render(), 'chartTitle': 'Stacked Column 2D with Line Chart'})
    # Create your views here.
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
