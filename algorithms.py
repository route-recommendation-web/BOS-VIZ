from heapq import heappush, heappop
from sys import stdin, stdout
from heapdict import heapdict
import networkx as nx
import A_star
import time

from networkx.algorithms.shortest_paths.weighted import _weight_function

INF = ((1 << 63) - 1) // 2


# Dijktra's shortest path algorithm. Prints the path from source to target.


# def dijkstra(adj, source, target):
#     INF = ((1 << 63) - 1) // 2
#     pred = {x: x for x in adj}
#     dist = {x: INF for x in adj}
#     dist[source] = 0
#     PQ = []
#     heapq.heappush(PQ, [dist[source], source])
#
#     while (PQ):
#         u = heapq.heappop(PQ)  # u is a tuple [u_dist, u_id]
#         u_dist = u[0]
#         u_id = u[1]
#         if u_dist == dist[u_id]:
#             # if u_id == target:
#             #    break
#             for v in adj[u_id]:
#                 v_id = v[0]
#                 w_uv = v[1]
#                 if dist[u_id] + w_uv < dist[v_id]:
#                     dist[v_id] = dist[u_id] + w_uv
#                     heapq.heappush(PQ, [dist[v_id], v_id])
#                     pred[v_id] = u_id
#
#     if dist[target] == INF:
#         stdout.write("There is no path between ", source, "and", target)
#     else:
#         st = []
#         node = target
#         while (True):
#             st.append(str(node))
#             if (node == pred[node]):
#                 break
#             node = pred[node]
#         path = st[::-1]
#         stdout.write("The shortest path is: " + " ".join(path) + "\n\n")
#         stdout.write("The distance from 'a' to 'i' is: " + str(dist['i']) + "\n\n")
#         stdout.write("distance dictionary: " + str(dist) + "\n\n")
#         stdout.write("predecessor dictionary: " + str(pred))
#
#
# # ----------------------------------------------------------

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


def main():
    # adj = {'c': [('b', 0.32), ('e', 0.17), ('f', 0.91)],
    #        'g': [('d', 0.17), ('e', 0.27), ('h', 0.92)],
    #        'i': [('e', 1.98), ('f', 0.13), ('h', 0.22)],
    #        'f': [('c', 0.91), ('e', 0.33), ('i', 0.13)],
    #        'h': [('e', 0.18), ('g', 0.92), ('i', 0.22)],
    #        'd': [('a', 0.72), ('e', 0.29), ('g', 0.17)],
    #        'a': [('b', 0.95), ('d', 0.72), ('e', 1.75)],
    #        'e': [('a', 1.75), ('b', 0.82), ('c', 0.17), ('d', 0.29), ('f', 0.33), ('g', 0.27), ('h', 0.18),
    #              ('i', 1.98)],
    #        'b': [('a', 0.95), ('c', 0.32), ('e', 0.82)]}
    # G = nx.path_graph(5)
    G = nx.grid_graph(dim=[3, 3])
    nx.set_edge_attributes(G, {e: e[1][0] * 2 for e in G.edges()}, "cost")
    start_time = time.time()
    path = a_star(G, (0, 0), (2, 2), heuristic=None, weight="cost")
    print("--- %s seconds ---" % (time.time() - start_time))
    print(path)


# ----------------------------------------------------------

if __name__ == "__main__":
    main()
