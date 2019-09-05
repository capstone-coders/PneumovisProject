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
		"theme": "fusion",
		"valuefontsize": "25",
		"showlabels": "1",
		"showvalues": "0",
		"showplotborder": "1",
		"placexaxislabelsontop": "1",
		"mapbycategory": "0",
		"showlegend": "0",
		"plottooltext": "<b>$columnlabel</b> has <b>$displayvalue</b> <b>$rowlabel</b>",
		"valuefontcolor": "#262A44",
		"xAxisName": "Patient ID",
		"yAxisName": "Serotype",
        }


	dataSource["rows"] = []
	rowarr = {}
	rowarr["row"] = []
	ro1 = {}
	ro1["id"] = "Gender"
	ro1["Label"] = "Gender"
	rowarr["row"].append(ro1)
	ro2 = {}
	ro2["id"] = "HIV Status"
	ro2["Label"] = "HIV Status"
	rowarr["row"].append(ro2)
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Serotype) as id from PneumoVis ORDER BY Serotype ASC'):
		row = {}
		row["id"] = key.id
		row["Label"] = key.id
		rowarr["row"].append(row)
	dataSource["rows"] = rowarr

	dataSource["columns"] = []
	colarr = {}
	colarr["column"] = []
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Patient_ID) as id from PneumoVis'):
		c = {}
		c["id"] = key.id
		c["Label"] = key.id
		colarr["column"].append(c)
	dataSource["columns"] = colarr
	
	dataSource["dataset"] = []
	datarr = {}
	temp = []
	datarr["data"] = []
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Patient_ID) as id, sex from PneumoVis'):
		d = {}
		if key.sex == "Male":
			x = 20
		else:
			x = 30
		d["rowid"] = "Gender"
		d["columnid"] = key.id
		d["value"] = x
		d["displayvalue"] = key.sex
		datarr["data"].append(d)
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Patient_ID) as id, HIVexpose from PneumoVis'):
		d = {}
		if key.HIVexpose == "Yes":
			x = 40
		else:
			x = 50
		d["rowid"] = "HIV Status"
		d["columnid"] = key.id
		d["value"] = x
		d["displayvalue"] = key.HIVexpose
		datarr["data"].append(d)
	for key in database.objects.using('mysql').raw('SELECT Patient_ID as id, Serotype from PneumoVis'):
		d = {}
		d["rowid"] = key.Serotype
		d["columnid"] = key.id
		d["value"] = "10"
		d["displayvalue"] = "Serotype"
		datarr["data"].append(d)
	temp.append(datarr)
	dataSource["dataset"].append(datarr)

	dataSource['colorrange'] = {
		"gradient": "0",
		"minvalue": "0",
		"code": "#FCFBFF",
		"color": [
		      {
			"code": "#FF0000",
			"minvalue": "0",
			"maxvalue": "10"
		      },
		      {
			"code": "#2471A3",
			"minvalue": "11",
			"maxvalue": "20"
		      },
		      {
			"code": "#F1948A",
			"minvalue": "21",
			"maxvalue": "30"
		      },
		      {
			"code": "#6C3483",
			"minvalue": "31",
			"maxvalue": "40"
		      },
		      {
			"code": "#F4D03F",
			"minvalue": "41",
			"maxvalue": "50"
		      }
		]
	}
	

	chartObj = FusionCharts('heatmap', 'ex1', '11000', '1000', 'chart-1', 'json', dataSource)

	patients = database.objects.using('mysql').raw('SELECT COUNT(DISTINCT Patient_ID) as id from PneumoVis')[0]
	presence = database.objects.using('mysql').raw('SELECT COUNT(Presence) as id from PneumoVis WHERE Presence="Yes"')[0]
	samples = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM PneumoVis')[0]
	majority = database.objects.using('mysql').raw('SELECT Serotype as id, COUNT(*) as count FROM PneumoVis WHERE Serotype!="" GROUP BY Serotype ORDER BY count DESC LIMIT 1')[0]
	hiv = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM (SELECT DISTINCT(Patient_ID), HIVexpose FROM PneumoVis WHERE HIVexpose="Yes") as totals')[0]
	content = {"patients":patients.id, "presence":presence.id, "samples": samples.id, "majority":majority.id, "HIV":hiv.id, "output":chartObj.render()}
	return render(request, 'dashboard.html', content)

