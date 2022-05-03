import requests
import json
from flask import render_template
import folium
import pandas as pd


def choropleth():
    m = folium.Map(location=[40, -95], zoom_start=4)

    url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
    state_geo = f"{url}/us-states.json"
    state_unemployment = f"{url}/US_Unemployment_Oct2012.csv"
    state_data = pd.read_csv(state_unemployment)

    folium.Choropleth(
        geo_data=state_geo,
        name="choropleth",
        data=state_data,
        columns=["State", "Unemployment"],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=.1,
        legend_name="Unemployment Rate (%)",
    ).add_to(m)

    m.save(outfile='templates/choropleth.html')
    return render_template('choropleth.html')
