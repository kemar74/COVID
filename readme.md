# COVID visual
=====

## Data used :
In this project I started using data from corona.lmao.ninja  
But recently they let down the v1 version to a v2, loosing some data.  
  
Then I continued by using [The Center for Systems Science and Engineering's data](https://github.com/CSSEGISandData/COVID-19) who made [a great application](https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) for tracking COVID-19 evolution. But, Iwanted to do mine.  
  
Also, we've used [WorldoMeter's](https://www.worldometers.info/world-population/population-by-country/) data to track the total population of each country, but, that wasn't really useful in the project...

## Requirement
This project is using Python 3 and MySQL.

## Usage
First, start your MySQL server.  
To use this script, simply open a terminal, go to the location of the file, and type  
```console
python covid2.py
```
This will get data from CSSE and WorldoMeter, store it in your MySql server and then launch the program.  

It is a quite easy interface :  
![mainFrame]  

To analyse a country, select it from the country list. It will show you the total cases (full line), deaths (dashed) and recovered (dotted) amounts. Select multiple countries to compare them.  
Use the ```matplotlib```'s tools to zoom in the graph.  

I wanted to add a SIR representation by double-clicking on a country, but the data wasn't revelant as COVID-19 only touches (currently) less than 0.15 of the population. So the graph just looks like there is no change in time... If you know how to do something representative, please contact me (marc.hartley@hotmail.com).  
This functionality is still accessible if you uncomment line n° ~142 : ```self.countriesLists[i].bind("<Double-Button-1>", self.displaySIR)``` from covid2.py  

Have fun!