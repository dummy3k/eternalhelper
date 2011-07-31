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

start = Node("start")
alpha = Node("alpha")
beta = Node("beta")

start.cost = 0
add_edge(4, start, alpha)
add_edge(2, start, beta)
add_edge(1, alpha, beta)

unvisited = [alpha, beta, start]

print "Start"
pprint(unvisited)

while len(unvisited):
    # find min cost node
    unvisited = sorted(unvisited, lambda x, y: cmp(x.cost, y.cost))
    current = unvisited.pop(0)
    print "current: %s, unvisited: %s" % (current, unvisited)
    for item in current.edges:
        if item[1] in unvisited and item[1].cost > current.cost + item[0]:
            item[1].cost = current.cost + item[0]
            item[1].predecessor = current

print "start: %s" % start
print "alpha: %s" % alpha
print "beta: %s" % beta

current = alpha
while current:
    print current
    current = current.predecessor
