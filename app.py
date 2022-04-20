import views.map as map
import views.graphs as graphs
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


app.add_url_rule('/map', view_func=map.map)
app.add_url_rule('/graphs', view_func=graphs.graphs)

if __name__ == '__main__':
    app.run(use_reloader=True)
