import networkx as nx
import plotly.graph_objs as go
import pickle
import random
import json
from colour import Color
import math
# Initializing variables
MAX_X = 80
MAX_Y = 50

# global_G might subject to changes
# global_G is the constant variable that use to restore blocked edges
global_G = nx.read_gpickle("brookline.gpickle")
global_G_const = nx.read_gpickle("brookline.gpickle")
for node in global_G_const.nodes:
    global_G_const.nodes[node]['pos'] = [global_G_const.nodes[node]['x'] / MAX_X, global_G_const.nodes[node]['y'] / MAX_Y]
    global_G.nodes[node]['pos'] = [global_G_const.nodes[node]['x'] / MAX_X, global_G_const.nodes[node]['y'] / MAX_Y]

# Read in global trace recode
# traceRecode.pkl is generated from the "pickle file renderer' branch, check out that file for details
# global_node_trace is global npc nodes Scatter
# global_edge_trace is global blocked edges Scatter
with open('traceRecode.pkl', 'rb') as f:
    global_trace_recode = pickle.load(f)
global_node_trace = None
global_edge_trace = []

# Other variables/consts
damage = 0
destination = list(global_G.nodes())[5]
time_offset = 0
reset_offset = 0
global_npc = []
global_time = 0
edges_blocked = []
INF = math.inf

# Global state
restart_flag = False
add_block_enabled = False

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
    global global_npc
    global global_G
    global global_node_trace

    # Initialize local variables
    global_G = nx.read_gpickle("brookline.gpickle")
    for node in global_G_const.nodes:
        global_G_const.nodes[node]['pos'] = [global_G_const.nodes[node]['x'] / MAX_X,
                                             global_G_const.nodes[node]['y'] / MAX_Y]
        global_G.nodes[node]['pos'] = [global_G_const.nodes[node]['x'] / MAX_X, global_G_const.nodes[node]['y'] / MAX_Y]
    global_npc = random.sample(global_G.nodes(), 50)
    G = global_G_const
    npc = global_npc
    index = 0
    trace_recode = global_trace_recode.copy()

    # Add destination to the trace_recode
    trace_recode = set_destination(trace_recode, G)

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
    global_node_trace = node_trace
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
    global edges_blocked
    global global_node_trace
    global global_edge_trace
    global global_time
    # Because the n_clicks for 'refresh data' and 'set as destination' never reset, add this offset to avoid bug
    global reset_offset
    global time_offset
    if restart_flag or (reset-reset_offset > 0):
        restart_flag = False
        damage = 0
        reset_offset = reset
        time_offset = n_clicks
        global_edge_trace = []
        edges_blocked = []
        return initialize()

    G = global_G
    trace_recode = global_trace_recode.copy()
    edge_trace = global_edge_trace.copy()

    # Add destination to the trace_recode
    trace_recode = set_destination(trace_recode, G)

    index = 0
    tmp = []
    npc = global_npc
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 10, 'color': 'Red'})
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
        x, y = G.nodes[npc_nodes]['pos']
        hover_text = "location: " + str(G.nodes[npc_nodes]['x']) + "," + str(G.nodes[npc_nodes]['y']) + "id:" + str(npc_nodes)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hover_text])
        node_trace['text'] += tuple([text])
        index = index + 1

    global_node_trace = node_trace
    trace_recode += edge_trace
    trace_recode.append(global_node_trace)
    global_time = n_clicks-time_offset
    figure = {
        "data": trace_recode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: "+str(global_time), showlegend=False,
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
        dest = json.loads(new_dest)['points'][0]['hovertext'].partition(';nodeid:')[2]
        if dest != '':
            destination = int(dest)
            restart_flag = True
            return u'''The destination is not reset to \n{}'''.format(destination)
        else:
            return u'''You can't select a street as your detination'''
    return u'''Current destination is {}'''.format(destination)


def enable_add_block(n_clicks):
    global add_block_enabled
    if (n_clicks != 0): add_block_enabled = not add_block_enabled
    return 'add-block-enable' if add_block_enabled else 'add-block-disable'


def add_block(clickData):
    global edges_blocked
    global global_G
    global global_edge_trace

    trace_recode = global_trace_recode.copy()
    edge_trace = global_edge_trace
    G = global_G
    # Add destination to the trace_recode
    trace_recode = set_destination(trace_recode, G)
    if add_block_enabled and clickData is not None:
        click_data = clickData['points'][0]['hovertext']
        if ';startnode:' in click_data:
            start_end = click_data.partition(';startnode:')[2].partition(';endnode:')
            edge = (int(start_end[0]), int(start_end[2]), 0)
            try:
                edge_idx = edges_blocked.index(edge)
                edges_blocked.pop(edge_idx)
                edge_trace.pop(edge_idx)
                G.edges[edge]['length'] = global_G_const.edges[edge]['length']
            except:
                edges_blocked.append(edge)  # could be replaced with hash table to improve performance
                add_block_item(edge_trace, edge)
                # G.edges[edge]['length'] = INF
                try:
                    G.remove_edge(edge[0],edge[1])
                    G.remove_edge(edge[1], edge[0])
                except:
                    pass


        # Show blocked edges (debug use, delete it in the PROD environment)
        # merge the edges_blocked with edge_trace to improve performance
        # if edges_blocked is not []:
        #     for edge in edges_blocked:
        #         x0, y0 = G.nodes[edge[0]]['pos']
        #         x1, y1 = G.nodes[edge[1]]['pos']
        #         weight = float(G.edges[edge]['length'])
        #         trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
        #                            mode='lines',
        #                            line={'width': 3},
        #                            # marker=dict(color=colors[index]),
        #                            marker={'color': 'Red'},
        #                            line_shape='spline',
        #                            opacity=0.5)
        #         edge_trace.append(trace)
    global_G = G
    global_edge_trace = edge_trace
    trace_recode = trace_recode + edge_trace
    trace_recode.append(global_node_trace)
    figure = {
        "data": trace_recode,
        "layout": go.Layout(title='Total Damage: ' + str(damage)+" Time: "+str(global_time), showlegend=False,
                            hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure


def add_block_item(edge_trace, edge):
    G = global_G_const
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    weight = float(G.edges[edge]['length'])
    trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                       mode='lines',
                       line={'width': 3},
                       # marker=dict(color=colors[index]),
                       marker={'color': 'Red'},
                       line_shape='spline',
                       opacity=0.5)
    edge_trace.append(trace)


def set_destination(trace_recode, G):
    x, y = G.nodes[destination]['pos']
    hover_text = "location: " + str(G.nodes[destination]['x']) + "," + str(G.nodes[destination]['y']) + "id: " + str(
        destination)
    text = "Main Base"
    trace_recode = [(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hover_text]), mode='markers+text',
                                text=tuple([text]), textposition="bottom center", hoverinfo="text",
                                marker={'size': 40, 'color': 'Green'}))] + trace_recode
    return trace_recode
