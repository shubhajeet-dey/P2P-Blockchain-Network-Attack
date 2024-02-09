#!/usr/bin/env python3
from block import Block
from transactions import TXN
import numpy as np
import random

# Class for Node
class Node:
	'''
	NodeID: Unique Identifier for each Node
	isSlow: Boolean value stating if the node is slow or fast
	isLowCPU: Boolean value stating if the node has low or high CPU
	hashPower: Node's fraction of the total hashing power.
	PoWI: The interarrival time between blocks on average
	T_Tx: The mean interarrival time between transactions
	status: Status of miner, possible status: {"free", "mining"}
	blocksSeen: Dictionary of blocks present in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): { "arrival_time": ~ , "Block": Block Object }, ... }
	leafBlocks: Dictionary of blocks which are leaf nodes in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): Block Object, ...}
	peers: Contains information about the peers of the nodes, Structure = { Peer's NodeID : [ Peer's Node Object, propagation delay (rho_ij), link speed (c_ij) ], ... }
	heardTXNs: Dictionary of all the Transactions which are heard by this node, Structure = { TXNID : TXN Object, ... }

	'''
	def __init__(self, nodeID, isSlow, isLowCPU, hashPower, PoWI, T_Tx):

		self.nodeID = nodeID
		self.isSlow = isSlow
		self.isLowCPU = isLowCPU
		self.hashPower = hashPower
		self.PoWI = PoWI
		self.T_Tx = T_Tx
		self.status = "free"
		self.blocksSeen = dict()
		self.leafBlocks = dict()
		self.peers = dict()
		self.heardTXNs = dict()

	# Calculating latency for transmitting a message to a connected peer
	def calculate_latency(self, numberOfKBs, peerNodeID):

		# Message Size in bits
		messageSize = numberOfKBs * 8000

		# Calculating various delays
		propagation_delay = self.peers[peerNodeID][1]
		link_speed = self.peers[peerNodeID][2]

		# 96kbits = 96000
		queueing_delay = np.random.exponential(scale=(96000 / link_speed))

		# Total Latency
		total_latency = propagation_delay + (messageSize / link_speed) + queueing_delay
		return total_latency

	def next_create_transaction_delay(self):
		return np.random.exponential(scale=self.T_Tx)

	# Create a random transaction with random amount
	def create_transaction(self, nodeArray, timestamp):
		# Choosing a random peer (can choose itself also, which is ok)
		toNode = random.choice(nodeArray)

		# Random amount from 1 to 10 coins
		amount = random.randint(1, 10)

		# Creating the TXN object
		txn = TXN(timestamp, self.nodeID, toNode.nodeID, amount, False)

		# Adding in seen transactions
		self.heardTXNs[txn.TXNID] = txn

		return txn
