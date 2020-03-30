import os
import requests
import json

def urlToFile(url) :
	return url.replace("https://corona.lmao.ninja/", "").replace("/", "_")

def importData(url, folder) :
	data = requests.get(url).text
	try:
		os.makedirs(folder)
	except:
		pass

	with open(os.path.join(folder, urlToFile(url)), "w") as file:
		file.write(data)
	return json.loads(data)

def getData(url, folder):
	fileURL = os.path.join(folder, urlToFile(url))

	data = ""
	if os.path.exists(fileURL):
		with open(fileURL, "r") as file:
			data = file.read()
			return json.loads(data)
	return False

def importOrGetData(url, folder) :
	fromLocal = getData(url, folder)
	if fromLocal:
		return fromLocal
	return importData(url, folder)
