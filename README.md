# Coronavirus Map

*Read this in: [Français](README.fr.md)*

This is a map which shows the number of cases, deaths, and mortality rate for each country. Visually, it shows this through circle sizes and the redness of them.

An up-to-date view can be found [here](https://coronavirus-map-with-circles.herokuapp.com/).

## How It Works

The python script accesses another [repository by pomber](https://github.com/pomber/covid19) to get the current number of cases and a csv file to get the latitude and longitude of each country. After that, it uses the [folium](https://python-visualization.github.io/folium/) library to map it.

![A screenshot of the Maps page](img/showcase.PNG)

The second page is the graphs page, made with [Chart.js](https://github.com/chartjs/Chart.js). This allows you to see the number of cases worldwide, or in a specific country, since January 22, 2020.

![A screenshot of the Graphs page](img/graphs.PNG)
