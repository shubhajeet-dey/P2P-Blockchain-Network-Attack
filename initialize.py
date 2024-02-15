#!/usr/bin/env python3
from node import Node
from utils import create_graph, connected_graph
import random
from generateNodesGraph import generate_node_connectivity_graph

# Initialize Nodes and assign Slow, Fast, Low CPU and High CPU features.
# PowI represents interarrival time between blocks on average
# T_Tx represents the mean interarrival time between transactions
def init_nodes(N, z0, z1, PoWI, T_Tx):
	
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
	nodeIDs.sort()
	for nodeID in nodeIDs:
		
		isSlow = False
		if nodeID in slowNodes:
			isSlow = True

		isLowCPU = False
		hashPower = hashHighCPU
		if nodeID in lowCPUNodes:
			isLowCPU = True
			hashPower = hashLowCPU

		nodeArray.append(Node(nodeID, isSlow, isLowCPU, hashPower, PoWI, T_Tx))

	
	print("Creating Node graph!")

	# Creating a connected peer graph network
	gen_graph(nodeArray)

	# Printing Initialization details
	print("")
	print("Node Information:")
	print("Node ID range: 0 ... " + str(N-1))
	print("Slow Nodes: ", slowNodes)
	print("Fast Nodes: ", fastNodes)
	print("")
	print("Low CPU Nodes: ", lowCPUNodes)
	print("High CPU Nodes: ", highCPUNodes)
	print("")
	print("Hash power for Low CPU Nodes: " + str(hashLowCPU))
	print("Hash power for High CPU Nodes: " + str(hashHighCPU))
	print("")
	print("Peers Information: ")
	for nodeID in nodeIDs:
		print("Node " + str(nodeID) + " : ", list(nodeArray[nodeID].peers.keys()))
	print("")

	return nodeArray

# Generate graph and check if connected or not
def gen_graph(nodeArray):
	while(True):
		# Reinitalizing peers if not connected
		for i in range(len(nodeArray)):
			nodeArray[i].peers = dict()

		create_graph(nodeArray)

		if(connected_graph(nodeArray)):
			#Since the graph of Nodes is now connected let us generate visual representation of it and save it in node_connectivity_graph.png
			generate_node_connectivity_graph(nodeArray)
			break



