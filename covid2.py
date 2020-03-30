import mysql.connector
import datetime
import requests
import tkinter as tk 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import colorsys
import math
from lxml import html
import decimal

def updateDatabase(cursor):
	url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
	caseLines = requests.get(url + "time_series_covid19_confirmed_global.csv").text.split("\n")
	deadLines = requests.get(url + "time_series_covid19_deaths_global.csv").text.split("\n")
	recoLines = requests.get(url + "time_series_covid19_recovered_global.csv").text.split("\n")
	states = {}
	countries = {}
	resp = requests.get(url = "https://www.worldometers.info/world-population/population-by-country/")
	xhtml = html.fromstring(resp.content)
	country_lines = xhtml.xpath('//*[@id="example2"]/tbody/tr')
	for i in range(min(len(caseLines), len(deadLines), len(recoLines))):
		if i == 0:
			continue
		data = caseLines[i].split(",")
		deadData = deadLines[i].split(",")
		recoData = recoLines[i].split(",")
		try:
			for x1 in range(len(data)):
				if "\"" in data[x1]:
					for x2 in range(x1, len(data)):
						if "\"" in data[x2]:
							data = data[:x1] + [",".join(data[x1:x2+2]).replace("\"", "")] + data[x2+2:]
							deadData = deadData[:x1] + [",".join(deadData[x1:x2+2]).replace("\"", "")] + deadData[x2+2:]
							recoData = recoData[:x1] + [",".join(recoData[x1:x2+2]).replace("\"", "")] + recoData[x2+2:]
							break
		except :
			pass
		if data[0]:
			states[data[0]] = [data[1], data[2], data[3]]
		countryPop = -1
		for line in country_lines:
			if line[1].text_content().lower().strip() == data[1].lower().strip() :
				countryPop = int(line[2].text_content().replace(",", ""))
				break
		if countryPop == -1:
			print(data[1] + " didn't find a population count")
		countries[data[1]] = (data[2], data[3], countryPop)
	sqlCountries = ["INSERT IGNORE INTO countries (name, latitude, longitude, population) VALUES "]
	for country in countries.keys():
		coord = countries[country]
		sqlCountries += ["(\"" + country + "\"," + coord[0] + "," + coord[1] + "," + str(coord[2]) + ") "]
	cursor.execute(sqlCountries[0] + ",\n".join(sqlCountries[1:]) + ";")
	sqlStates = ["INSERT IGNORE INTO states (name, id_country, latitude, longitude) VALUES "]
	for state in states.keys():
		stateData = states[state]
		cursor.execute("SELECT id_country FROM countries WHERE name = \"" + stateData[0] + "\";")
		id = cursor.fetchone()[0]
		sqlStates += ["(\"" + state + "\"," + str(id) + "," + stateData[1] + "," + stateData[2] + ") "]
	cursor.execute(sqlStates[0] + ",".join(sqlStates[1:]) + ";")

		

	for i in range(min(len(caseLines), len(deadLines), len(recoLines))):
		if i == 0:
			continue
		data = caseLines[i].split(",")
		deadData = deadLines[i].split(",")
		recoData = recoLines[i].split(",")
		try:
			for x1 in range(len(data)):
				if "\"" in data[x1]:
					for x2 in range(x1, len(data)):
						if "\"" in data[x2]:
							data = data[:x1] + [",".join(data[x1:x2+2]).replace("\"", "")] + data[x2+2:]
							deadData = deadData[:x1] + [",".join(deadData[x1:x2+2]).replace("\"", "")] + deadData[x2+2:]
							recoData = recoData[:x1] + [",".join(recoData[x1:x2+2]).replace("\"", "")] + recoData[x2+2:]
							break
		except :
			pass


		sqlFacts = ["REPLACE INTO daily_report(id_state, id_country, confirmed, dead, recovered, date) VALUES "] 
		for iDay in range(4, min(len(data), len(deadData), len(recoData))) :
			if data[0] :
				cursor.execute("SELECT id_state FROM states WHERE name = \"" + data[0] + "\"")
				id_state = cursor.fetchone()[0]
			else :
				id_state = 0

			cursor.execute("SELECT id_country FROM countries WHERE name = \"" + data[1] + "\"")
			id_country = cursor.fetchone()[0]
			sqlFacts += ["(" + str(id_state) + ", " + str(id_country) + "," + str(round(float(data[iDay]))) + "," + 
				str(round(float(deadData[iDay]))) + "," + str(round(float(recoData[iDay]))) + ",\"" + str(datetime.datetime.strptime(caseLines[0].split(",")[iDay].strip(), "%m/%d/%y")) + "\")"]
		try:
			cursor.execute(sqlFacts[0] + ",".join(sqlFacts[1:]) + ";")
		except:
			print("erreur sur : ", sqlFacts[0] + ",".join(sqlFacts[1:]) + ";")


	sqlRequests = open("confin.sql", "r").read().split(";")
	sqlRequests = []
	for request in sqlRequests: 
		if request.strip():
			cursor.execute(request)


	print("OK")

