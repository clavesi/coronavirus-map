import folium
import requests
import json
import csv
import math
from flask import render_template


def map():
    m = folium.Map(
        location=[0, 0],
        tiles='OpenStreetMap',
        zoom_start=2,
        height="95%",
    )

    # Folium auto imports Bootstrap 3, but
    # the navbar uses Bootstrap 5, so change what it uses
    m.default_css = [
        ('leaflet_css', 'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css'),
        ('bootstrap_css', 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'),
        ('awesome_markers_css', 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),
        ('awesome_rotate_css', 'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css')
    ]
    m.default_js = [
        ('leaflet', 'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js'),
        ('jquery', 'https://code.jquery.com/jquery-1.12.4.min.js'),
        ('bootstrap', 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'),
        ('awesome_markers', 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js')
    ]

    latlon = []
    with open('natlatlon.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            latlon.append(row['Country'])
            latlon.append(row['Latitude'])
            latlon.append(row['Longitude'])

    pop = []
    with open('natpop2020.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pop.append(row['Country'])
            pop.append(row['Population'])

    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    cases = json.loads(info.text)

    confirmedCasesList = []
    ratesList = []
    percapitaList = []
    countries = []

    # This is separate because the second loop requires the max
    # value of the list in this loop
    for case in cases:
        confirmedCasesList.append(cases[case][-1]['confirmed'])
        ratesList.append(cases[case][-1]['deaths'] /
                         cases[case][-1]['confirmed'])
        if case in latlon:
            percapitaList.append(
                (cases[case][-1]['confirmed'] / int(pop[pop.index(case) + 1])) * 100000)

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

    testlist = []
    for case in cases:
        testlist.append(case)

    for count in pop:
        if pop.index(count) % 2 == 0:
            if count not in testlist:
                print(count)

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

    # Read map.html and save a variable that has the header added
    f = open("templates/map.html", "r")
    text = f.read()
    if '<body>' in text:
        bodyIndex = text.index('<body>') + 6
        htmlText = '''
                    <nav class="navbar navbar-expand-md navbar-dark" style="background-color: #222222;">
                        <div class="container-fluid">
                            <a class="navbar-brand" href="/">
                                <img src="https://www.pfma.org/uploads/1/3/2/9/132961961/published/covid-icon-red-no-background.png?1616616356"
                                    alt="" width="30" height="30" class="d-inline-block align-text-top">Visualize COVID-19</a>
                            <button class="navbar-toggler ml-auto" type="button" data-bs-toggle="collapse" data-bs-target="#collapseNavbar">
                                <span class="navbar-toggler-icon"></span>
                            </button>
                            <div class="navbar-collapse collapse" id="collapseNavbar">
                                <ul class="navbar-nav ms-auto">
                                    <li class="nav-item active">
                                        <a class="nav-link" href="/map">Map</a>
                                    </li>
                                    <li class="nav-item">
                                        <a class="nav-link" href="/graphs">Graphs</a>
                                    </li>
                                    <li class="nav-item">
                                        <a class="nav-link" href="https://github.com/clavesi/coronavirus-map">GitHub</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </nav>
                    <link rel="stylesheet" type="text/css" href="{{ url_for('static',filename='css/map.css') }}">
                    </script>
                    '''
        finalText = text[:bodyIndex] + htmlText + text[bodyIndex:]
    f.close()

    # Write variable to file
    f = open("templates/map.html", "w+")
    f.write(finalText)
    f.close()

    return render_template('map.html')
