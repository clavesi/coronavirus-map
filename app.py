import views.map as map
import views.graphs as graphs
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


app.add_url_rule('/map', view_func=map.map)
app.add_url_rule('/graphs', view_func=graphs.graphs)

if __name__ == '__main__':
    app.run(use_reloader=True)
