# Coronavirus Map
*Read this in: [Français](README.fr.md)*

This is a map which shows the number of cases, deaths, and mortality rate for each country. Visually, it shows this through circle sizes and the redness of them.

An up-to-date view can be found [here](https://coronavirus-map-with-circles.herokuapp.com/).

## How It Works
The python script accesses another [repository by pomber](https://github.com/pomber/covid19) to get the current number of cases and a csv file to get the latitutde and longitude of each country. After that, it uses the [folium](https://python-visualization.github.io/folium/) library to map it all.

![](img/showcase.png)