def ToData(request):
	answer = ""
	if request.POST:
		answer=request.POST['PID']
	print(answer)
	table = database.objects.using('mysql').raw('SELECT * FROM PneumoVis WHERE Patient_ID=%s ORDER BY DateCollection ASC', [answer])
	content = { "t":table, "answer":answer }
	return render(request, "data.html", content)

def ToDrill(request,pid):
	answer = str(pid)
	
	dataSource = {}
	dataSource['chart'] = { 
		"theme": "fusion",
		"valuefontsize": "25",
		"showlabels": "1",
		"showvalues": "0",
		"showplotborder": "1",
		"placexaxislabelsontop": "1",
		"mapbycategory": "0",
		"showlegend": "0",
		"plottooltext": "<b>$columnlabel</b> has <b>$displayvalue</b> <b>$rowlabel</b>",
		"valuefontcolor": "#262A44",
		"xAxisName": "Patient ID",
		"yAxisName": "Serotype",
        }
        
	dataSource["rows"] = []
	rowarr = {}
	rowarr["row"] = []
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Serotype) as id from PneumoVis ORDER BY Serotype ASC'):
		row = {}
		row["id"] = key.id
		row["Label"] = key.id
		rowarr["row"].append(row)
	dataSource["rows"] = rowarr

	dataSource["columns"] = []
	colarr = {}
	colarr["column"] = []
	c = {}
	c["id"] = answer
	c["Label"] = answer
	colarr["column"].append(c)
	dataSource["columns"] = colarr
	
	dataSource["dataset"] = []
	datarr = {}
	temp = []
	datarr["data"] = []
	for key in database.objects.using('mysql').raw('SELECT Patient_ID as id, Serotype from PneumoVis WHERE Patient_ID=%s', [answer]):
		d = {}
		d["rowid"] = key.Serotype
		d["columnid"] = key.id
		d["value"] = "10"
		d["displayvalue"] = "Serotype"
		datarr["data"].append(d)
	temp.append(datarr)
	dataSource["dataset"].append(datarr)
	
	dataSource['colorrange'] = {
		"gradient": "0",
		"minvalue": "0",
		"code": "#FCFBFF",
		"color": [
		      {
			"code": "#FF0000",
			"minvalue": "0",
			"maxvalue": "10"
		      },
		]
	}
	
	chartObj = FusionCharts('heatmap', 'ex1', '200', '550', 'chart-1', 'json', dataSource)
	content = { "output":chartObj.render() }
	return render(request, "popup.html", content)

