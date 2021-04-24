#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import json
import layout as lo
import utils
import styles as st
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
styles = st.styles


# ##################################callback for left side components
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
    Input('switch', 'n_clicks'),
    Input('reset', 'n_clicks'),
    Input('my-graph', 'clickData'),
    State('add-block', 'style'))
def update_output(n_clicks, new_dest, reset, clickData, style, switch):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id']
    if button_id == 'my-graph.clickData' and style == styles['add-block-enable']:
        # add block
        return utils.add_block(clickData)
    elif button_id == 'play-val.n_clicks' or button_id == 'reset.n_clicks':
        # next tic
        return utils.next_tic(n_clicks, reset)
    elif button_id == 'switch.n_clicks':
        return utils.switch_algo()
    else:
        # no update
        return dash.no_update


# ###############################callback for right side components
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


@app.callback(
    Output('add-block', 'style'),
    Input('add-block', 'n_clicks'))
def enable_add_block(n_clicks):
    return styles[utils.enable_add_block(n_clicks)]


# @app.callback(
#     Output('edges-blocked', 'children'),
#     Input('my-graph', 'clickData'))
# def add_block(clickData):
#     return utils.add_block(clickData)


if __name__ == '__main__':
    app.run_server(debug=True)
