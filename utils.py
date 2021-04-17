import networkx as nx
import plotly.graph_objs as go
import pickle
import random
import json
from colour import Color

# Initializing variables
MAX_X = 80
MAX_Y = 50

global_G = nx.read_gpickle("brookline.gpickle")
for node in global_G.nodes:
    global_G.nodes[node]['pos'] = [global_G.nodes[node]['x'] / MAX_X, global_G.nodes[node]['y'] / MAX_Y]

with open('traceRecode.pkl', 'rb') as f:
    global_traceRecode = pickle.load(f)

damage = 0
global_npc = []
restart_flag = False
destination = list(global_G.nodes())[5]
time_offset = 0
reset_offset = 0

# Methods
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
    traceRecode=[(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hovertext]), mode='markers+text',
                             text=tuple([text]), textposition="bottom center", hoverinfo="text",
                             marker={'size': 40, 'color': 'Green'}))] + traceRecode

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
def draw_graph(n_clicks, reset):
    global restart_flag
    global damage
    global global_npc
    global reset_offset
    global time_offset
    if restart_flag or (reset-reset_offset > 0):
        restart_flag = False
        damage = 0
        reset_offset = reset
        time_offset = n_clicks
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
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: "+str(n_clicks-time_offset), showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure

def update_destination(new_dest):
    global destination
    global restart_flag
    if new_dest is not None:
        dest = json.loads(new_dest)['points'][0]['hovertext'].partition('id:')[2]
        if (dest != ''):
            destination = int(dest)
            restart_flag = True
            return u'''The destination is not reset to \n{}'''.format(new_dest)
        else:
            return u'''You can't select a street as your detination'''
    return u'''Current destination is {}'''.format(destination)