def ToQuery(request):
	answer = "Gender VS Location VS Presence"
	search = ""
	if request.POST:
		answer=request.POST['dropdown']
		if 'PID' in request.POST:
			search=request.POST['PID']
		
	if answer == "Gender VS Location VS Presence":	
		dataSource = {}
		dataSource['chart'] = { 
			"caption": "Gender vs Location vs Presence",
			"showvalues": "0",
			"xAxisName": "Location",
			"yAxisName": "Patient Count",
			"drawcrossline": "1",
			"formatnumberscale": "1",
			"plottooltext": "<b>$dataValue</b> are <b>$seriesName</b> in $label",
			"theme": "candy"
		}
		
		dataSource["categories"] = []
		catarr = {}
		catarr["category"] = []
		for key in database.objects.using('mysql').raw('SELECT DISTINCT(site) as id from PneumoVis'):
			c = {}
			c["label"] = key.id
			catarr["category"].append(c)
		dataSource["categories"].append(catarr)
		
		dataSource["dataset"] = []
		s1atarr = {}
		s1atarr["seriesname"] = "Male With No Presence"
		s1atarr["data"] = []
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Male" AND Presence="No") as t GROUP BY site, sex, Presence'):
			d = {}
			d["value"] = key.count
			s1atarr["data"].append(d)
		dataSource["dataset"].append(s1atarr)
		
		s2atarr = {}
		s2atarr["seriesname"] = "Male With Presence"
		s2atarr["data"] = []
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Male" AND Presence="Yes") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s2atarr["data"].append(d)
		dataSource["dataset"].append(s2atarr)
		
		s3atarr = {}
		s3atarr["seriesname"] = "Female With No Presence"
		s3atarr["data"] = []
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Female" AND Presence="No") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s3atarr["data"].append(d)
		dataSource["dataset"].append(s3atarr)
		
		s4atarr = {}
		s4atarr["seriesname"] = "Female With Presence"
		s4atarr["data"] = []
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Female" AND Presence="Yes") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s4atarr["data"].append(d)
		dataSource["dataset"].append(s4atarr)
		
		chartObj = FusionCharts('mscolumn2d', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)
		
	elif answer == "HIV VS Presence":
		dataSource = {}
		dataSource['chart'] = { 
			"caption": "HIV VS Presence",
			"theme": "fusion",
			"xaxisminvalue": "0",
			"xaxismaxvalue": "100",
			"yaxisminvalue": "0",
			"yaxismaxvalue": "100",
			"xaxisname": "Presence",
			"yaxisname": "HIV",
			"plottooltext": "$zvalue Patients",
			"drawquadrant": "1",
			"quadrantlabeltl": "HIV / No Presence",
			"quadrantlabeltr": "HIV / Presence",
			"quadrantlabelbl": "No HIV / No Presence",
			"quadrantlabelbr": "No HIV / Presence",
			"quadrantxval": "50",
			"quadrantyval": "50",
			"quadrantlinealpha": "50",
			"quadrantlinethickness": "2",
			"showYAxisValues": "0",
			"showLabels": "0",
			"showValues": "1"
		}
		
		dataSource["categories"] = []
		
		dataSource["dataset"] = []
		s1atarr = {}
		s1atarr["data"] = []
		for key in database.objects.using('mysql').raw('SELECT HIVexpose as id, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID), HIVexpose, Presence FROM PneumoVis WHERE HIVexpose!="") as t GROUP BY HIVexpose, Presence'):
			d = {}
			if key.id == "No" and key.Presence == "No":
				x = 25
				y = 25
			elif key.id == "No" and key.Presence == "Yes":
				x = 75
				y = 25
			elif key.id == "Yes" and key.Presence == "No":
				x = 25
				y = 75
			else:
				x = 75
				y = 75
			d["x"] = x
			d["y"] = y
			d["z"] = key.count
			d["name"] = str(key.count)+" Patients"
			s1atarr["data"].append(d)
		dataSource["dataset"].append(s1atarr)
		
		dataSource["trendlines"] = []
		
		chartObj = FusionCharts('bubble', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)
		
	else:
		dataSource = {}
		dataSource['chart'] = { 
			"caption": "Number of Collected Data Per Patient",
			"subCaption": "(Click on Bar For More Information)",
			"yaxisname": "Number of Collected Data",
			"flatscrollbars": "0",
			"scrollheight": "12",
			"numvisibleplot": "10",
			"plottooltext": "<b>$dataValue</b> data collected from <b>$label</b>",
			"theme": "fusion"
		}
		
		dataSource["categories"] = []
		catarr = {}
		catarr["category"] = []
		if search == "":
			newdatabase = database.objects.using('mysql').raw('SELECT Patient_ID as id, COUNT(Patient_ID) as count FROM PneumoVis GROUP BY Patient_ID ORDER BY Patient_ID ASC')
		else:
			newdatabase = database.objects.using('mysql').raw('SELECT Patient_ID as id, COUNT(Patient_ID) as count FROM PneumoVis WHERE Patient_ID=%s GROUP BY Patient_ID ORDER BY Patient_ID ASC', [search])
		for key in newdatabase:
			c = {}
			c["label"] = key.id
			catarr["category"].append(c)
		dataSource["categories"].append(catarr)
		
		dataSource["dataset"] = []
		s1atarr = {}
		s1atarr["seriesname"] = "Number of Data Collected"
		s1atarr["data"] = []
		for key in newdatabase:
			d = {}
			d["value"] = key.count
			d["link"] = "n-detailsWin,width=220,height=580,toolbar=no-http://localhost:8000/popup"+key.id
			s1atarr["data"].append(d)
		dataSource["dataset"].append(s1atarr)
		
		chartObj = FusionCharts('scrollstackedcolumn2d', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)
		
	content = {"output":chartObj.render(), "answer":answer, "search":search}
	return render(request, 'query.html', content)
    # Create your views here.
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
