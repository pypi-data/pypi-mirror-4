import networkx as nx
from collections import defaultdict
below = defaultdict(int)

def walkup(G, n, linked):
    print u"Visiting {}".format(G.node[n]['label'])
    for u,v in G.out_edges(n):
        first_edge = G[u][v][0] # Beware: may be more than one
        if first_edge['type'] == 'has_hyperonym':
            if v in linked:
                print u"\tBlocked by {}".format(G.node[v]['label'])
                continue
            else:
                print u"\tUp {} to {}".format(G.node[u]['label'], G.node[v]['label'])
                below[v] += 1
                walkup(G, v, linked)









