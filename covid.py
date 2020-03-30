import colorsys
import numpy as np
import matplotlib.pyplot as plt
import json
import importData
import math
import datetime

api = "https://corona.lmao.ninja/"
countries = ["france", "china"]#, "uk", "s. korea", "italy", "vietnam", "usa", "spain", "germany", "switzerland"]
history = {}

confinDate = {
	"china" 		: "01-24-2020",
	"italy" 		: "03-10-2020",
	"spain" 		: "03-14-2020",
	"liban" 		: "03-15-2020",
	"liban" 		: "03-15-2020",
	"czechia" 		: "03-16-2020",
	"austria" 		: "03-16-2020",
	"france" 		: "03-17-2020",
	"israel" 		: "03-17-2020",
	"venezuela" 	: "03-17-2020",
	"belgium" 		: "03-18-2020",
	"argentina"		: "03-19-2020",
	"rwanda" 		: "03-22-2020",
	"tunisia" 		: "03-22-2020",
	"irak" 			: "03-22-2020",
	"bolivia" 		: "03-22-2020",
	"usa" 			: "03-22-2020", # Pour NY et Californie
	"uk" 			: "03-23-2020",
	"greece" 		: "03-23-2020",
	"germany" 		: "03-23-2020",
	"south africa" 	: "03-23-2020",
	"brazil" 		: "03-24-2020",
	"colombia" 		: "03-24-2020",
}
def getColor(i, N):
	return colorsys.hsv_to_rgb(i*1.0/N, 0.5, 0.5)
def mean(a):
	return sum(a)/len(a)
def median(a):
	a.sort()
	return a[len(a)//2]

def smoothGraph(values, smoothness=2) :
	if smoothness == 0:
		return values
	smooth = []
	for loop in range(smoothness):
		smooth = []
		for i in range(len(values)):
			_index = max(0, i - 2)
			index_ = min(i + 2, len(values))
			smooth.append(mean(values[_index:index_] + [values[i]]))
		values = smooth
	return smooth


for i, country in enumerate(countries):
	history[country] = {'data' : importData.importData(api + "historical/" + country, "data")["timeline"]}
	history[country]['cases'] = {} #history[country]['data']['cases']
	history[country]['deaths'] = {} #history[country]['data']['deaths']
	history[country]['recovered'] = {} #history[country]['data']['recovered']
	history[country]["dates"] = []
	for iDay in history[country]["data"]["cases"].keys():
		splittedDate = iDay.split("/")
		day = datetime.date(int("20" + splittedDate[2]), int(splittedDate[0]), int(splittedDate[1]))
		history[country]['cases'][day] = history[country]["data"]['cases'][iDay]
		history[country]['deaths'][day] = history[country]["data"]['deaths'][iDay]
		history[country]['recovered'][day] = history[country]["data"]['recovered'][iDay]
		history[country]['dates'].append(day.strftime("%d/%m"))

	history[country]["color"] = getColor(i, len(countries))
	if country in confinDate:
		history[country]["confinement"] = datetime.datetime.strptime(confinDate[country], "%m-%d-%Y").date()
	else:
		history[country]["confinement"] = None

for country in countries:
	x = history[country]['dates']
	y_before = [ history[country]['cases'][day] for day in history[country]['cases'].keys() 
					if not history[country]["confinement"] or day < history[country]["confinement"] ]
	y_after = [history[country]['cases'][day] for day in history[country]['cases'].keys() 
					if history[country]["confinement"] and day >= history[country]["confinement"] ]

	if len(y_after) >= 1:
		y_before.append(y_after[0])
	plt.plot(x[:len(y_before)], y_before, label=country.capitalize(), linestyle="-", c=history[country]["color"])
	if len(y_after):
		plt.plot(x[-len(y_after):], y_after, linestyle="--", c=history[country]["color"])

	plt.title('Evolution of cases of COVID-19')
	plt.xlabel('Date')
	plt.ylabel('Number of cases')
	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.tight_layout()
	plt.xticks([i*10 for i in range(len(history[country]["cases"].keys())//10)])

plt.show()

# for country in countries:
# 	x = history[country]['dates']
# 	y = list(history[country]['recovered'].values())
# 	plt.plot(x, y, linestyle="--", c=history[country]["color"])
# 	plt.title('Recovering of COVID per country')
# 	plt.xlabel('Date')
# 	plt.ylabel('Recovered')
# plt.show()

# for country in countries:
# 	x = history[country]['dates']
# 	y = smoothGraph(list(history[country]['deaths'].values()), 3)
# 	plt.plot(x, y, linestyle=":", c=history[country]["color"])
# 	plt.title('Recovering of COVID per country')
# 	plt.xlabel('Date')
# 	plt.ylabel('Deaths')

# plt.show()

# for country in countries:
# 	a = [0, 0]
# 	for i in range(1, len(history[country]["deaths"]) -1 ) :
# 		# a.append(0 if list(history[country]["deaths"].values())[i] == 0 else (list(history[country]["deaths"].values())[i+1] - list(history[country]["deaths"].values())[i])/list(history[country]["deaths"].values())[i])
# 		deathsToday = list(history[country]["deaths"].values())[i+1] - list(history[country]["deaths"].values())[i]
# 		deathsYesterday = list(history[country]["deaths"].values())[i] - list(history[country]["deaths"].values())[i-1]
# 		a.append(0 if deathsYesterday == 0 else deathsToday / deathsYesterday)
# 	# plt.plot(list(history[country]["deaths"].keys()), a, linestyle="-", color=history[country]["color"])

# 	smoothed = smoothGraph(a, 3)
# 	plt.plot(list(history[country]["deaths"].keys()), smoothed, linestyle="-", color=history[country]["color"], label=country)
# 	plt.xticks([i*5 for i in range(len(history[country]["deaths"])//5)])
# 	plt.text(len(history[country]["deaths"])+1, smoothed[-1], country, color=history[country]["color"])
# 	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# 	plt.tight_layout()

# plt.show()


# for country in countries:
# 	x = history[country]['dates']
# 	y = []
# 	for i in range(len(history[country]['cases'])):
# 		y.append(list(history[country]['cases'].values())[i] - list(history[country]['recovered'].values())[i] - list(history[country]['deaths'].values())[i])
# 	plt.plot(x, y, label=country.capitalize(), linestyle="-", c=history[country]["color"])

# 	plt.title('Evolution of current cases of COVID-19')
# 	plt.xlabel('Date')
# 	plt.ylabel('Number of cases')
# 	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# 	plt.tight_layout()
# 	plt.xticks([i*10 for i in range(len(history[country]["cases"].keys())//10)])

# plt.show()