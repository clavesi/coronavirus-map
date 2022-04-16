import folium
import requests
import json
import csv
import math
from flask import render_template


def map():
    """
    It reads a JSON file, a CSV file, and a CSV file, and then creates a map with circles on it.
    :return: The map.html file is being returned.
    """
    m = folium.Map(
        location=[0, 0],
        tiles='OpenStreetMap',
        zoom_start=2,
        height="95%",
    )

    # Reading a CSV file and appending the data to a list.
    latlon = []
    with open('natlatlon.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            latlon.append(row['Country'])
            latlon.append(row['Latitude'])
            latlon.append(row['Longitude'])

    # Reading a CSV file and appending the data to a list.
    pop = []
    with open('natpop2020.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pop.append(row['Country'])
            pop.append(row['Population'])

    # Getting the data from the website and loading it into a JSON file.
    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    cases = json.loads(info.text)

    # Creating empty lists.
    confirmedCasesList = []
    ratesList = []
    percapitaList = []
    countries = []

    # Creating a list of confirmed cases, a list of death rates, and a list of per capita cases.
    for case in cases:
        # This is separate because the second loop requires the max
        # value of the list in this loop
        confirmedCasesList.append(cases[case][-1]['confirmed'])
        ratesList.append(cases[case][-1]['deaths'] /
                         cases[case][-1]['confirmed'])
        if case in latlon:
            percapitaList.append(
                (cases[case][-1]['confirmed'] / int(pop[pop.index(case) + 1])) * 100000)

    # Creating a list of countries, their latitudes, longitudes, confirmed cases, deaths, radius,
    # color, and per capita cases.
    for case in cases:
        confirmed = cases[case][-1]['confirmed']
        deaths = cases[case][-1]['deaths']

        if case in latlon:
            if not confirmed == 0:
                lat = latlon[latlon.index(case) + 1]
                lon = latlon[latlon.index(case) + 2]
                population = int(pop[pop.index(case) + 1])
                percapita = (confirmed / population) * 100000

                radius = math.sqrt(max(percapitaList) * percapita) * 4

                color = int((deaths / confirmed) * 100)
                sqrtfunc = int(math.sqrt(2048 * color))
                # Convert red RGB to hex
                color = '#{:02x}{:02x}{:02x}'.format(sqrtfunc, 0, 0)

                countries.append([lat, lon, case, confirmed,
                                  deaths, radius, color, percapita])

    # Creating a popup for each country and adding a circle to the map.
    for country in countries:
        popup = folium.Popup(
            f'{country[2]}:<br>{country[3]} cases,<br>{round(country[7], 2)} per 100k,<br>{country[4]} deaths,<br>{round(country[4]/country[3]*100, 2)}% mortality', max_width=1500)
        circle = folium.Circle(
            location=[country[0], country[1]],
            radius=country[5],
            popup=popup,
            color=country[6],
            fill=True,
            fill_color=country[6],
            fill_opacity=.3
        ).add_to(m)
    m.save(outfile='templates/map.html')

    # Read map.html and save a variable that has the navbar added
    f = open("templates/map.html", "r")
    text = f.read()
    if '<body>' in text:
        bodyIndex = text.index('<body>') + 6
        htmlText = '''
                    <nav>
                        <ul class="nav-links">
                            <li><a href="/">Visualize COVID-19</a></li>
                            <li><a href="/map">Map</a></li>
                            <li><a href="/graphs">Graphs</a></li>
                        </ul>
                    </nav>
                    <link rel="stylesheet" type="text/css" href="{{ url_for('static',filename='css/map.css') }}">
                    '''
        finalText = text[:bodyIndex] + htmlText + text[bodyIndex:]
    f.close()

    # Write variable to file
    f = open("templates/map.html", "w")
    f.write(finalText)
    f.close()

    return render_template('map.html')
