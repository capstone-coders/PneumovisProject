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
from fusioncharts import FusionCharts

class Post(models.Model):
    pic = models.ImageField(default = "logo.png")

class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse('login')

#class CustomPasswordChangeView(PasswordChangeView):
    success_url = '/dashboard' # <- choose your URL
def ToDashboard(request):

	dataSource = {}
	dataSource['chart'] = { 
		"caption": "Overview",
		"theme": "fusion",
		"valuefontsize": "25",
		"showlabels": "1",
		"showvalues": "0",
		"showplotborder": "0",
		"placexaxislabelsontop": "1",
		"mapbycategory": "0",
		"showlegend": "0",
		"plottooltext": "<b>$columnlabel</b> has <b>$rowlabel</b>",
		"valuefontcolor": "#262A44",
		"xAxisName": "Patient ID",
		"yAxisName": "Serotype",
        }


	dataSource["rows"] = []
	rowarr = {}
	rowarr["row"] = []
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Serotype) as id from PneumoVis'):
		row = {}
		row["id"] = key.id
		row["Label"] = key.id
		rowarr["row"].append(row)
	dataSource["rows"] = rowarr

	#dataSource['rows'] = {
	#	"row": [
	#	      {
	#		"id": "2002",
	#		"label": "2002"
	#	      }
	#	]
	#}

	dataSource["columns"] = []
	colarr = {}
	colarr["column"] = []
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Patient_ID) as id from PneumoVis'):
		c = {}
		c["id"] = key.id
		c["Label"] = key.id
		colarr["column"].append(c)
	dataSource["columns"] = colarr

	#dataSource['columns'] = { 
	#	"column": [
	#	      {
	#		"id": "1",
	#		"label": "#1"
	#	      }
	#	]
	#}
	
	dataSource["dataset"] = []
	datarr = {}
	temp = []
	datarr["data"] = []
	for key in database.objects.using('mysql').raw('SELECT Patient_ID as id, Serotype from PneumoVis'):
		d = {}
		d["rowid"] = key.Serotype
		d["columnid"] = key.id
		d["value"] = "10"
		d["displayvalue"] = key.Serotype
		datarr["data"].append(d)
	temp.append(datarr)
	dataSource["dataset"].append(datarr) 
	print(dataSource)

	#dataSource['dataset'] = [
	#	{"data": [
	#		{
	#		  "rowid": "13",
	#		  "columnid": "PT1",
	#		  "value": "0",
	#		  "displayvalue": "13"
	#		}
	#	]}
	#]

	dataSource['colorrange'] = {
		"gradient": "1",
		"minvalue": "0",
		"code": "#FCFBFF",
		"color": [
		      {
			"code": "#FF0000",
			"minvalue": "0",
			"maxvalue": "10"
		      }
		]
	}
	

	chartObj = FusionCharts('heatmap', 'ex1', '12500', '1000', 'chart-1', 'json', dataSource)

	patients = database.objects.using('mysql').raw('SELECT COUNT(DISTINCT Patient_ID) as id from PneumoVis')[0]
	presence = database.objects.using('mysql').raw('SELECT COUNT(Presence) as id from PneumoVis WHERE Presence="Yes"')[0]
	samples = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM PneumoVis')[0]
	majority = database.objects.using('mysql').raw('SELECT Serotype as id, COUNT(*) as count FROM PneumoVis WHERE Serotype!="" GROUP BY Serotype ORDER BY count DESC LIMIT 1')[0]
	hiv = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM (SELECT DISTINCT(Patient_ID), HIVexpose FROM PneumoVis WHERE HIVexpose="Yes") as totals')[0]
	content = {"patients":patients.id, "presence":presence.id, "samples": samples.id, "majority":majority.id, "HIV":hiv.id, "output":chartObj.render()}
	return render(request, 'dashboard.html', content)

def ToData(request):
    table = database.objects.using('mysql').raw('SELECT * FROM PneumoVis WHERE Patient_ID="PT1" ORDER BY DateCollection ASC')
    content = { "t":table }
    return render(request, "data.html", content)

def ToQuery(request):
    return render(request, 'query.html')
    # Create your views here.
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
