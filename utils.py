import networkx as nx
import plotly.graph_objs as go
import pickle
import random
import json
import osmnx
import math
from colour import Color
import algorithms
import A_star
import time
from PIL import Image

# Initializing variables ##############################################################################################
#######################################################################################################################
# Choose city
global_city = 'boston'
global_file_dict = dict(boston=dict(gpickle='boston_s.gpickle', tracerecode='trace_recode_boston_s.pkl'),
                        brookline=dict(gpickle='brookline.gpickle', tracerecode='trace_recode_brookline.pkl'))
global_gp_file = global_file_dict[global_city]['gpickle']
global_tracerecode_file = global_file_dict[global_city]['tracerecode']

# global_graph might subject to changes
# global_graph_const is the constant variable that use to restore blocked edges
global_graph_const = nx.read_gpickle(global_gp_file)
global_graph = global_graph_const

# Read in global trace recode
# traceRecode.pkl is generated from the "pickle file renderer' branch, check out that file for details
# global_node_trace is global npc nodes Scatter
# global_edge_trace is global blocked edges Scatter
with open(global_tracerecode_file, 'rb') as f:
    global_trace_recode = pickle.load(f)
global_node_trace = None
global_edge_trace = []

# Other variables/consts
global_damage = 0
global_destination = list(global_graph.nodes())[5]
global_reset_offset = 0
global_npc = []
global_time = 0
global_block_list = []
global_npc_step = 1
INF = math.inf
total_blocked = 0
runtime = 0
map = Image.open('map.png')

# Global state
global_restart_flag = False
global_enable_add_block = False

# Global algo
global_algorithm = 'default'


# Renderer (not used) #################################################################################################
#######################################################################################################################
def network_graph():
    graph = global_graph_const
    trace_recode = []  # contains edge_trace, node_trace, middle_node_trace

    colors = list(Color('lightcoral').range_to(Color('darkred'), len(graph.edges())))
    colors = ['rgb' + "(0.94, 0.75, 0.57)" for x in colors]
    index = 0
    for edge in graph.edges:
        x0, y0 = graph.nodes[edge[0]]['x'], graph.nodes[edge[0]]['y']
        x1, y1 = graph.nodes[edge[1]]['x'], graph.nodes[edge[0]]['y']
        # weight = float(graph.edges[edge]['length'])
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': 3},
                           marker=dict(color=colors[index]),
                           # marker={'color': 'Black'},
                           # line_shape='spline',
                           opacity=0.5)
        trace_recode.append(trace)
        index = index + 1

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 8, 'color': 'LightSkyBlue'})
    index = 0
    for graph_node in graph.nodes():
        x, y = graph.nodes[graph_node]['x'], graph.nodes[graph_node]['y']
        hover_text = "location: " + str(graph.nodes[graph_node]['x']) + "," + \
                     str(graph.nodes[graph_node]['y']) + "id :" + str(graph_node)
        text = ""
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hover_text])
        node_trace['text'] += tuple([text])
        index = index + 1
    trace_recode.append(node_trace)

    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'}, opacity=0)
    index = 0
    for edge in graph.edges:
        x0, y0 = graph.nodes[edge[0]]['x'], graph.nodes[edge[0]]['y']
        x1, y1 = graph.nodes[edge[1]]['x'], graph.nodes[edge[1]]['y']
        hover_text = str(graph.edges[edge]['osmid'])
        try:
            hover_text = str(graph.edges[edge]['name']) + ":" + hover_text
        except:
            pass
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hover_text])
        index = index + 1

    trace_recode.append(middle_hover_trace)

    with open(global_tracerecode_file, 'wb') as f:
        pickle.dump(trace_recode, f)
    # figure = {
    #     "data": trace_recode,
    #     "layout": go.Layout(title='Interactive Map', showlegend=False, hovermode='closest',
    #                         margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
    #                         xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
    #                         yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
    #                         height=600,
    #                         clickmode='event+select',
    #                         )}
    # return figure


# Methods #############################################################################################################
#######################################################################################################################
def initialize():
    global global_npc
    global global_graph
    global global_node_trace
    global global_block_list
    # Reset global_graph since it might has been changed
    global_graph = global_graph_const.copy()
    global_npc = random.sample(global_graph.nodes(), 20)
    # global_npc = global_graph[63547858]
    global_block_list = []
    # Initialize local variables
    graph = global_graph_const
    trace_recode = global_trace_recode.copy()

    # Add destination to the trace_recode
    trace_recode = draw_destination(trace_recode, graph)
    # Add npc nodes
    npc_trace = draw_npc(global_npc, graph)
    global_node_trace = npc_trace
    trace_recode.append(global_node_trace)

    # Return figure
    figure = {
        "data": trace_recode,
        # "data": [go.Scatter(x=[0, 0.5, 1, 2, 2.2], y=[1.23, 2.5, 0.42, 3, 1])],
        "layout": update_layout(global_damage, 0, 0)
    }
    return figure


