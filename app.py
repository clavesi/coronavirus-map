import folium, requests, json, csv, math
from flask import Flask, render_template

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
        height="95%"
    )

    latlon = []
    with open('natlatlon.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            latlon.append(row['Country'])
            latlon.append(row['Latitude'])
            latlon.append(row['Longitude'])

    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    cases = json.loads(info.text)

    countries = []

    for case in cases:
        confirmed = cases[case][-1]['confirmed']
        deaths = cases[case][-1]['deaths']
        recovered = cases[case][-1]['recovered']

        if case in latlon:
            if not confirmed == 0:
                lat = latlon[latlon.index(case) + 1]
                lon = latlon[latlon.index(case) + 2]

                smallSize = 10 # Plateau small countries
                bigSize = -1/10000 # Plateau big countries
                radius = confirmed
                # Sigmoid function to get proper circle radius
                radius = (1/(1 + smallSize * math.exp(bigSize * radius))) * 1000000

                lowMortality = 1/50 # Plateau low mortality rates
                color = int((deaths / confirmed) * 100)
                # Sigmoid function to get a red RGB value
                sigmoid = int((1/(1 + lowMortality * math.exp(-1/10 * color + 5))) * 255)
                # Convert red RGB to hex
                color = '#{:02x}{:02x}{:02x}'.format(sigmoid, 0, 0)

                countries.append([lat, lon, case, confirmed, deaths, radius, color])

    for country in countries:
        folium.Circle(
            location=[country[0], country[1]],
            radius=country[5],
            popup=f'{country[2]}: {country[3]}, {country[4]}, {round(country[4]/country[3]*100, 3)}%',
            color=country[6],
            fill=True,
            fill_color=country[6],
            fill_opacity=.5
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
                    
                    <style>
                        * {
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }

                        nav {
                            height: 5vh;
                        }

                        .nav-links {
                            display: flex;
                            list-style: none;
                            width: 100%;
                            height: 100%;
                            background: lightcoral;
                            justify-content: space-around;
                            align-items: center;
                            flex-direction: row;
                        }

                        .nav-links li a {
                        color: white;
                        text-decoration: none;
                        font-size: 36px;
                        }
                    </style>
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