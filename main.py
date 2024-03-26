#!/usr/bin/env python3
from initialize import init_nodes
from utils import parseArguments
from copy import deepcopy
from event import Event
from generateNodesGraph import generate_blockchain_graph_visualization, generate_records_of_all_nodes
import sys
import heapq
import os

def cleanup():
	for file in os.listdir('./Results/BlockChains/PDF'):
		os.remove('./Results/BlockChains/PDF/'+file)
	for file in os.listdir('./Results/BlockChains/PNG'):
		os.remove('./Results/BlockChains/PNG/'+file)
	for file in os.listdir('./Results/Records/HTML'):
		os.remove('./Results/Records/HTML/'+file)
	for file in os.listdir('./Results/Records/txt'):
		os.remove('./Results/Records/txt/'+file)

if __name__ == "__main__":
	
	# Parse here 
	inputs = parseArguments(deepcopy(sys.argv)) #this parses the command line argument into the parseArgument function which returns the arguments in the form of dictionary

	# In correct input arguments
	if inputs is None:
		sys.exit()

	# I and T_Tx are given in milliseconds
	# nodes represents number of honest nodes
	nodes = int(inputs['nodes'])

	if nodes <= 1:
		print("Node graph cannot be form using the given conditions (6 >= noOfPeers >= 3)!!!!")
		print("!!!!Exiting!!!!")
		sys.exit()

	zeta_1 = float(inputs['zeta_1'])
	zeta_2 = float(inputs['zeta_2'])

	if (zeta_1 + zeta_2) >= 1:
		print("Sum of hash powers of Adversaries is greater than equal to 1 (Not possible)!!!!")
		print("!!!!Exiting!!!!")
		sys.exit()

	T_Tx = int(inputs['T_Tx'])
	I  = int(inputs['I'])
	maxEventLoop = int(inputs['maxEventLoop'])

	# Colors to represent the advesary nodes
	colors = { 0 : "red", 1 : "orange" }

	# Initializing nodes and creating a P2P network
	nodeArray = init_nodes(nodes, zeta_1, zeta_2, I, T_Tx, colors)

	print("============= Starting Simulation =============")

	# Initializing the event queue with genesis block creation event
	eventQueue = []
	eventQueue.append(Event(0, None, None, None, ("genesis",)))

	# Using heapq module to simulate min heap (using timestamps)
	heapq.heapify(eventQueue)

	# Loop maxEventLoop times
	cnt = 0
	cancelledEventsSet = set()

	while(cnt < maxEventLoop and 0 < len(eventQueue)):
		# Getting nearest event (lowest timestamp)
		currEvent = heapq.heappop(eventQueue)

		if currEvent.eventID in cancelledEventsSet:
			cancelledEventsSet.remove(currEvent.eventID)
			continue

		# Executing the event and getting future events to be added
		futureEvents, cancelledEvents = currEvent.execute(nodeArray)
		
		for event in futureEvents:
			# Adding future events to the Event Queue
			heapq.heappush(eventQueue, event)

		# Updating cancelled events
		cancelledEventsSet.update(cancelledEvents)

		# Incrementing count
		cnt = cnt + 1

	print("============= Ending Simulation =============\n\n")
	cleanup()
	print("Storing the information in multiple files (HTML, PDF, TXT, PNG)......")

	generate_blockchain_graph_visualization(nodeArray, colors)
	generate_records_of_all_nodes(nodeArray)