#!/usr/bin/env python3

from block import Block
from transactions import TXN
import numpy as np
import random
import sys

# Class for Attack Node
class AttackNode:
	'''
	NodeID: Unique Identifier for each Node
	isSlow: Boolean value stating if the node is slow or fast
	hashPower: Node's fraction of the total hashing power.
	PoWI: The interarrival time between blocks on average
	T_Tx: The mean interarrival time between transactions
	status: Status of miner, possible status: {"free", "mining"}
	cntSuccessfulBlocks: Count of blocks created by this node in the block tree (both public and private)
	blocksTree: Dictionary of public blocks present in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): { "arrival_time": ~ , "Block": Block Object }, ... }
	leafBlocks: Dictionary of public blocks which are leaf nodes in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): Block Object, ...}
	peers: Contains information about the peers of the nodes, Structure = { Peer's NodeID : [ Peer's Node Object, propagation delay (rho_ij), link speed (c_ij) ], ... }
	heardTXNs: Dictionary of all the Transactions which are heard by this node, Structure = { TXNID : TXN Object, ... }
	privateChainExists: Boolean Value stating if private chain is active or not
	privateChain: List of private blocks, Structure = [["creation_time" , Block Object ], []...]
	lastBlock: Last block in the attacker's chain
	futureEvents: Future events that may needed to be cancelled
	atStateZero_: Boolean value stating whether the node is at State Zero Dash {0'}

	'''
	def __init__(self, nodeID, isSlow, hashPower, PoWI, T_Tx):

		self.nodeID = nodeID
		self.isSlow = isSlow
		self.hashPower = hashPower
		self.PoWI = PoWI
		self.T_Tx = T_Tx
		self.status = "free"
		self.cntSuccessfulBlocks = 0
		self.blocksTree = dict()
		self.leafBlocks = dict()
		self.peers = dict()
		self.heardTXNs = dict()
		self.privateChainExists = False
		self.privateChain = []
		self.lastBlock = None
		self.futureEvents = []
		self.atStateZero_ = False

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
		if self.hashPower == 0:
			return np.random.exponential(scale=(sys.maxsize))
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

		# This is a genesis block transaction (initial amount)
		if txn.fromNode == -1:
			nodeBalance[txn.toNode] += txn.amount
			return True

		# Adding and updating balances serially ensures no double spend happens within a block
		if nodeBalance[txn.fromNode] >= txn.amount:
			nodeBalance[txn.fromNode] -= txn.amount
			nodeBalance[txn.toNode] += txn.amount
			return True
		else:
			return False

	# Create Block
	def create_block(self, timestamp, nodeArray):
		
		# If no private chain exists, create a new secret chain starting from highest depth publicly visible block
		if not self.privateChainExists:

			# Finding the Longest chain the Block Tree, Maximum depth leaf node, Arrival Time (To get first seen block)
			longestChainLeaf = None
			maxDepth = -1
			arrivalTime = None

			# To allow randomness in choosing 2 equal depth blocks (resolution of forks)
			leafBlocksKeys = list(self.leafBlocks.keys()) 
			random.shuffle(leafBlocksKeys)

			for leafBlock in leafBlocksKeys:
				if self.leafBlocks[leafBlock].depth > maxDepth or (self.leafBlocks[leafBlock].depth == maxDepth and self.blocksTree[leafBlock]["arrival_time"] < arrivalTime):
					maxDepth = self.leafBlocks[leafBlock].depth
					longestChainLeaf = self.leafBlocks[leafBlock]
					arrivalTime = self.blocksTree[leafBlock]["arrival_time"]

			# Getting transaction details about the longest chain
			nodeBalance, transactionsInChain = self.get_details_chain(longestChainLeaf, nodeArray)

			# Adding Randomness in TXN subset selection
			heardTXNsKeys = list(self.heardTXNs.keys())
			random.shuffle(heardTXNsKeys)

			# Randomly selecting number of TXNs to added into the block, minimum = 0 transactions, maximum = min( number of transactions not included in any blocks in the longest chain, 999 ). 999 txns as 1MB max block size.
			noOfTXNs = random.randint(0, min(len(heardTXNsKeys) - len(transactionsInChain), 999))
			
			transactions = []

			# Adding the coinbase transaction, at 0th index
			transactions.append(TXN(timestamp, None, self.nodeID, 50, True))
			
			cnt = 0
			while(noOfTXNs and cnt < len(heardTXNsKeys)):

				# If transaction is not included in any blocks in the longest chain and If transaction is valid then add to the block
				if (heardTXNsKeys[cnt] not in transactionsInChain) and self.verify_txn(nodeBalance, self.heardTXNs[heardTXNsKeys[cnt]]):
					transactions.append(self.heardTXNs[heardTXNsKeys[cnt]])
					noOfTXNs -= 1

				cnt += 1

			# Create block based on transactions and longest chain leaf node
			block = Block(timestamp, longestChainLeaf, False, transactions)

			# Mining starts
			self.status = "mining"
			self.lastBlock = longestChainLeaf

			return block
		
		else:
			# If private chain exists then building on the last block of the private chain as the lead is >= 1 (private chain is the longest one)
			longestChainLeaf = self.lastBlock

			# Getting transaction details about the longest chain
			nodeBalance, transactionsInChain = self.get_details_chain(longestChainLeaf, nodeArray)

			# Adding Randomness in TXN subset selection
			heardTXNsKeys = list(self.heardTXNs.keys())
			random.shuffle(heardTXNsKeys)

			# Randomly selecting number of TXNs to added into the block, minimum = 0 transactions, maximum = min( number of transactions not included in any blocks in the longest chain, 999 ). 999 txns as 1MB max block size.
			noOfTXNs = random.randint(0, min(len(heardTXNsKeys) - len(transactionsInChain), 999))
			
			transactions = []

			# Adding the coinbase transaction, at 0th index
			transactions.append(TXN(timestamp, None, self.nodeID, 50, True))
			
			cnt = 0
			while(noOfTXNs and cnt < len(heardTXNsKeys)):

				# If transaction is not included in any blocks in the longest chain and If transaction is valid then add to the block
				if (heardTXNsKeys[cnt] not in transactionsInChain) and self.verify_txn(nodeBalance, self.heardTXNs[heardTXNsKeys[cnt]]):
					transactions.append(self.heardTXNs[heardTXNsKeys[cnt]])
					noOfTXNs -= 1

				cnt += 1

			# Create block based on transactions and longest chain leaf node
			block = Block(timestamp, longestChainLeaf, False, transactions)

			# Mining starts
			self.status = "mining"

			return block

	# Create Block at state zero dash {0'}
	def create_block_at_state_zero_dash(self, timestamp, nodeArray):
		
		# At state 0', racing condition b/w honest's and attacker's chain arrives. The selfish miner continues to mine on top of his own block.
		attackerBlock = self.lastBlock

		# Getting transaction details about the chain
		nodeBalance, transactionsInChain = self.get_details_chain(attackerBlock, nodeArray)

		# Adding Randomness in TXN subset selection
		heardTXNsKeys = list(self.heardTXNs.keys())
		random.shuffle(heardTXNsKeys)

		# Randomly selecting number of TXNs to added into the block, minimum = 0 transactions, maximum = min( number of transactions not included in any blocks in the chain, 999 ). 999 txns as 1MB max block size.
		noOfTXNs = random.randint(0, min(len(heardTXNsKeys) - len(transactionsInChain), 999))
		
		transactions = []

		# Adding the coinbase transaction, at 0th index
		transactions.append(TXN(timestamp, None, self.nodeID, 50, True))
		
		cnt = 0
		while(noOfTXNs and cnt < len(heardTXNsKeys)):

			# If transaction is not included in any blocks in the chain and If transaction is valid then add to the block
			if (heardTXNsKeys[cnt] not in transactionsInChain) and self.verify_txn(nodeBalance, self.heardTXNs[heardTXNsKeys[cnt]]):
				transactions.append(self.heardTXNs[heardTXNsKeys[cnt]])
				noOfTXNs -= 1

			cnt += 1

		# Create block based on transactions and attacker's block
		block = Block(timestamp, attackerBlock, False, transactions)

		# Mining starts
		self.status = "mining"

		return block

	# Broadcast Block at state zero dash {0'}
	def broadcast_block_at_state_zero_dash(self, block, timestamp):
		# Finding the Longest chain depth the Block Tree, to verify if it is still the longest
		maxDepth = -1

		parentBlockHash = block.prevBlockHash

		for leafBlock in self.leafBlocks.keys():
			if self.leafBlocks[leafBlock].depth > maxDepth:
				maxDepth = self.leafBlocks[leafBlock].depth

		# Checking the block still extends the longest, if honest miners win, then this will fail
		if(maxDepth > block.previousBlock.depth):
			# Free from Mining
			self.status = "free"
			self.privateChainExists = False
			self.privateChain = []
			self.lastBlock = None
			self.atStateZero_ = False
			return False

		# Adding block to public block Tree
		self.blocksTree[block.blockHash] = { "arrival_time": timestamp, "Block": block }

		# Removing parent block as leaf node and adding current block as leaf node
		self.leafBlocks.pop(parentBlockHash)
		self.leafBlocks[block.blockHash] = block

		# Free from Mining
		self.status = "free"
		self.privateChainExists = False
		self.privateChain = []
		self.lastBlock = None
		self.atStateZero_ = False

		# Incrementing the count as the block is successfully created
		self.cntSuccessfulBlocks += 1

		return True

	# Add Block to private chain
	def finished_block(self, block, timestamp):
		# Finding the Longest chain depth the Block Tree, to verify if it is still the longest
		maxDepth = -1

		parentBlockHash = block.prevBlockHash

		for leafBlock in self.leafBlocks.keys():
			if self.leafBlocks[leafBlock].depth > maxDepth:
				maxDepth = self.leafBlocks[leafBlock].depth

		# Checking the block still extends the longest
		if(maxDepth > block.previousBlock.depth):
			# The LVC exceeds the length of the selfish miner’s private chain
			# Free from Mining
			self.status = "free"
			self.privateChainExists = False
			self.privateChain = []
			self.lastBlock = None
			self.atStateZero_ = False
			return False

		# Free from Mining
		self.status = "free"

		# Incrementing the count as the block is successfully created
		self.cntSuccessfulBlocks += 1

		# Adding the block into the private chain
		self.privateChainExists = True
		self.privateChain.append([timestamp, block])
		self.lastBlock = block
		self.atStateZero_ = False

		return True

	# Validate Block
	def validate_block(self, timestamp, block, nodeArray):
		# Getting parent block of the node
		parentBlock = block.previousBlock

		# If parent not in block tree, return false (cannot validate)
		if parentBlock.blockHash not in self.blocksTree:
			return False

		# Getting transaction details about the parent block
		nodeBalance, transactionsInChain = self.get_details_chain(parentBlock, nodeArray)

		# Validating the Transactions
		for txn in block.transactions:
			# If coinbase transaction amount is not 50, return False
			if txn.isCoinbase:
				if txn.amount != 50:
					return False
				continue

			# If transaction invalid, return False
			if not self.verify_txn(nodeBalance, txn):
				return False

		# All transactions Validated
		# Adding block into the block tree
		self.blocksTree[block.blockHash] = { "arrival_time": timestamp, "Block": block }

		# Add block as a leaf node (no block pointing to the current block), and remove parent as leaf node as current block is pointing towards it
		if parentBlock.blockHash in self.leafBlocks:
			self.leafBlocks.pop(parentBlock.blockHash)
			self.leafBlocks[block.blockHash] = block
		else:
			self.leafBlocks[block.blockHash] = block

		# Adding transactions in block into heardTXNs
		for txn in block.transactions:
			if not txn.isCoinbase:
				self.heardTXNs[txn.TXNID] = txn

		return True



	# Get all the transaction details about the chain from a block
	def get_details_chain(self, block, nodeArray):
		# Initialize an empty list to store transactions seen in the chain.
		transactionsInChain = []
		# Initialize an dictionary to store node balances.
		nodeBalance = dict()
		for node in nodeArray:
			nodeBalance[node.nodeID] = 0
		nodeBalance[-1] = 0
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
					# Add the transaction to the list of transactions in the chain.
					transactionsInChain.append(txn.TXNID)
					nodeBalance[sender] -= amount
				nodeBalance[recipient] += amount
			# Update the current block to be the parent block for the next iteration. If genesis block then parent will be None, so loop exit
			parentBlock = currBlock.previousBlock
			currBlock = parentBlock
		
		return  nodeBalance, transactionsInChain