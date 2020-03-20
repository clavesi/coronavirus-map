# https://github.com/pomber/covid19
#! Will need to make this a Flask/Django project to host online
#! https://stackabuse.com/deploying-a-flask-application-to-heroku/

import folium, requests, json, csv, math

m = folium.Map(
    location=[0, 0],
    tiles='OpenStreetMap',
    zoom_start=2
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
radiusList = []
colorList = []

for case in cases:
    confirmed = cases[case][-1]['confirmed']
    deaths = cases[case][-1]['deaths']
    recovered = cases[case][-1]['recovered']

    if case in latlon:
        if not confirmed == 0:
            lat = latlon[latlon.index(case) + 1]
            lon = latlon[latlon.index(case) + 2]
            radius = confirmed
            # 0 1 2 3 4 5 6 7 8 9 A B C D E F
            color = int((deaths / confirmed) * 100)
            # print(case, color, int((deaths / confirmed) * 100), '%')

            radiusList.append(radius)
            colorList.append(color)
            countries.append([lat, lon, case, confirmed, deaths])

# Normalize radius values
sigmoidRadii = []
for x in range(len(radiusList)):
    smallSize = 10 # Plateau small countries
    bigSize = -1/10000 # Plateau big countries

    sigmoidRadii.append((1/(1 + smallSize * math.exp(bigSize * radiusList[x]))) * 1000000)

sigmoidColors = []
# Normalize color values
for x in range(len(colorList)):
    lowMortality = 1/50
    sigmoid = int((1/(1 + lowMortality * math.exp(-1/10 * colorList[x] + 5))) * 255)
    color = '#{:02x}{:02x}{:02x}'.format(sigmoid, 0, 0)
    print(sigmoid, color)
    sigmoidColors.append(color)

for country in countries:
    folium.Circle(
        location=[country[0], country[1]],
        radius=sigmoidRadii[countries.index(country)],
        popup=f'{country[2]}: {country[3]}, {country[4]}, {round(country[4]/country[3]*100, 3)}%',
        color=sigmoidColors[countries.index(country)],
        fill=True,
        fill_color=sigmoidColors[countries.index(country)],
        fill_opacity=.5
    ).add_to(m)


m.save(outfile='index.html')