def mpl_select(fig_name, duration):
    import matplotlib.pyplot as plt
    from matplotlib import dates as mpl_dates
    from datetime import datetime, timedelta
    import sqlite3
    from dateutil import parser
    from dateutil import parser

    duration = int(duration)*24

    plt.style.use('seaborn')
    ylegend = []
    ydata = []
    xdata = []

    conn = sqlite3.connect('plant.db')
    c = conn.cursor()

    ylabel = fig_name[3::]

    #check the type of form collected
    if fig_name[0:3] == 'dht':
        dht_time = []
        temperature = []
        humidity = []

        #execute the desired query
        for row in c.execute("SELECT * FROM DHT11 ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
            dht_time.append(parser.parse(str(row[0])))
            temperature.append(row[1])
            humidity.append(row[2])
        conn.close()

        xdata = dht_time

        #access the desired values: xvars,yvars,figure legend, and labels for title
        if ylabel == "Temperature":
            ydata = temperature
            ylegend.append('Temperature')

        if ylabel == "Humidity":
            ydata = humidity
            ylegend.append('Humidity')

        return xdata, ydata, ylabel, ylegend

    #repeat
    if fig_name[0:3] == 'pho':
        light_time = []
        plant_light = []
        window_light = []

        for row in c.execute("SELECT * FROM PHOTOCELL ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
            light_time.append(parser.parse(row[0]))
            plant_light.append(row[1])
            window_light.append(row[2])
        conn.close()

        xdata = light_time
        ydata = plant_light
        ylegend.append('Light')

        return xdata, ydata, ylabel, ylegend

    if fig_name[0:3] == 'cap':
        soil_time = []
        moisture = []

        for row in c.execute("SELECT * FROM SOIL ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
            soil_time.append(parser.parse(row[1]))
            moisture.append(row[0])

        conn.close()

        xdata = soil_time
        ydata = moisture
        ylegend.append('Moisture')

        return xdata, ydata, ylabel, ylegend

    if fig_name[0:3] == 'pcv' or fig_name[0:3] == 'all':
        pcv_time = []
        height = []
        width = []
        area = []
        duration = duration/24

        for row in c.execute("SELECT HEIGHT,WIDTH,AREA,TIME_COLLECTED FROM FERN ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
            pcv_time.append(parser.parse(row[3]))
            height.append(row[0])
            width.append(row[1])
            area.append(row[2])




        if ylabel == "Height & Width":

            ylegend.append('Height')
            ylegend.append('Width')
            ydata.append(height)
            ydata.append(width)
            xdata.append(pcv_time)
            xdata.append(pcv_time)


        if ylabel == "Area":
            xdata = pcv_time
            ydata = area
            ylegend.append('Area')

        if ylabel == "Height,Width,Light,Moisture,Temperature":

            height = []
            width = []
            light = []
            moisture = []
            temperature = []

            pcv_time = []
            cap_time = []
            light_time = []
            dht_time = []

            for row in c.execute("SELECT HEIGHT, WIDTH, TIME_COLLECTED FROM FERN ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
                height.append(row[0])
                width.append(row[1])
                pcv_time.append(row[2])
            for row in c.execute("SELECT MOISTURE, TIME_COLLECTED FROM SOIL ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
                moisture.append(row[0])
                cap_time.append(row[1])
            for row in c.execute("SELECT PLANT_LIGHT, TIME_COLLECTED FROM PHOTOCELL ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
                light.append(row[0])
                light_time.append(row[1])
            for row in c.execute("SELECT TEMPERATURE, TIME_COLLECTED FROM DHT11 ORDER BY TIME_COLLECTED DESC LIMIT ?", (duration,)):
                temperature.append(row[0])
                dht_time.append(row[0])

            ydata.append(height)
            ydata.append(width)
            ydata.append(light)
            ydata.append(moisture)
            ydata.append(temperature)

            ylegend.append('Height')
            ylegend.append('Width')
            ylegend.append('Light')
            ylegend.append('Moisture')
            ylegend.append('Temperature')

            xdata.append(pcv_time)
            xdata.append(pcv_time)
            xdata.append(light_time)
            xdata.append(cap_time)
            xdata.append(dht_time)

    conn.close()


    return xdata, ydata, ylabel, ylegend
