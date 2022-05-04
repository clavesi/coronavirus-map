import views.bubble as bubble
import views.graphs as graphs
import views.choropleth as choropleth
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


app.add_url_rule('/bubble', view_func=bubble.bubble)
app.add_url_rule('/choropleth', view_func=choropleth.choropleth)
app.add_url_rule('/graphs', view_func=graphs.graphs)


if __name__ == '__main__':
    app.run(use_reloader=True)