def next_tic(n_clicks, reset):
    # This function runs whenever user clicks 'play'
    global global_restart_flag
    global global_damage
    global global_block_list
    global global_node_trace
    global global_edge_trace
    global global_time
    global global_npc_step
    # Because the n_clicks for 'refresh data' and 'set as destination' never reset, add this offset to avoid bug
    global global_reset_offset
    if global_restart_flag or (reset - global_reset_offset > 0) or (n_clicks == 0):
        global_restart_flag = False
        global_damage = 0
        global_time = 0
        global_reset_offset = reset
        global_edge_trace = []
        global_block_list = []
        # global_npc_step = 1
        return initialize()

    # Declare local variables
    trace_recode = global_trace_recode.copy()

    # Add destination to the trace_recode
    trace_recode = draw_destination(trace_recode, global_graph)

    # Update npc locations on global_graph
    time = update_npc()

    npc_trace = draw_npc(global_npc, global_graph)  # npc fig
    global_node_trace = npc_trace  # update global npc fig
    trace_recode += global_edge_trace  # add edge blocking trace to fig
    trace_recode.append(global_node_trace)  # add npc trace to fig

    # Update time
    global_time += time

    # Return figure
    figure = {
        "data": trace_recode,
        "layout": update_layout(global_damage, global_time, total_blocked)
    }
    return figure


def update_npc():
    global global_npc
    global global_restart_flag
    global global_damage
    global total_blocked
    global runtime

    runtime = 0

    # Local method
    def heuristic(a, b):  # using distance between nodes for heuristic
        # start_time = time.time()
        x2 = global_graph.nodes[a]['x']
        x3 = global_graph.nodes[b]['x']
        y2 = global_graph.nodes[a]['y']
        y3 = global_graph.nodes[b]['y']
        return osmnx.distance.euclidean_dist_vec(y2, x2, y3, x3)

    for i in range(1):
        # Update npc locations
        npc_updated = []
        for npc_nodes in global_npc:
            if npc_nodes == global_destination:
                global_damage += 1
            else:
                try:
                    # route = nx.shortest_path(graph, npc_nodes, destination, weight="length")
                    if global_algorithm == 'default':
                        # route = nx.astar_path(global_graph, npc_nodes, global_destination, heuristic=heuristic,
                        #                       weight="length")
                        tic = time.perf_counter()
                        route = algorithms.a_star(global_graph, npc_nodes, global_destination, heuristic=None,
                                                  weight="length")
                        toc = time.perf_counter()
                        runtime = runtime + (toc - tic)

                    else:
                        # Change algorithm here
                        # route = nx.astar_path(global_graph, npc_nodes, global_destination, heuristic=heuristic,
                        #                       weight="length")
                        tic = time.perf_counter()
                        route = algorithms.a_star(global_graph, npc_nodes, global_destination, heuristic=heuristic,
                                                  weight="length")
                        toc = time.perf_counter()
                        runtime = runtime + (toc - tic)
                    if len(route) <= global_npc_step + 1:
                        npc_updated.append(route[-1])
                    else:
                        npc_updated.append(route[global_npc_step + 1])
                except:
                    print("no path")
                    total_blocked = total_blocked + 1
        global_npc = npc_updated
        print(f"Ran in {runtime:0.4f} seconds")
        if len(global_npc) == 0:
            global_restart_flag = True
            return i
    return global_npc_step


def update_destination(new_dest):
    global global_destination
    global global_restart_flag
    try:
        dest = json.loads(new_dest)['points'][0]['hovertext'].partition(';nodeid:')[2]
        if dest != '':
            global_destination = int(dest)
            global_restart_flag = True
            show_dest = u'''The destination is now reset to \n{}'''.format(global_destination)
        else:
            show_dest = u'''You can't select a street as your detination'''
    except:
        show_dest = u'''Current destination is {}'''.format(global_destination)
    return show_dest


def enable_add_block(n_clicks):
    global global_enable_add_block
    if n_clicks != 0:
        global_enable_add_block = not global_enable_add_block
    return 'add-block-enable' if global_enable_add_block else 'add-block-disable'


