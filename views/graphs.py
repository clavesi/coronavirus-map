import requests
import json
from flask import render_template

def graphs():
    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    covid19 = json.loads(info.text)

    return render_template('graphs.html', coviddata=covid19)