def HSL(i, N, sat=0.5) :
	return colorsys.hsv_to_rgb(i*1.0/N, sat, sat) 

class Application(tk.Frame):
	def __init__(self, cursor, master=None):
		super().__init__(master)
		self.master = master

		cursor.execute("SELECT * FROM countries c ORDER BY c.name")
		self.countries = cursor.fetchall()
		cursor.execute("SELECT * FROM states s ")
		self.states = cursor.fetchall()
		cursor.execute("SELECT '0' AS state, d.id_country, SUM(d.confirmed), SUM(d.dead), SUM(d.recovered), d.date  \
				FROM daily_report d GROUP BY d.id_country, d.date ORDER BY d.date ASC;")
		self.reports = cursor.fetchall()

		self.countriesPerList = 20

		self.create_widgets()
		self.pack()

	def create_widgets(self):
		self.topFrame = tk.Frame(self.master)
		self.optionsFrame = tk.Frame(self.master)
		self.countriesLists = []
		for i in range(math.ceil(len(self.countries) / self.countriesPerList)):
			self.countriesLists.append(tk.Listbox(self.topFrame, selectmode="multiple", exportselection=False, height=self.countriesPerList))
			for country in self.countries[(self.countriesPerList*i):(min((self.countriesPerList*(i+1)), len(self.countries)))]:
				self.countriesLists[i].insert(tk.END, country[1])
			self.countriesLists[i].pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
			self.countriesLists[i].bind("<ButtonRelease>", self.displayGraph)
			# self.countriesLists[i].bind("<Double-Button-1>", self.displaySIR)
		self.topFrame.pack(side = tk.TOP, expand=1, fill=tk.BOTH)
		self.optionsFrame.pack(side = tk.TOP, expand=1, fill=tk.BOTH)

		self.displayCurfew = tk.IntVar()
		self.displayCurfew.set(0)
		check = tk.Checkbutton(self.optionsFrame, text="Display curfew date", variable=self.displayCurfew, command=self.displayGraph)
		check.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
		# check.bind("<ButtonRelease>", self.displayGraph)

		options = {"Classic", "New cases"}
		self.calculusChoice = tk.StringVar(self.master)
		self.calculusChoice.set("Classic")
		self.calculusChoice.trace('w', self.displayGraph)
		calculus = tk.OptionMenu(self.optionsFrame, self.calculusChoice, *options)
		calculus.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
		

		self.launch = tk.Button(self.optionsFrame, text="Analyse", command=self.displayGraph)
		self.launch.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

		figure = plt.Figure()
		self.ax = figure.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(figure, master=self.master)
		toolbar = NavigationToolbar2Tk(self.canvas, self.master)
		toolbar.update()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		for i in range(len(self.countriesLists)):
			pass

	def displayGraph(self, *args1, **args2):
		self.ax.clear()
		id_countries = []
		for i, liste in enumerate(self.countriesLists):
			id_countries += [(self.countries[(self.countriesPerList*i):(min(self.countriesPerList*(i+1), len(self.countries)))][j][0], self.countries[(self.countriesPerList*i):(self.countriesPerList*(i+1))][j][1],self.countries[(self.countriesPerList*i):(self.countriesPerList*(i+1))][j][4]) for j in self.countriesLists[i].curselection() ]
		data = []
		for i, country in enumerate(id_countries):
			id_country, country_name, curfew_date = country
			x_axis = []
			data.append([[], [], []])
			reports = [r for r in self.reports if r[1] == id_country]
			before_curfew_data = {"cases":[], "deaths":[], "recovered":[]}
			before_curfew_dates = []
			after_curfew_data = {"cases":[], "deaths":[], "recovered":[]}
			after_curfew_dates = []
			for i_report, report in enumerate(reports):
				# x_axis.append(report[5])
				cases = report[2] 	# Cases
				deaths = report[3]	# Deaths
				recovered = report[4]	# Recovered

				if self.calculusChoice.get().lower() == "classic" : 
					pass
				elif self.calculusChoice.get().lower() == "new cases" and i_report > 0:
					cases -= reports[i_report-1][2] 	# Cases
					deaths -= reports[i_report-1][3]	# Deaths
					recovered -= reports[i_report-1][4]	# Recovered

				if self.displayCurfew.get() == 1 and curfew_date and curfew_date >= report[5]:
					before_curfew_dates.append(report[5])
					before_curfew_data["cases"].append(cases)
					before_curfew_data["deaths"].append(deaths)
					before_curfew_data["recovered"].append(recovered)
				# else:
				# 	print(curfew_date, report[5])
				# 	print("curfew_date <= report[5] : ", curfew_date <= report[5])

				if self.displayCurfew.get() == 0 or not curfew_date or (self.displayCurfew.get() == 1 and curfew_date and curfew_date <= report[5]):
					# print("YES!")
					after_curfew_dates.append(report[5])
					after_curfew_data["cases"].append(cases)
					after_curfew_data["deaths"].append(deaths)
					after_curfew_data["recovered"].append(recovered)

			if self.displayCurfew.get() == 1:
				self.ax.plot(before_curfew_dates, before_curfew_data["cases"], color=HSL(i, len(id_countries), 0.2), linestyle='-')
				self.ax.plot(before_curfew_dates, before_curfew_data["deaths"], color=HSL(i, len(id_countries), 0.2), linestyle='--')
				self.ax.plot(before_curfew_dates, before_curfew_data["recovered"], color=HSL(i, len(id_countries), 0.2), linestyle=':')

			self.ax.plot(after_curfew_dates, after_curfew_data["cases"], color=HSL(i, len(id_countries), 1), linestyle='-', label=country_name)
			self.ax.plot(after_curfew_dates, after_curfew_data["deaths"], color=HSL(i, len(id_countries), 1), linestyle='--')
			self.ax.plot(after_curfew_dates, after_curfew_data["recovered"], color=HSL(i, len(id_countries), 1), linestyle=':')

			# print(after_curfew_data)


		self.ax.set_title('Evolution of cases of COVID-19')
		self.ax.set_xlabel('Date')
		self.ax.set_ylabel('Number of cases')
		self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
		self.canvas.draw()

	def displaySIR(self, event):
		populationRateSusceptible = decimal.Decimal(4/10)
		liste = event.widget
		sel = liste.curselection()
		iListe = [i for i, _liste in enumerate(self.countriesLists) if liste == _liste][0]
		country = self.countries[int(self.countriesPerList) * int(iListe) + int(sel[0])]
		data = {"S":[], "I":[], "R":[]}
		reports = [r for r in self.reports if r[1] == country[0]]
		x_axis = []
		for report in reports:
			R = report[3] + report[4]
			I = report[2] - R
			S = country[5]*populationRateSusceptible - R - I
			print("S:", S, " I:", I, " R:", R)
			data["S"].append(S)
			data["I"].append(I)
			data["R"].append(R)
			x_axis.append(report[5])
		plt.plot(x_axis, data["S"], color="blue", linestyle="-")
		plt.plot(x_axis, data["I"], color="red", linestyle="-")
		plt.plot(x_axis, data["R"], color="green", linestyle="-")
		plt.title("SIR of " + country[1])
		plt.xlabel("Date")
		plt.ylabel("Population")
		plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
		# plt.yscale("log")
		plt.tight_layout()
		plt.show()




mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd=""
)
if not mydb:
	raise Exception("Unable to connect to MySQL on {}@{}".format(usr, host))
print("Connected to the DB!")
cursor = mydb.cursor(buffered=True)
try:
	cursor.execute("USE covid19;")
except:
	pass

try:
	sqlRequests = open("covid19.sql", "r").read().split(";")
	# sqlRequests = []
	for request in sqlRequests: 
		if request.strip():
			cursor.execute(request)
	updateDatabase(cursor)
except:
	print("We were not able to access online data")




root = tk.Tk()
app = Application(cursor = cursor, master=root)
app.mainloop()