def add_block(clickData):
    global global_block_list
    global global_graph
    global global_edge_trace

    trace_recode = global_trace_recode.copy()
    edge_trace = global_edge_trace
    graph = global_graph

    # Add destination to the trace_recode
    trace_recode = draw_destination(trace_recode, graph)

    if global_enable_add_block and clickData is not None:
        click_data = clickData['points'][0]['hovertext']
        if ';startnode:' in click_data:
            start_end = click_data.partition(';startnode:')[2].partition(';endnode:')
            edge = (int(start_end[0]), int(start_end[2]), 0)
            # try:
            #      edge_idx = global_block_list.index(edge)
            #      global_block_list.pop(edge_idx)
            #      edge_trace.pop(edge_idx)
            #      graph.edges[edge]['length'] = global_graph_const.edges[edge]['length']
            if edge not in global_block_list:
                global_block_list.append(edge)  # could be replaced with hash table to improve performance
                add_block_item(edge_trace, edge)
                # graph.edges[edge]['length'] = INF
                try:
                    graph.remove_edge(edge[0], edge[1])
                    graph.remove_edge(edge[1], edge[0])
                except:
                    pass

    global_graph = graph
    global_edge_trace = edge_trace
    trace_recode = trace_recode + edge_trace
    trace_recode.append(global_node_trace)
    figure = {
        "data": trace_recode,
        "layout": update_layout(global_damage, global_time, total_blocked)
    }
    return figure


def add_block_item(edge_trace, edge):
    graph = global_graph_const
    x0, y0 = graph.nodes[edge[0]]['x'], graph.nodes[edge[0]]['y']
    x1, y1 = graph.nodes[edge[1]]['x'], graph.nodes[edge[1]]['y']
    weight = float(graph.edges[edge]['length'])
    trace = go.Scatter(x=tuple([x0, x1, None]),
                       y=tuple([y0, y1, None]),
                       mode='lines',
                       line={'width': 3},
                       # marker=dict(color=colors[index]),
                       marker={'color': 'Red'},
                       line_shape='spline',
                       opacity=0.5)
    edge_trace.append(trace)


def draw_destination(trace_recode, graph):
    x, y = graph.nodes[global_destination]['x'], graph.nodes[global_destination]['y']
    hover_text = "Destination" + " id: " + str(global_destination)
    text = "Main Base"
    trace_recode.append(go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hover_text]), mode='markers+text',
                                   text=tuple([text]), textposition="bottom center", hoverinfo="text", opacity=0.75,
                                   marker={'size': 30, 'color': 'Green'}))
    return trace_recode


def draw_npc(npc, graph):
    npc_trace = go.Scatter(x=[], y=[], name="npc", hovertext=[], text=[], mode='markers+text',
                           textposition="bottom center", hoverinfo="text", marker={'size': 10, 'color': 'Red'})
    for npc_nodes in npc:
        x, y = graph.nodes[npc_nodes]['x'], graph.nodes[npc_nodes]['y']
        hover_text = "npc id:" + str(npc_nodes)
        text = ""
        npc_trace['x'] += tuple([x])
        npc_trace['y'] += tuple([y])
        npc_trace['hovertext'] += tuple([hover_text])
        npc_trace['text'] += tuple([text])

    return npc_trace


def update_layout(damage, time, blocked):
    layout = go.Layout(
        title='Total Damage: ' + str(damage) + ' Time: ' + str(time) + ' Blocked NPCs: ' + str(blocked) +
              '\nLast Runtime: ' + str(runtime)[:6] + 's',
        showlegend=False,
        hovermode='closest',
        margin={'b': 40, 'l': 40, 'r': 40, 't': 80},
        xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
        yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False, 'scaleanchor': 'x', 'scaleratio': 1.15},
        height= 820,
        # width=850,
        clickmode='event+select',
        images=[{'layer': 'below',
                 'opacity': 1,
                 'sizex': 0.2395,  # increase value to extend img on x axis
                 'sizey': 0.1638,  # increase value to extend img on y axis
                 'sizing': 'stretch',
                 'source': map,
                 'x': -71.20131,  # decrease value to move left
                 'xref': 'x',
                 'y': 42.41345,  # decrease value to move down
                 'yref': 'y'}]
    )
    return layout


def switch_algorithm():
    global global_algorithm
    global_algorithm = 'a_star' if global_algorithm == 'default' else 'default'
    return u'''Current Algorithm: {}\nNPC step: {}'''.format(global_algorithm, global_npc_step)


def change_npc_step(selected_step):
    global global_npc_step
    global_npc_step = selected_step
    return u'''Current Algorithm: {}\nNPC step: {}'''.format(global_algorithm, global_npc_step)
