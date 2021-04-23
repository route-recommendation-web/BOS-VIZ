# route-recommendation-web

##### Pickle file renderer:
The main branch uses traceRecode.pkl to graph the map. Yet the map data is stored in boston.gpickle, it would be too inefficient if we read that everytime.
Therefore, we built this branch to render a traceRecode.pkl file to accelerate the computation effiecency.

##### Run:
Import the file to the PyCharm. Install dependencies in settings (preferences for MacOS). Hit the run button on the top-right.
Alternative way is to type the following in project root directory.
```console
python app.py
```
After the run completed, replace the traceRecode.pkl file in your main branch with the one you just rendered.

##### References:
https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7
https://github.com/gboeing/osmnx
https://github.com/networkx/networkx
