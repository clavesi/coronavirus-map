import folium, requests, json, csv, math
from flask import Flask, render_template

'''
Again, fix colors and circle size, maybe finally implement per capita with a population csv, 
    but that would be another thing to keep the same
When the per capita is implemented, the formula for size should hopefully be a bit easier to 
    do. Perhaps there is some way to change size differences based on location on the map. 
    There has to be some calculation for Spherical Mercator Projection.
(Cases / Population) * 100,000
Fix fonts, currently only the map page has them
Fix headers, the "Visualize COVID-19" is causing it's box to be longer
Adjust README.fr
'''

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def coronavirusMap():
    m = folium.Map(
        location=[0, 0],
        tiles='OpenStreetMap',
        zoom_start=2,
        height="95%",
    )

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
        ratesList.append(cases[case][-1]['deaths'] / cases[case][-1]['confirmed'])
        if case in latlon:
            percapitaList.append((cases[case][-1]['confirmed'] / int(pop[pop.index(case) + 1])) * 100000)

    for case in cases:
        confirmed = cases[case][-1]['confirmed']
        deaths = cases[case][-1]['deaths']
        recovered = cases[case][-1]['recovered']

        if case in latlon:
            if not confirmed == 0:
                lat = latlon[latlon.index(case) + 1]
                lon = latlon[latlon.index(case) + 2]
                population = int(pop[pop.index(case) + 1])
                percapita = (confirmed / population) * 100000

                smallSize = 10 # Plateau small countries
                bigSize = -1 / (max(percapitaList) * .01) # Plateau big countries
                radius = percapita
                # Sigmoid function to get proper circle radius
                radius = (1/(1 + smallSize * math.exp(bigSize * radius))) * 250000

                lowMortality = 1/100 # Plateau low mortality rates
                color = int((deaths / confirmed) * 100)
                # Sigmoid function to get a red RGB value
                sigmoid = int((1/(1 + lowMortality * math.exp(-1/7 * color + 6))) * 255)
                # Convert red RGB to hex
                color = '#{:02x}{:02x}{:02x}'.format(sigmoid, 0, 0)

                countries.append([lat, lon, case, confirmed, deaths, radius, color, percapita])

    for country in countries:
        popup = folium.Popup(f'{country[2]}:<br>{country[3]} cases,<br>{round(country[7], 2)} per 100k,<br>{country[4]} deaths,<br>{round(country[4]/country[3]*100, 2)}% mortality', max_width=1500)
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

@app.route('/graphs')
def graphs():
    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    covid19 = json.loads(info.text)

    return render_template('graphs.html', data=covid19)