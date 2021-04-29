# route-recommendation-web
This code has been tested on MacOS, Python 3.7-3.9, please follow readme to setup a virtual conda environment for faster deployment.

#####
- Install conda by following the guide https://conda.io/projects/conda/en/latest/user-guide/install/index.html

- Setup Environment
```
conda create -n bpv python=3.9
source activate bpv
pip install dash
pip install networkx
pip install osmnx
pip install colour
pip install heapdict
```
- run the app
```
python app.py
```
- Dash is running on http://127.0.0.1:8050/ 

##### Link to our project report:

##### References:
https://github.com/gboeing/osmnx
https://github.com/networkx/networkx
https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7
