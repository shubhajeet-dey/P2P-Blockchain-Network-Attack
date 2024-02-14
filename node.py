#!/usr/bin/env python3
import copy
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

	# Calculating next transaction time gap
	def next_create_transaction_delay(self):
		return np.random.exponential(scale=self.T_Tx)

	# Calculating POW time (T_k)
	def calculate_POW_time(self):
		return np.random.exponential(scale=(self.PoWI / self.hashPower))

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

	# Received a transaction from a peer
	def receive_transaction(self, txn):
		# Adding in seen transactions
		self.heardTXNs[txn.TXNID] = txn

	# Verifying the transaction
	def verify_txn(self, nodeBalance, txn):
		# Adding and updating balances serially ensures no double spend happens within a block
		if nodeBalance[txn.fromNode] >= txn.amount:
			nodeBalance[txn.fromNode] -= txn.amount
			nodeBalance[txn.toNode] += txn.amount
			return True
		else:
			return False

	# Create Block
	def create_block(self, timestamp):
		
		# Finding the Longest chain the Block Tree, Maximum depth leaf node
		longestChainLeaf = None
		maxDepth = 0

		# To allow randomness in choosing 2 equal depth blocks
		leafBlocksKeys = self.leafBlocks.keys() 
		random.shuffle(leafBlocksKeys)

		for leafBlock in leafBlocksKeys:
			if self.leafBlocks[leafBlock].depth > maxDepth:
				maxDepth = self.leafBlocks[leafBlock].depth
				longestChainLeaf = self.leafBlocks[leafBlock]

		# Getting transaction details about the longest chain
		nodeBalance, transactionsInChain = self.get_details_longest_chain(longestChainLeaf)

		# Adding Randomness in TXN subset selection
		heardTXNsKeys = self.heardTXNs.keys()
		random.shuffle(heardTXNsKeys)

		# Randomly selecting number of TXNs to added into the block, minimum = 0 transactions, maximum = min( number of transactions not included in any blocks in the longest chain, 999 ). 999 txns as 1MB max block size.
		noOfTXNs = random.randint(0, min(len(heardTXNsKeys) - len(transactionsInChain), 999))
		
		transactions = []

		# Adding the coinbase transaction, at 0th index
		transactions.append(TXN(timestamp, None, self.nodeID, 50, True))
		
		cnt = 0
		while(noOfTXNs and cnt < len(heardTXNsKeys)):

			# If transaction is not included in any blocks in the longest chain and If transaction is valid then add to the block
			if (heardTXNsKeys[cnt] not in transactionsInChain) and self.verify_txn(nodeBalance, heardTXNs[heardTXNsKeys[cnt]]):
				transactions.append(heardTXNs[heardTXNsKeys[cnt]])
				noOfTXNs -= 1

			cnt += 1

		# Create block based on transactions and longest chain leaf node
		block = Block(timestamp, longestChainLeaf, False, transactions)

		# Mining starts
		self.status = "mining"

		return block

	# Broadcast Block
	def broadcast_block(self, block, timestamp):
		# Finding the Longest chain the Block Tree, Maximum depth leaf node, to verify if it is still the longest
		longestChainLeaf = None
		maxDepth = 0

		parentBlockHash = block.prevBlockHash

		for leafBlock in self.leafBlocks.keys():
			if self.leafBlocks[leafBlock].depth > maxDepth:
				maxDepth = self.leafBlocks[leafBlock].depth
				longestChainLeaf = self.leafBlocks[leafBlock]

		# Checking the block still extends the longest
		if(not (longestChainLeaf.blockHash == parentBlockHash) ):
			return False

		# Adding block to block Tree
		self.blocksSeen[block.blockHash] = { "arrival_time": timestamp, "Block": block}

		# Removing parent block as leaf node and adding current block as leaf node
		self.leafBlocks.pop(parentBlockHash)
		self.leafBlocks[block.blockHash] = block

		# Free from Mining
		self.status = "free"

		return True

	# Get all the transaction details about the longest chain
	def get_details_longest_chain(self, block):
		# Initialize an empty list to store transactions seen in the chain.
		transactionsInChain = []
		# Initialize an empty dictionary to store node balances.
		nodeBalance = dict()
		# Continue looping indefinitely until condition is met.
		currBlock = block
		while currBlock:
			# Get the transactions from the current block.
			transactions = currBlock.transactions

			# Iterate through each transaction in the block.
			for txn in transactions:
				sender = txn.fromNode
				recipient = txn.toNode
				amount = txn.amount
				# If the transaction is not a coinbase transaction, update the node balances accordingly.
				if not txn.isCoinbase:
					nodeBalance[sender] -= amount
				nodeBalance[recipient] += amount
				# Add the transaction to the list of transactions in the chain.
				transactionsInChain.append(txn.TXNID)
			# Update the current block to be the parent block for the next iteration. If genesis block then parent will be None, so loop exit
			parentBlock = currBlock.previousBlock
			currBlock = parentBlock
		
		return  nodeBalance, transactionsInChain