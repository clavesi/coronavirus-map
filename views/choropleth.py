from flask import render_template
import folium
import requests
import json
import csv
import pandas as pd


def choropleth():
    m = folium.Map(location=[0, 0], zoom_start=2, height="94%")
    m.default_css = [
        ('leaflet_css', 'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css'),
        ('bootstrap_css', 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'),
        ('awesome_markers_css', 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),
        ('awesome_rotate_css', 'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css')
    ]
    m.default_js = [
        ('leaflet', 'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js'),
        ('jquery', 'https://code.jquery.com/jquery-1.12.4.min.js'),
        ('awesome_markers', 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js')
    ]

    write_csv()
    country_geo = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    country_data = pd.read_csv("./data/alpha3_cases.csv")

    folium.Choropleth(
        geo_data=country_geo,
        name="choropleth",
        data=country_data,
        columns=["Alpha-3", "Cases Per Capita"],
        key_on="feature.id",
        fill_color="Reds",
        fill_opacity=.8,
        line_opacity=1,
        legend_name="Per Capita (100k)",
    ).add_to(m)

    m.save(outfile='templates/choropleth.html')

    # Read choropleth.html and save a variable that has the navbar added
    f = open("templates/choropleth.html", "r")
    text = f.read()
    if '<body>' in text:
        bodyIndex = text.index('<body>') + 6
        htmlText = '''
                    <nav class="navbar navbar-expand-md navbar-dark" style="background-color: #222222;">
                        <div class="container-fluid">
                            <a class="navbar-brand" href="/">
                                <img src="https://www.pfma.org/uploads/1/3/2/9/132961961/published/covid-icon-red-no-background.png?1616616356"
                                    alt="" width="30" height="30" class="d-inline-block align-text-top">
                                Visualize COVID-19
                            </a>
                            <button class="navbar-toggler ml-auto" type="button" data-bs-toggle="collapse"
                                data-bs-target="#collapseNavbar">
                                <span class="navbar-toggler-icon"></span>
                            </button>
                            <div class="navbar-collapse collapse" id="collapseNavbar">
                                <ul class="navbar-nav ms-auto">
                                    <li class="nav-item active">
                                        <a class="nav-link" href="/bubble">Bubble</a>
                                    </li>
                                    <li class="nav-item active">
                                        <a class="nav-link" href="/choropleth">Choropleth</a>
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
                    <link rel="stylesheet" type="text/css" href="{{ url_for('static',filename='css/navbar.css') }}">
                    </script>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
        crossorigin="anonymous"></script>
                    '''
        finalText = text[:bodyIndex] + htmlText + text[bodyIndex:]
    f.close()

    # Write variable to file
    f = open("templates/choropleth.html", "w+")
    f.write(finalText)
    f.close()

    return render_template('choropleth.html')


def write_csv():
    fields = ['Alpha-3', 'Cases Per Capita']
    rows = []

    pop = []
    with open('./data/natpop2020.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pop.append(row['Country'])
            pop.append(row['Population'])

    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    cases = json.loads(info.text)
    covid_countries = []
    for case in cases:
        covid_countries.append(case)

    countries_json_path = "./data/countries.json"
    with open(countries_json_path, 'r') as f:
        contents = json.loads(f.read())
        for country in contents:
            if country['name'] in covid_countries:
                confirmed = cases[country['name']][-1]['confirmed']
                population = int(pop[pop.index(country['name']) + 1])
                percapita = int((confirmed / population) * 100000)

                row = [str.upper(country['alpha3']), str(percapita)]
                rows.append(row)

    with open("data/alpha3_cases.csv", 'w+') as csvfile:
        csvwriter = csv.writer(csvfile)

        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
