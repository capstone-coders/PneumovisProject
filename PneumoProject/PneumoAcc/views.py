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

# Method ToDashboard is responsible for all the components
# displayed on the Dashboard page. Includes calculations
# for dispaying an overview of the data appearing in the
# main CSV file of patient records
def ToDashboard(request):


	dataSource = {} #given to the connection set up to a database from a server

    # Setting up the chart conditions for displaying the Patient vs Serotype chart
	dataSource['chart'] = {
		"theme": "candy",
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

    #Formatting of the graph to suit the needs of data.
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

    # Collecting all the unique serotypes and adding them to the graph on the y-axis in alphabetical order
	for key in database.objects.using('mysql').raw('SELECT DISTINCT(Serotype) as id from PneumoVis ORDER BY Serotype ASC'):
		row = {}
		row["id"] = key.id
		row["Label"] = key.id
		rowarr["row"].append(row)
	dataSource["rows"] = rowarr
	dataSource["columns"] = []
	colarr = {}
	colarr["column"] = []

    #Collecting all the the patients in the database and puting them on the x-axis of the graph
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

    #Creating a section of the graph where the gender of the patient is indicated with a colour block.
    #A blue block is used for a male patient and a pink block indicates a female
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

    #Creating a section of the graph where the HIV status of the patient is indicated with a colour block
    #A purple block is used for a patient with HIV and a yellow block indicates a patient with no HIV exposure
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

    #Database is searched and data is collected and displayed on the graph regarding that serotype the patients
    #has had. If the patient has been diagnosed with a spesific serotype, it is indicated with a red block
	for key in database.objects.using('mysql').raw('SELECT Patient_ID as id, Serotype from PneumoVis'):
		d = {}
		d["rowid"] = key.Serotype
		d["columnid"] = key.id
		d["value"] = "10"
		d["displayvalue"] = "Serotype"
		datarr["data"].append(d)
	temp.append(datarr)
	dataSource["dataset"].append(datarr)

    #Setting the colours of the blocks on the graph
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

    #Preparing a chart from Fusion Charts collection to be displayed
	chartObj = FusionCharts('heatmap', 'ex1', '11000', '1000', 'chart-1', 'json', dataSource)#Accessing fusionCharts chart library

    # The values below are data sumariies of the data contained in the database, these values are calculated using SQL commands
	patients = database.objects.using('mysql').raw('SELECT COUNT(DISTINCT Patient_ID) as id from PneumoVis')[0]
	presence = database.objects.using('mysql').raw('SELECT COUNT(Presence) as id from PneumoVis WHERE Presence="Yes"')[0]
	samples = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM PneumoVis')[0]
	majority = database.objects.using('mysql').raw('SELECT Serotype as id, COUNT(*) as count FROM PneumoVis WHERE Serotype!="" GROUP BY Serotype ORDER BY count DESC LIMIT 1')[0]
	hiv = database.objects.using('mysql').raw('SELECT COUNT(*) as id FROM (SELECT DISTINCT(Patient_ID), HIVexpose FROM PneumoVis WHERE HIVexpose="Yes") as totals')[0]
	content = {"patients":patients.id, "presence":presence.id, "samples": samples.id, "majority":majority.id, "HIV":hiv.id, "output":chartObj.render()}
	return render(request, 'dashboard.html', content)

#This method is used to filter data according to the patient chosen by the user
def ToData(request):
	answer = ""
	if request.POST:
		answer=request.POST['PID']
	print(answer)

    #A table is populated with records of whatever patient the user indicates. eg, all the records of PT1 is displayed on tab;e.
	table = database.objects.using('mysql').raw('SELECT * FROM PneumoVis WHERE Patient_ID=%s ORDER BY DateCollection ASC', [answer])
	content = { "t":table, "answer":answer }
	return render(request, "data.html", content)


def ToDrill(request,pid):
	answer = str(pid)

	dataSource = {} #given to the connection set up to a database from a server

    # Setting up the chart conditions for displaying the Patient vs Serotype chart
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

    # Collecting all the unique serotypes and adding them to the graph on the y-axis in alphabetical order
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

    #Selecting and displaying all the serotypes associated witha  specific patient
	for key in database.objects.using('mysql').raw('SELECT Patient_ID as id, Serotype from PneumoVis WHERE Patient_ID=%s', [answer]):
		d = {}
		d["rowid"] = key.Serotype
		d["columnid"] = key.id
		d["value"] = "10"
		d["displayvalue"] = "Serotype"
		datarr["data"].append(d)
	temp.append(datarr)
	dataSource["dataset"].append(datarr)

    #Setting the colours of the blocks on the graph
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

    #Preparing a chart from Fusion Charts collection to be displayed
	chartObj = FusionCharts('heatmap', 'ex1', '200', '550', 'chart-1', 'json', dataSource)#Accessing fusionCharts chart library
	content = { "output":chartObj.render() }
	return render(request, "popup.html", content)

#The 'ToQuery' method is used on the Query page where the user selects a visual filter.
#The method is used to determine the type of graph and visual data to display,
#depending on the visual filter chosen by the user. This method prepares the necessary
#data that needs to be filtered appropriately to display the correct data as a specific graph.
def ToQuery(request):
	answer = "Gender VS Location VS Presence"
	search = ""
	if request.POST:
		answer=request.POST['dropdown']
		if 'PID' in request.POST:
			search=request.POST['PID']

    # This if statement checks to see which graph the user has chosen so that it can be displayed
	if answer == "Gender VS Location VS Presence":
		dataSource = {}

        # Below the pre conditions for the Gender vs Location vs Presence graph is set
		dataSource['chart'] = {
			"caption": "Gender vs Location vs Presence",
			"showvalues": "0",
			"xAxisName": "Location",
			"yAxisName": "Patient Count",
			"drawcrossline": "1",
			"formatnumberscale": "1",
			"plottooltext": "<b>$dataValue</b> are <b>$seriesName</b> in $label",
			"theme": "fusion"
		}

		dataSource["categories"] = []
		catarr = {}
		catarr["category"] = []

        # The for loop below goes through the entire data and collects all the unique sites in the database
		for key in database.objects.using('mysql').raw('SELECT DISTINCT(site) as id from PneumoVis'):
			c = {}
			c["label"] = key.id
			catarr["category"].append(c)
		dataSource["categories"].append(catarr)
		dataSource["dataset"] = []
		s1atarr = {}
		s1atarr["seriesname"] = "Male With No Presence"
		s1atarr["data"] = []

        # This SQL statement counts the number of patients that are male with no presence of the disease so that it can be displayed on the bar graph
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Male" AND Presence="No") as t GROUP BY site, sex, Presence'):
			d = {}
			d["value"] = key.count
			s1atarr["data"].append(d)
		dataSource["dataset"].append(s1atarr)
		s2atarr = {}
		s2atarr["seriesname"] = "Male With Presence"
		s2atarr["data"] = []

        # This SQL statement counts the number of patients that are male with a presence of the disease so that it can be displayed on the bar graph
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Male" AND Presence="Yes") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s2atarr["data"].append(d)
		dataSource["dataset"].append(s2atarr)
		s3atarr = {}
		s3atarr["seriesname"] = "Female With No Presence"
		s3atarr["data"] = []

        # This SQL statement counts the number of patients that are female with no presence of the disease so that it can be displayed on the bar graph
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Female" AND Presence="No") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s3atarr["data"].append(d)
		dataSource["dataset"].append(s3atarr)
		s4atarr = {}
		s4atarr["seriesname"] = "Female With Presence"
		s4atarr["data"] = []

        # This SQL statement counts the number of patients that are female with a presence of the disease so that it can be displayed on the bar graph
		for key in database.objects.using('mysql').raw('SELECT site as id, sex, Presence, COUNT(Presence) as count FROM (SELECT DISTINCT(Patient_ID) as id, site, sex, Presence FROM PneumoVis WHERE sex="Female" AND Presence="Yes") as t GROUP BY site, sex, Presence;'):
			d = {}
			d["value"] = key.count
			s4atarr["data"].append(d)
		dataSource["dataset"].append(s4atarr)

        #Preparing a chart from Fusion Charts collection to be displayed
		chartObj = FusionCharts('mscolumn2d', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)

    # This next part of the if-statement checks if the user selected the HIV VS Presence graph in the drop-down menu
	elif answer == "HIV VS Presence":
		dataSource = {}
		dataSource['chart'] = {
			"caption": "HIV VS Presence",
			"theme": "fusion",
			"xaxisminvalue": "0",
			"xaxismaxvalue": "100",
			"yaxisminvalue": "0", # OPTIMIZE:
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

        #This for-loop uses SQL statements to collect all the data regarding the HIV exposure as well as the counts the number with and without HIV exposure
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

        #Preparing a chart from Fusion Charts collection to be displayed
		chartObj = FusionCharts('bubble', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)

    # the else is for displaying the last possibe graph choice of the user whic is a Serotype chart per patient
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
            #This SQL statement is used to add ALL patient records to a new database for displaying as a graph
			newdatabase = database.objects.using('mysql').raw('SELECT Patient_ID as id, COUNT(Patient_ID) as count FROM PneumoVis GROUP BY Patient_ID ORDER BY Patient_ID ASC')
		else:
            #This SQL statement is used to add a SPECIFIC patients record to a new database for displaying as a graph
			newdatabase = database.objects.using('mysql').raw('SELECT Patient_ID as id, COUNT(Patient_ID) as count FROM PneumoVis WHERE Patient_ID=%s GROUP BY Patient_ID ORDER BY Patient_ID ASC', [search])

        #Displaying of the records in the newly temporary created database
		for key in newdatabase:
			c = {}
			c["label"] = key.id
			catarr["category"].append(c)
		dataSource["categories"].append(catarr)
		dataSource["dataset"] = []
		s1atarr = {}
		s1atarr["seriesname"] = "Number of Data Collected"
		s1atarr["data"] = []

        # For-Loop uses the data in the new temporary database to show more detailed information on a selected patient as a pop-up
		for key in newdatabase:
			d = {}
			d["value"] = key.count
			d["link"] = "n-detailsWin,width=220,height=580,toolbar=no-http://localhost:8000/popup"+key.id
			s1atarr["data"].append(d)
		dataSource["dataset"].append(s1atarr)

        #Preparing a chart from Fusion Charts collection to be displayed
		chartObj = FusionCharts('scrollstackedcolumn2d', 'ex1', '1000', '480', 'chart-1', 'json', dataSource)

	content = {"output":chartObj.render(), "answer":answer, "search":search}
	return render(request, 'query.html', content)

#Takes user to a new page to change their current password
path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
