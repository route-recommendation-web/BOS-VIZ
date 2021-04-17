#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import json
import layout as lo
import utils
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
# import pandas as pd
# from datetime import datetime
# import A_star
# import pickle
# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Boston Graph"
app.layout = lo.layout

###################################callback for left side components
# @app.callback(
#     dash.dependencies.Output('my-graph', 'figure'),
#     [dash.dependencies.Input('my-range-slider', 'value'), dash.dependencies.Input('input1', 'value')])
# def update_output(value, input1):
#     YEAR = value
#     ACCOUNT = input1
#     return draw_graph(value, input1)
#     # to update the global variable of YEAR and ACCOUNT
#
@app.callback(
    Output('my-graph', 'figure'),
    Input('play-val', 'n_clicks'),
    Input('show-dest', 'children'),
    Input('reset', 'n_clicks'))
def update_output(n_clicks, new_dest, reset):
    return utils.draw_graph(n_clicks, reset)
################################callback for right side components
@app.callback(
    Output('hover-data', 'children'),
    Input('my-graph', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)
@app.callback(
    Output('click-data', 'children'),
    Input('my-graph', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)
@app.callback(
    Output('show-dest', 'children'),
    Input('set-dest', 'n_clicks'),
    State('click-data', 'children'))
def set_destination(n_clicks, new_dest):
    return utils.update_destination(new_dest)

if __name__ == '__main__':
    app.run_server(debug=True)
