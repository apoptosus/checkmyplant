from flask import Flask, render_template, make_response, send_file, request, jsonify, redirect, url_for, request, session
import base64
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import requests
import os
from datetime import datetime

app = Flask(__name__)

fig_name = None
duration = None
ylabel = None


#home page
@app.route('/')
def home():
    return render_template('home.html')

#about page
@app.route('/why/')
def why():
    return render_template('why.html')

# Retrieve data from database and feed it to '/status/' for gauges and conditions bar
def query_data():

    conn=sqlite3.connect('plant.db')
    curs=conn.cursor()

    time_under = 0
    forecast = []
    temp = []


    #weather for last 30 days
    for row in curs.execute("SELECT FORECAST FROM WEATHER WHERE ROWID%24=0 ORDER BY TIME_COLLECTED DESC LIMIT 30"):
        forecast.append(row[0])
    forecast = ', '.join(forecast)

    #last watered- only takes the first value that is above 60, semi inaccurate
    def last_watered():
        for row in curs.execute("SELECT MOISTURE, TIME_COLLECTED FROM SOIL ORDER BY TIME_COLLECTED DESC"):
            if int(row[0]) > 60:
                last_watered = row[1]
                return last_watered
    last_watered = last_watered()

    #how many hours spent under temp threshold
    for row in curs.execute("SELECT TEMPERATURE FROM DHT11 ORDER BY ROWID DESC LIMIT 730"):
        temp.append(row[0])
    for i in temp:
        if int(i) < 16:
            time_under += 1

    #area from last month
    for row in curs.execute("SELECT AREA FROM FERN ORDER BY ROWID DESC LIMIT 30"):
        lastarea = row[0]

    #justgauge measurements
    for row in curs.execute("SELECT MOISTURE FROM SOIL ORDER BY ROWID DESC LIMIT 1"):
        moisture = row[0]
    for row in curs.execute("SELECT TEMPERATURE FROM DHT11 ORDER BY ROWID DESC LIMIT 1"):
        temperature = row[0]
    for row in curs.execute("SELECT PLANT_LIGHT FROM PHOTOCELL ORDER BY ROWID DESC LIMIT 1"):
        light = row[0]
    for row in curs.execute("SELECT HEIGHT, WIDTH, AREA, TIME_COLLECTED FROM FERN"):
        height = str(row[0])
        width = row[1]
        area = row[2]
        time_now = row[3]
    conn.close()
    return height, width, area, forecast, lastarea, time_under, last_watered, moisture, temperature, light, time_now

#Daily updates of plant
@app.route('/status/')
def status():
    height, width, area, forecast, lastarea, time_under, last_watered, moisture, temperature, light, time_now = query_data()
    templateData = {
        'height': height,
        'width': width,
        'area': area,
        'lastarea': lastarea,
        'forecast': forecast,
        'time_under': time_under,
        'last_watered': last_watered,
        'moisture': moisture,
        'temperature': temperature,
        'light': light,
        'time_now': time_now
	}

    #darksky information
    weather_key = os.getenv('WEATHER_KEY')
    location = os.getenv('LOCATION')

    #access darksky
    try:
        response = requests.get('https://api.forecast.io/forecast/' + weather_key + '/' + location)
        data = response.json()
        cloudcover = str(data["currently"]["cloudCover"])
        cloudcover = float(cloudcover)*10
        icon = data["currently"]["icon"]
    except:
        cloudcover = 'unavailable'
        icon = 'unavailable'

    weatherData = {
        'cloudcover': cloudcover,
        'icon': icon
	}

    return render_template('status.html', **templateData, **weatherData)

#data graphing page
@app.route('/data/', methods=['GET', 'POST'])
def data():

    conn=sqlite3.connect('plant.db')
    curs=conn.cursor()

  #number in db
    for row in curs.execute("SELECT ROWID FROM FERN DESC"):
        total = row[0]

    conn.close()

    #take data from submit
    if request.method == 'POST':
        try:
            fig_name = request.form["sensortype"]
            duration = request.form["duration"]
            duration = int(duration)

        except:
            fig_name = None
            duration = None

    else:
        fig_name = None
        duration = None

    return render_template('data.html', fig_name=fig_name, duration=duration, total=total)


#Disable caching
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


#create mpl plots of sql data in another page
@app.route('/data/<fig_name>/<duration>')
# def fig(which_sensor,how_long):
def fig(fig_name, duration):
    from mpl_plots import mpl_select
    xdata, ydata, ylabel, ylegend = mpl_select(fig_name, duration)

    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel(ylabel)
    axis.set_xlabel('Time')
    axis.legend(loc=0)

    #set legends and multiple y values for different selected plots
    if fig_name[0:3] == "all":
        for i in range(0,len(ydata)):

            axis.plot(xdata[i], ydata[i], alpha = 10)
            # legend_name = mpatches.Patch(label=ylabel[i])
        if fig_name[3::] == "Height & Width":
            axis.legend([ylegend[0], ylegend[1]])
        else:
            axis.legend([ylegend[0], ylegend[1], ylegend[2], ylegend[3], ylegend[4]])
    else:
        axis.plot(xdata, ydata, alpha = 10)
        axis.legend([ylegend[0]])

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    fig.savefig(output)
    output.seek(0)
    return send_file(output,mimetype='image/png')

if __name__ == '__main__':
    app.run() # remember to remove when pushing to heroku

