#!/usr/bin/env python3
from collections import deque
from node import Node
import numpy as np
import random

# Initialize Nodes and assign Slow, Fast, Low CPU and High CPU features.
# PowI represents interarrival time between blocks on average
def init_nodes(N, z0, z1, PoWI):
	
	nodeArray = []

	# Node IDs range from 0 to N-1
	nodeIDs = list(range(0, N))

	# Assigning z0 percent of nodes as 'slow' and the others as 'fast' randomly.
	random.shuffle(nodeIDs)
	slowNodes = nodeIDs[:int(z0*N)]
	fastNodes = nodeIDs[int(z0*N):]

	# Assigning z1 percent of nodes as 'Low CPU' and the others as 'High CPU' randomly.
	random.shuffle(nodeIDs)
	lowCPUNodes = nodeIDs[:int(z1*N)]
	highCPUNodes = nodeIDs[int(z1*N):]

	# Calculating hash power for a low CPU node, say x then x = 1 / (len(lowCPUnodes) + 10*len(highCPUnodes))
	hashLowCPU = 1 / (len(lowCPUNodes) + (10 * len(highCPUNodes)))
	hashHighCPU = 10 * hashLowCPU

	# Initializing the Node objects
	for i in range(len(nodeIDs)):
		
		isSlow = False
		if nodeIDs[i] in slowNodes:
			isSlow = True

		isLowCPU = False
		hashPower = hashHighCPU
		if nodeIDs[i] in lowCPUNodes:
			isLowCPU = True
			hashPower = hashLowCPU

		nodeArray.append(Node(i, isSlow, isLowCPU, hashPower, PoWI))

	# Creating peer graph network and checking if it is a connected graph or not

# Generate graph and check if connected or not
def gen_graph(nodeArray):
	while(True):
		# Reinitalizing peers if not connected
		for i in range(len(nodeArray)):
			nodeArray[i].peers = dict()

		create_graph(nodeArray)

		if(connected_graph(nodeArray)):
			break

# Create graph with each node having randomly connections to 3-6 other peers
def create_graph(nodeArray):
	pass

def connected_graph(nodeArray):
	visited = [False] * len(nodeArray)

	# Performing BFS (Breadth First Search)
	queue = deque()
	queue.append(0)
	visited[0] = True

	while(not queue.empty()):
		ele = queue.popleft()

		for peer in nodeArray[ele].peers.keys()
			if visited[peer] == False:
				queue.append(peer)
				visited[peer] = True

	# Some nodes are not visited, so graph not connected
	if False in visited:
		return False
	
	# Graph is connected
	return True

