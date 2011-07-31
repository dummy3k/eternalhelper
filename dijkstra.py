import sys
from pprint import pprint

class Node():
    def __init__(self, payload):
        self.cost = sys.maxint
        self.predecessor = None
        self.edges = []
        self.payload = payload

    def __repr__(self):
        return "Node(%s, $%s)" % (self.payload, self.cost)

def add_edge(cost, nodeA, nodeB):
    nodeA.edges.append((cost, nodeB))
    nodeB.edges.append((cost, nodeA))

def solve(unvisited):
    while len(unvisited):
        # find min cost node
        unvisited = sorted(unvisited, lambda x, y: cmp(x.cost, y.cost))
        current = unvisited.pop(0)
        #~ print "current: %s, unvisited: %s" % (current, unvisited)
        for item in current.edges:
            if item[1] in unvisited and item[1].cost > current.cost + item[0]:
                item[1].cost = current.cost + item[0]
                item[1].predecessor = current

def get_route(nodes, dest):
    retval = []
    current = dest
    while current:
        #~ print current
        retval.append(current)
        current = current.predecessor

    retval.reverse()
    return retval

if __name__ == '__main__':
    start = Node("start")
    alpha = Node("alpha")
    beta = Node("beta")
    delta = Node("delta")

    start.cost = 0
    add_edge(40, start, alpha)
    add_edge(20, start, beta)
    add_edge(10, alpha, beta)
    add_edge(5, alpha, delta)
    #~ add_edge(1, start, delta)
    #~ start.edges.append((1, delta))
    delta.edges.append((1, start))

    unvisited = [alpha, beta, start, delta]
    pprint(unvisited)

    solve(unvisited)

    print "start: %s" % start
    print "alpha: %s" % alpha
    print "beta: %s" % beta

    #~ current = alpha
    #~ while current:
        #~ print current
        #~ current = current.predecessor

    for item in get_route(unvisited, alpha):
        print item
