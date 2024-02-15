#!/usr/bin/env python3
from initialize import init_nodes
from utils import parseArguments
from copy import deepcopy
from event import Event
import sys
import heapq

if __name__ == "__main__":
	
	# Parse here 
	inputs = parseArguments(deepcopy(sys.argv)) #this parses the command line argument into the parseArgument function which returns the arguments in the form of dictionary

	# In correct input arguments
	if inputs is None:
		sys.exit()

	# I and T_Tx are given in milliseconds
	nodes = int(inputs['nodes'])
	z0 = float(inputs['z0'])
	z1 = float(inputs['z1'])
	T_Tx = int(inputs['T_Tx'])
	I  = int(inputs['I'])
	maxEventLoop = int(inputs['maxEventLoop'])

	# Initializing nodes and creating a P2P network
	nodeArray = init_nodes(nodes, z0, z1, I, T_Tx)

	print("============= Starting Simulation =============")

	# Initializing the event queue with genesis block creation event
	eventQueue = []
	eventQueue.append(Event(0, None, None, None, ("genesis",)))

	# Using heapq module to simulate min heap (using timestamps)
	heapq.heapify(eventQueue)

	# Loop maxEventLoop times
	cnt = 0
	while(cnt < maxEventLoop and 0 < len(eventQueue)):
		# Getting nearest event (lowest timestamp)
		currEvent = heapq.heappop(eventQueue)

		# Executing the event and getting future events to be added
		futureEvents = currEvent.execute(nodeArray)
		
		for event in futureEvents:
			# Adding future events to the Event Queue
			heapq.heappush(eventQueue, event)	

		# Incrementing count
		cnt = cnt + 1
