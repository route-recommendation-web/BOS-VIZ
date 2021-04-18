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
add_block_enabled = False
destination = list(global_G.nodes())[5]
time_offset = 0
reset_offset = 0
edges_blocked = []

# Methods
def network_graph(yearRange, AccountToSearch):
    G = nx.read_gpickle("brookline.gpickle")
    for node in G.nodes:
        G.nodes[node]['pos'] = [G.nodes[node]['x'] / MAX_X, G.nodes[node]['y'] / MAX_Y]
    trace_recode = []  # contains edge_trace, node_trace, middle_node_trace
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
        trace_recode.append(trace)
        index = index + 1
    ###################################################################################################################
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 20, 'color': 'LightSkyBlue'})

    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        hover_text = "location: " + str(G.nodes[node]['x']) + "," + str(G.nodes[node]['y']) + "id :" + str(node)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hover_text])
        node_trace['text'] += tuple([text])
        index = index + 1

    trace_recode.append(node_trace)
    ###################################################################################################################
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hover_text = str(G.edges[edge]['osmid'])
        try:
            hover_text = str(G.edges[edge]['name']) + ":" + hover_text
        except:
            pass
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hover_text])
        index = index + 1

    trace_recode.append(middle_hover_trace)

    with open('traceRecode.pkl', 'wb') as f:
        pickle.dump(trace_recode, f)
    ###################################################################################################################
    figure = {
        "data": trace_recode,
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
    trace_recode = global_traceRecode.copy()
    x, y = G.nodes[destination]['pos']
    hover_text = "location: " + str(G.nodes[destination]['x']) + "," + str(G.nodes[destination]['y']) + "id: " + str(destination)
    text = "Main Base"
    trace_recode = [(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hover_text]), mode='markers+text',
                             text=tuple([text]), textposition="bottom center", hoverinfo="text",
                             marker={'size': 40, 'color': 'Green'}))] + trace_recode

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 10, 'color': 'Red'})

    for npc_nodes in npc:
        x, y = G.nodes[npc_nodes]['pos']
        hover_text = "location: " + str(G.nodes[npc_nodes]['x']) + "," + str(G.nodes[npc_nodes]['y']) + "id:" + str(npc_nodes)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hover_text])
        node_trace['text'] += tuple([text])
        index = index + 1
    trace_recode.append(node_trace)

    figure = {
        "data": trace_recode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: 0", showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure


def next_tic(n_clicks, reset):
    # This function runs whenever user clicks 'play'
    global restart_flag
    global damage
    global global_npc
    # Because the n_clicks for 'refresh data' and 'set as destination' never reset, add this offset to avoid bug
    global reset_offset
    global time_offset
    if restart_flag or (reset-reset_offset > 0):
        restart_flag = False
        damage = 0
        reset_offset = reset
        time_offset = n_clicks
        return initialize()

    G = global_G
    trace_recode = global_traceRecode.copy()
    x, y = G.nodes[destination]['pos']
    hover_text = "location: " + str(G.nodes[destination]['x']) + "," + str(G.nodes[destination]['y']) + "id:" + str(destination)
    text = "Main Base"
    trace_recode = [(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hover_text]), mode='markers+text',
                               text=tuple([text]), textposition="bottom center",
                               hoverinfo="text", marker={'size': 40, 'color': 'Green'}))] + trace_recode

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 10, 'color': 'Red'})

    index = 0
    tmp = []
    npc = global_npc
    for npc_nodes in npc:
        if npc_nodes == destination:
            damage += 1
        else:
            try:
                route = nx.shortest_path(G, npc_nodes, destination, weight="length")
                if len(route) < 2:
                    tmp.append(route[-1])
                else:
                    tmp.append(route[1])
            except:
                print("no path")

    if len(npc) == 0:
        restart_flag = True
    global_npc = tmp
    for npc_nodes in npc:
        x, y = G.nodes[node]['pos']
        hover_text = "location: " + str(G.nodes[npc_nodes]['x']) + "," + str(G.nodes[npc_nodes]['y']) + "id:" + str(npc_nodes)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hover_text])
        node_trace['text'] += tuple([text])
        index = index + 1

    trace_recode.append(node_trace)

    figure = {
        "data": trace_recode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: "+str(n_clicks-time_offset), showlegend=False,
                            hovermode='closest',
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
        dest = json.loads(new_dest)['points'][0]['hovertext'].partition('id: ')[2]
        if (dest != ''):
            destination = int(dest)
            restart_flag = True
            return u'''The destination is not reset to \n{}'''.format(new_dest)
        else:
            return u'''You can't select a street as your detination'''
    return u'''Current destination is {}'''.format(destination)


def enable_add_block(n_clicks):
    global add_block_enabled
    if (n_clicks != 0): add_block_enabled = not add_block_enabled
    return 'add-block-enable' if add_block_enabled else 'add-block-disable'

def add_block(clickData):
    # for edges in global_G.edges
    return "No street is currently blocked"