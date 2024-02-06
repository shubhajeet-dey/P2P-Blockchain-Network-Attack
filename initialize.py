#!/usr/bin/env python3
from node import Node
from utils import create_graph, connected_graph
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

	
	# Creating a connected peer graph network
	gen_graph(nodeArray)

	return nodeArray

# Generate graph and check if connected or not
def gen_graph(nodeArray):
	while(True):
		# Reinitalizing peers if not connected
		for i in range(len(nodeArray)):
			nodeArray[i].peers = dict()

		create_graph(nodeArray)

		if(connected_graph(nodeArray)):
			break



