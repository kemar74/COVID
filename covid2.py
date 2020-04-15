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
import pickle
import os


def concatIfQuotes(data):
	for x1 in range(len(data)-1):
		if "\"" in data[x1]:
			for x2 in range(x1, len(data)-1):
				if "\"" in data[x2]:
					data = data[:x1] + [",".join(data[x1:x2+2]).replace("\"", "")] + data[x2+2:]
	return data

def getDataWithoutDB(forceUpdate=False):
	if not forceUpdate and os.path.exists("donnees_corona_virus.obj") : 
		lastModified = datetime.datetime.fromtimestamp(os.path.getmtime("donnees_corona_virus.obj"))
		if datetime.datetime.now().date() == lastModified.date() :
			try:
				return pickle.load(open("donnees_corona_virus.obj", "rb"))
			except:
				pass
	print("Fetching data without database...")
	url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
	caseURL = url + "time_series_covid19_confirmed_global.csv"
	deadURL = url + "time_series_covid19_deaths_global.csv"
	recoURL = url + "time_series_covid19_recovered_global.csv"

	caseLines = requests.get(caseURL).text.split("\n")
	deadLines = requests.get(deadURL).text.split("\n")
	recoLines = requests.get(recoURL).text.split("\n")
	states = {}
	countries = {}
	resp = requests.get(url = "https://www.worldometers.info/world-population/population-by-country/")
	xhtml = html.fromstring(resp.content)
	country_lines = xhtml.xpath('//*[@id="example2"]/tbody/tr')
	for i in range(min(len(caseLines), len(deadLines), len(recoLines))):
		if i == 0:
			continue
		data = concatIfQuotes(caseLines[i].split(","))
		deadData = concatIfQuotes(deadLines[i].split(","))
		recoData = concatIfQuotes(recoLines[i].split(","))

		reports = {'cases': {}, 'deaths':{}, 'recovered': {} }
		for iDay in range(4, len(data)) :
			reports['cases'][datetime.datetime.strptime(caseLines[0].split(",")[iDay].strip(), "%m/%d/%y")] = int(data[iDay])
			if data[1] in countries:
				countries[data[1]]['daily_reports']['cases'][datetime.datetime.strptime(caseLines[0].split(",")[iDay].strip(), "%m/%d/%y")] += int(data[iDay])
		for iDay in range(4, len(deadData)) :
			reports['deaths'][datetime.datetime.strptime(deadLines[0].split(",")[iDay].strip(), "%m/%d/%y")] = int(deadData[iDay])
			if data[1] in countries:
				countries[data[1]]['daily_reports']['deaths'][datetime.datetime.strptime(deadLines[0].split(",")[iDay].strip(), "%m/%d/%y")] += int(deadData[iDay])
		for iDay in range(4, len(recoData)) :
			# print(recoData[1])
			# print(len(recoLines[0].split(",")), iDay)
			reports['recovered'][datetime.datetime.strptime(recoLines[0].split(",")[iDay].strip(), "%m/%d/%y")] = int(recoData[iDay])
			if data[1] in countries:
				countries[data[1]]['daily_reports']['recovered'][datetime.datetime.strptime(recoLines[0].split(",")[iDay].strip(), "%m/%d/%y")] += int(recoData[iDay])

		if data[0]:
			states[data[0]] = {'name':data[0], 'latitude':data[2], 'longitude':data[3], 'id_state':len(states)//2, 'country_name':data[1], 'daily_reports':reports}
		countryPop = -1
		for line in country_lines:
			if line[1].text_content().lower().strip() == data[1].lower().strip() :
				countryPop = int(line[2].text_content().replace(",", ""))
				break
		if countryPop == -1:
			print("Warning : ",data[1] + " didn't find a population count")

		if data[1] not in countries:
			countries[data[1]] = {'id_country':len(countries)//2, 'name':data[1], 'latitude':data[2], 'longitude':data[3], 'population':countryPop, 'curfew_date':None, 'daily_reports':reports}
		countries[countries[data[1]]['id_country']] = countries[data[1]]

	for state in states:
		country = countries[states[state]['country_name']]
		states[state]['country'] = country
		country['state'] = states[state]
		countries[country['id_country']] = country 

	pickle.dump({'countries' : countries, 'states' : states}, open("donnees_corona_virus.obj", "wb"))
	return {'countries' : countries, 'states' : states}



def HSL(i, N, sat=0.5) :
	return colorsys.hsv_to_rgb(i*1.0/N, sat, sat) 


class Splash(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self, parent)
		self.title("Splash")

		## required to make window show before the program gets to the mainloop
		self.update()

class Application(tk.Frame):
	def __init__(self, cursor=None, master=None, forceUpdate=False):
		super().__init__(master)

		self.master = master
		self.master.minsize(100, 50)
		self.master.title("Patience...")
		label = tk.Label(self.master, text = 'Chargement des données en cours, merci de patienter...', width=100)
		label.pack()
		self.update()

		data = getDataWithoutDB(forceUpdate)

		self.master.title("COVID-19")
		label.pack_forget()
		
		self.countries = data['countries']
		self.states = data['states']
		self.countries = sorted([self.countries[i] for i in self.countries if isinstance(i, int)], key=lambda x: x['name'])
		self.states = [self.states[i] for i in self.states if isinstance(i, int)]

		self.countriesPerList = 20

		self.create_widgets()
		self.pack()

	def create_widgets(self):
		self.topFrame = tk.Frame(self.master)
		self.optionsFrame = tk.Frame(self.master)
		self.displayOptionsFrame = tk.Frame(self.optionsFrame)
		self.countriesLists = []
		for i in range(math.ceil(len(self.countries) / self.countriesPerList)):
			self.countriesLists.append(tk.Listbox(self.topFrame, selectmode="multiple", exportselection=False, height=self.countriesPerList))
			for country in self.countries[(self.countriesPerList*i):(min((self.countriesPerList*(i+1)), len(self.countries)))]:
				self.countriesLists[i].insert(tk.END, country['name'])
			self.countriesLists[i].pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
			self.countriesLists[i].bind("<ButtonRelease>", self.displayGraph)
			# self.countriesLists[i].bind("<Double-Button-1>", self.displaySIR)
		self.topFrame.pack(side = tk.TOP, expand=1, fill=tk.BOTH)
		self.optionsFrame.pack(side = tk.TOP, expand=1, fill=tk.BOTH)
		self.displayOptionsFrame.pack(side = tk.LEFT, expand=1, fill=tk.BOTH)

		self.displayCurfew = tk.IntVar()
		self.displayCurfew.set(0)
		check = tk.Checkbutton(self.optionsFrame, text="Display curfew date", variable=self.displayCurfew, command=self.displayGraph)
		# check.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
		# check.bind("<ButtonRelease>", self.displayGraph)

		self.displayVariables = {'cases': tk.IntVar(self), 'deaths' : tk.IntVar(self), 'recovered' : tk.IntVar(self)}
		self.displayVariables['cases'].set(1)
		self.displayVariables['deaths'].set(1)
		self.displayVariables['recovered'].set(1)
		displayOption = tk.Checkbutton(self.displayOptionsFrame, text="Afficher les cas", variable=self.displayVariables['cases'], command=self.displayGraph)
		displayOption.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
		displayOption = tk.Checkbutton(self.displayOptionsFrame, text="Afficher les décès", variable=self.displayVariables['deaths'], command=self.displayGraph)
		displayOption.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
		displayOption = tk.Checkbutton(self.displayOptionsFrame, text="Afficher les rétablis", variable=self.displayVariables['recovered'], command=self.displayGraph)
		displayOption.pack(side=tk.TOP, expand=1, fill=tk.BOTH)


		options = {"Classique", "Rapport quotidien"}
		self.calculusChoice = tk.StringVar(self.master)
		self.calculusChoice.set("Classique")
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
		if self.displayVariables['cases'].get():
			self.ax.plot([], color="black", linestyle="-", label="Cas confirmé")
		if self.displayVariables['deaths'].get():
			self.ax.plot([], color="black", linestyle="--", label="Décès")
		if self.displayVariables['recovered'].get():
			self.ax.plot([], color="black", linestyle=":", label="Rétablis")
		selectedCountries = []
		for i, liste in enumerate(self.countriesLists):
			selectedCountries += [self.countries[(self.countriesPerList*i):(min(self.countriesPerList*(i+1), len(self.countries)))][j] for j in self.countriesLists[i].curselection() ]
		data = []
		for i, country in enumerate(selectedCountries):

			before_curfew_data = {"cases":[], "deaths":[], "recovered":[]}
			after_curfew_data = {"cases":[], "deaths":[], "recovered":[]}

			if country['curfew_date'] and self.displayCurfew.get == 1:
				before_curfew_data['cases'] = [int(country['daily_reports']['cases'][key]) for key in country['daily_reports']['cases'] if key <= country['curfew_date']]
				before_curfew_data['deaths'] = [int(country['daily_reports']['deaths'][key]) for key in country['daily_reports']['deaths'] if key <= country['curfew_date']]
				before_curfew_data['recovered'] = [int(country['daily_reports']['recovered'][key]) for key in country['daily_reports']['recovered'] if key <= country['curfew_date']]
				after_curfew_data['cases'] = [int(country['daily_reports']['cases'][key]) for key in country['daily_reports']['cases'] if key >= country['curfew_date']]
				after_curfew_data['deaths'] = [int(country['daily_reports']['deaths'][key]) for key in country['daily_reports']['deaths'] if key >= country['curfew_date']]
				after_curfew_data['recovered'] = [int(country['daily_reports']['recovered'][key]) for key in country['daily_reports']['recovered'] if key >= country['curfew_date']]
			else :
				after_curfew_data['cases'] = [int(country['daily_reports']['cases'][key]) for key in country['daily_reports']['cases']]
				after_curfew_data['deaths'] = [int(country['daily_reports']['deaths'][key]) for key in country['daily_reports']['deaths']]
				after_curfew_data['recovered'] = [int(country['daily_reports']['recovered'][key]) for key in country['daily_reports']['recovered']]

			if self.calculusChoice.get().lower() == "classique":
				pass
			elif self.calculusChoice.get().lower() == "rapport quotidien":
				before_curfew_data['cases'] = [0 if i == 0 else before_curfew_data['cases'][i] - before_curfew_data['cases'][i-1] for i in range(len(before_curfew_data['cases']))]
				before_curfew_data['deaths'] = [0 if i == 0 else before_curfew_data['deaths'][i] - before_curfew_data['deaths'][i-1] for i in range(len(before_curfew_data['deaths']))]
				before_curfew_data['recovered'] = [0 if i == 0 else before_curfew_data['recovered'][i] - before_curfew_data['recovered'][i-1] for i in range(len(before_curfew_data['recovered']))]
				after_curfew_data['cases'] = [0 if i == 0 else after_curfew_data['cases'][i] - after_curfew_data['cases'][i-1] for i in range(len(after_curfew_data['cases']))]
				after_curfew_data['deaths'] = [0 if i == 0 else after_curfew_data['deaths'][i] - after_curfew_data['deaths'][i-1] for i in range(len(after_curfew_data['deaths']))]
				after_curfew_data['recovered'] = [0 if i == 0 else after_curfew_data['recovered'][i] - after_curfew_data['recovered'][i-1] for i in range(len(after_curfew_data['recovered']))]
		
			self.ax.plot([], color=HSL(i, len(selectedCountries), 1), label=country['name'])
			if self.displayVariables['cases'].get():
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["cases"].keys() if self.displayCurfew.get() == 1 and x <= country['curfew_date']], before_curfew_data["cases"], color=HSL(i, len(selectedCountries), 0.2), linestyle='-')
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["cases"].keys() if self.displayCurfew.get() == 0 or x >= country['curfew_date']], after_curfew_data["cases"], color=HSL(i, len(selectedCountries), 1), linestyle='-')
			if self.displayVariables['deaths'].get():
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["deaths"].keys() if self.displayCurfew.get() == 1 and x <= country['curfew_date']], before_curfew_data["deaths"], color=HSL(i, len(selectedCountries), 0.2), linestyle='--')
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["deaths"].keys() if self.displayCurfew.get() == 0 or x >= country['curfew_date']], after_curfew_data["deaths"], color=HSL(i, len(selectedCountries), 1), linestyle='--')
			if self.displayVariables['recovered'].get():
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["recovered"].keys() if self.displayCurfew.get() == 1 and x <= country['curfew_date']], before_curfew_data["recovered"], color=HSL(i, len(selectedCountries), 0.2), linestyle=':')
				self.ax.plot([x.strftime("%d/%m") for x in country['daily_reports']["recovered"].keys() if self.displayCurfew.get() == 0 or x >= country['curfew_date']], after_curfew_data["recovered"], color=HSL(i, len(selectedCountries), 1), linestyle=':')




		self.ax.set_title('Evolution of cases of COVID-19')
		self.ax.set_xlabel('Date')
		self.ax.set_ylabel('Number of cases')
		self.ax.set_xticks([x.strftime("%d/%m") for x in country['daily_reports']["recovered"].keys() if x.day in (1, 7, 15, 22) or x.date() == datetime.datetime.now().date()]) # Tous les 15 jours
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


root = tk.Tk()
app = Application(cursor = None, master=root, forceUpdate=False)
app.mainloop()



