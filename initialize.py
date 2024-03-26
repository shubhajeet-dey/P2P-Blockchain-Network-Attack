#!/usr/bin/env python3
from node import Node
from attack import AttackNode
from utils import create_graph, connected_graph
from generateNodesGraph import generate_node_connectivity_graph
import random

# Initialize Nodes and assign Slow and Fast features.
# PowI represents interarrival time between blocks on average
# T_Tx represents the mean interarrival time between transactions
def init_nodes(N, zeta_1, zeta_2, PoWI, T_Tx, colors):
	
	nodeArray = []

	# Node IDs range from 0 to N-1
	nodeIDs = list(range(0, N))

	# Assigning 50 percent of nodes as 'slow' and the others as 'fast' randomly.
	z0 = 0.5
	random.shuffle(nodeIDs)
	slowNodes = nodeIDs[:int(z0*N)]
	fastNodes = nodeIDs[int(z0*N):]

	# Calculating hash power for a low CPU node, say x then x = 1 / (len(lowCPUnodes) + 10*len(highCPUnodes))
	honestHashCPU = (1 - zeta_1 - zeta_2) / N

	# Initializing the Node objects
	nodeIDs.sort()
	for nodeID in nodeIDs:
		
		isSlow = False
		if nodeID in slowNodes:
			isSlow = True

		hashPower = honestHashCPU

		nodeArray.append(Node(nodeID, isSlow, hashPower, PoWI, T_Tx))

	# Attack Node with Node ID = N, and is fast and have a hash power of zeta_1
	nodeArray.append(AttackNode(N, False, zeta_1, PoWI, T_Tx))

	# Attack Node with Node ID = N+1, and is fast and have a hash power of zeta_2
	nodeArray.append(AttackNode(N+1, False, zeta_2, PoWI, T_Tx))

	nodeIDs.extend([N,N+1])
	
	print("Creating Node graph!")

	# Creating a connected peer graph network
	gen_graph(nodeArray, colors)

	# Printing Initialization details
	print("")
	print("Node Information:")
	print("Node ID range: 0 ... " + str(N+1))
	print("Slow Honest Nodes: ", slowNodes)
	print("Fast Honest Nodes: ", fastNodes)
	print("")
	print("Hash power for Honest Nodes: " + str(honestHashCPU))
	print("")
	print("Adversary 1")
	print("nodeID:", N)
	print("Is Fast Node:", (not nodeArray[N].isSlow))
	print("Hash Power:", (nodeArray[N].hashPower))
	print("")
	print("Adversary 2")
	print("nodeID:", N+1)
	print("Is Fast Node:", (not nodeArray[N+1].isSlow))
	print("Hash Power:", (nodeArray[N+1].hashPower))
	print("")
	print("Peers Information: ")
	for nodeID in nodeIDs:
		print("Node " + str(nodeID) + " : ", list(nodeArray[nodeID].peers.keys()))
	print("")

	return nodeArray

# Generate graph and check if connected or not
def gen_graph(nodeArray, colors):
	while(True):
		# Reinitalizing peers if not connected
		for i in range(len(nodeArray)):
			nodeArray[i].peers = dict()

		create_graph(nodeArray)

		if(connected_graph(nodeArray)):
			#Since the graph of Nodes is now connected let us generate visual representation of it and save it in node_connectivity_graph.png
			generate_node_connectivity_graph(nodeArray, colors)
			break



