#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
import json
import A_star
import pickle
import random
# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Boston Graph"

#initilization variables
MAX_Y = 50
MAX_X = 80
damage = 0
global_npc = []
restart_flag = False
global_G = nx.read_gpickle("brookline.gpickle")
for node in global_G.nodes:
    global_G.nodes[node]['pos'] = [global_G.nodes[node]['x'] / MAX_X, global_G.nodes[node]['y'] / MAX_Y]
destination=0
destination = list(global_G.nodes())[5]
with open('traceRecode.pkl', 'rb') as f:
    global_traceRecode = pickle.load(f)


#######################################################################################################################
#for reference purpose
def network_graph(yearRange, AccountToSearch):
    G = nx.read_gpickle("brookline.gpickle")
    for node in G.nodes:
        G.nodes[node]['pos'] = [G.nodes[node]['x'] / MAX_X, G.nodes[node]['y'] / MAX_Y]
    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    # ###################################################################################################################
    colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
    colors = ['rgb' + "(0.94, 0.75, 0.57)" for x in colors]
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = float(G.edges[edge]['length'])
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': 3},
                           marker=dict(color=colors[index]),
                           # marker={'color': 'Black'},
                           line_shape='spline',
                           opacity=0.5)
        traceRecode.append(trace)
        index = index + 1
    ###################################################################################################################
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 20, 'color': 'LightSkyBlue'})

    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        hovertext = "location: " + str(G.nodes[node]['x']) + "," + str(G.nodes[node]['y']) + "id:" + str(node)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)
    ###################################################################################################################
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hovertext = str(G.edges[edge]['osmid'])
        try:
            hovertext = str(G.edges[edge]['name']) + ":" + hovertext
        except:
            pass
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(middle_hover_trace)

    with open('traceRecode.pkl', 'wb') as f:
        pickle.dump(traceRecode, f)
    ###################################################################################################################
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Interactive Map', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    # return figure
#######################################################################################################################
def initialize():
    global global_traceRecode
    global global_npc
    global global_G
    global destination
    global_G = nx.read_gpickle("brookline.gpickle")

    for node in global_G.nodes:
        global_G.nodes[node]['pos'] = [global_G.nodes[node]['x'] / MAX_X, global_G.nodes[node]['y'] / MAX_Y]


    global_npc = random.sample(global_G.nodes(), 50)
    G = global_G
    npc = global_npc
    index = 0
    traceRecode = global_traceRecode.copy()
    x, y = G.nodes[destination]['pos']
    hovertext = "location: " + str(G.nodes[destination]['x']) + "," + str(G.nodes[destination]['y']) + "id:" + str(destination)
    text = "Main Base"
    traceRecode=[(go.Scatter(x=tuple([x]), y= tuple([y]), hovertext=tuple([hovertext]), mode='markers+text', text=tuple([text]), textposition="bottom center",
                            hoverinfo="text", marker={'size': 40, 'color': 'Green'}))] +traceRecode

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 10, 'color': 'Red'})

    for node in npc:
        x, y = G.nodes[node]['pos']
        hovertext = "location: " + str(G.nodes[node]['x']) + "," + str(G.nodes[node]['y']) + "id:" + str(node)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1
    traceRecode.append(node_trace)

    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: 0", showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure
def draw_graph(n_clicks):
    global restart_flag
    global damage
    global global_npc
    if restart_flag:
        restart_flag = False
        damage = 0
        return initialize()

    G = global_G
    traceRecode = global_traceRecode.copy()
    x, y = G.nodes[destination]['pos']
    hovertext = "location: " + str(G.nodes[destination]['x']) + "," + str(G.nodes[destination]['y']) + "id:" + str(destination)
    text = "Main Base"
    traceRecode = [(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hovertext]), mode='markers+text',
                               text=tuple([text]), textposition="bottom center",
                               hoverinfo="text", marker={'size': 40, 'color': 'Green'}))] + traceRecode

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 10, 'color': 'Red'})

    index = 0
    tmp = []
    npc = global_npc
    for node in npc:
        if node==destination:
            damage+=1
        else:
            try:
                route = nx.shortest_path(G, node, destination, weight="length")
                if len(route)<2:
                    tmp.append(route[-1])
                else:
                    tmp.append(route[1])
            except:
                print("no path")
    if len(npc)==0:
        restart_flag = True
    global_npc = tmp
    for node in npc:
        x, y = G.nodes[node]['pos']
        hovertext = "location: " + str(G.nodes[node]['x']) + "," + str(G.nodes[node]['y']) + "id:" + str(node)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)


    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: "+str(n_clicks), showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure


#######################################################################################################################
# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    #########################Title
    html.Div([html.H1("Boston Graph")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[

                    # html.Div(
                    #     className="twelve columns",
                    #     children=[
                    #         dcc.Markdown(d("""
                    #         **Account To Search**
                    #
                    #         Input the account to visualize.
                    #         """)),
                    #         dcc.Input(id="input1", type="text", placeholder="Account"),
                    #         html.Div(id="output")
                    #     ],
                    #     style={'height': '300px'}
                    # ),
                    html.Div([
                        # html.Div(dcc.Input(id='input-on-play', type='text')),
                        html.Button('play', id='play-val', n_clicks=0),
                        # html.Div(id='container-button-basic',
                        #          children='Enter a value and press play')
                    ]),
                    html.A(html.Button('Refresh Data'),href='/'),
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(1,1))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Hover Data**

                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Click Data**

                            Click on points in the graph.
                            """)),
                            html.Pre(id='click-data', style=styles['pre'])
                        ],
                        style={'height': '400px'})


                ]
            )
        ]
    )
])


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
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('play-val', 'n_clicks')])
def update_output(n_clicks):
    return draw_graph(n_clicks)
################################callback for right side components
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
