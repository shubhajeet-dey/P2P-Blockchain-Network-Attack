#!/usr/bin/env python3
from collections import deque
from numpy.random import uniform
import random

# Parsing the command line arguments
def parseArguments(inputs):

    if len(inputs) != 7:
        print("Usage : python3 main.py nodes zeta_1 zeta_2 T_Tx I maxEventLoop\n")
        return None
    else:
        required_input = {
            'nodes'             : inputs[1],
            'T_Tx'              : inputs[4],
            'I'                 : inputs[5],
            'zeta_1'            : inputs[2],
            'zeta_2'            : inputs[3],
        	'maxEventLoop'      : inputs[6],
        }
        return required_input

# Assign Edge between node i and node j
def assign_edge(nodeArray, i, j):

	# Setting propagation delay from a uniform distribution between 10ms and 500ms
	propagation_delay = uniform(10, 500)

	# Setting link speed for this edge in bits/millisecond = 1000 bits/second
	# If one of them is slow, link speed = 5 Mbps = 5*10^6 bps = 5000 bits/millisecond
	if nodeArray[i].isSlow or nodeArray[j].isSlow:
		link_speed = 5000
	else:
	# If both are fast, link speed = 100 Mbps = 10^8 bps = 10^5 bits/millisecond
		link_speed = 100000

	# Adding each other as peers
	nodeArray[i].peers[j] = [ nodeArray[j], propagation_delay, link_speed ]
	nodeArray[j].peers[i] = [ nodeArray[i], propagation_delay, link_speed ]

# Create graph with each node having randomly connections to 3-6 other peers
def create_graph(nodeArray):
	nodePeers = [[i, 0] for i in range(len(nodeArray))]
	random.shuffle(nodePeers)
	
	while(True):
		# Every node has more than 3 peers
		if nodePeers[0][1] >= 3:
			break

		# Maximum number of peers that can be added to the 1st element in the list
		max_remaining_peers = 6 - nodePeers[0][1]

		# Now, randomly select the number of peers to be added
		addPeers = random.randint(1, max_remaining_peers)
		
		i = 1
		# Random Shuffle introduces randomness, even when looping sequentially
		while(i < len(nodePeers) and addPeers > 0):

			# If node is already a peer of the first node, continue
			if nodePeers[i][0] in nodeArray[nodePeers[0][0]].peers:
				i += 1
				continue

			# If this node has less than 6 peers then add
			if(nodePeers[i][1] < 6):
				nodePeers[i][1] = nodePeers[i][1] + 1
				nodePeers[0][1] = nodePeers[0][1] + 1
				assign_edge(nodeArray, nodePeers[0][0], nodePeers[i][0])
				addPeers -= 1
			else:
			# If equal to 6, then next following nodes will also have 6 peers (as sorted) 
				break

			i += 1

		
		# Sort nodes based on number of peers, random shuffle to ensure randomness
		random.shuffle(nodePeers)
		nodePeers.sort(key=lambda node: node[1])

# Checking if generated graph is connected
def connected_graph(nodeArray):
	visited = [False] * len(nodeArray)

	print("Checking if Graph is connected..")
	# Performing BFS (Breadth First Search)
	queue = deque()
	queue.append(0)
	visited[0] = True

	while(queue):
		ele = queue.popleft()
		for peer in nodeArray[ele].peers.keys():
			if visited[peer] == False:
				queue.append(peer)
				visited[peer] = True

	# Some nodes are not visited, so graph not connected
	if False in visited:
		return False
	
	print("Graph is connected!!")
	# Graph is connected
	return True