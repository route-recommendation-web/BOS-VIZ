from heapq import heappush, heappop
from sys import stdin, stdout
from heapdict import heapdict
import networkx as nx
import A_star
import time
import osmnx

from networkx.algorithms.shortest_paths.weighted import _weight_function

INF = ((1 << 63) - 1) // 2


def a_star(G, source, target, heuristic="None", weight="weight"):
    hd = heapdict()
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
        def heuristic(u, v):
            return 0

    weight = _weight_function(G, weight)

    for node in G.nodes:
        hd[node] = [INF, INF, (None, None)]

    hd[source] = [0, 0, (None, None)]
    explored = {}
    enqueued = {}
    while len(hd) != 0:
        temp = hd.popitem()
        curnode = temp[0]
        priority = temp[1][0]
        cost = temp[1][1]
        parent = temp[1][2]
        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
                if node == source:
                    path.append(node)
                    path.reverse()
                    return path

        if curnode in explored:
            if explored[curnode] is None:
                continue
            qcost, h = enqueued[curnode]
            if qcost < cost:
                continue

        explored[curnode] = parent

        for neighbor, w in G[curnode].items():
            if neighbor == target and source == curnode:
                return [curnode, target]
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
            else:
                h = heuristic(neighbor, target)
            edge_cost = weight(curnode, neighbor, w)
            if neighbor not in explored:
                priority, neighbor_cost, parent = hd[neighbor]
                if neighbor_cost > cost + edge_cost:
                    hd[neighbor] = [cost + edge_cost + h, cost + edge_cost, curnode]

            enqueued[neighbor] = cost + edge_cost, h

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
