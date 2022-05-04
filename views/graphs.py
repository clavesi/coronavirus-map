import requests
import json
from flask import render_template


def graphs():
    """
    It takes the data from the URL, loads it into a variable, and then passes it to the template
    :return: The coviddata variable is being returned.
    """
    info = requests.get("https://pomber.github.io/covid19/timeseries.json")
    covid19 = json.loads(info.text)

    return render_template('graphs.html', coviddata=covid19)