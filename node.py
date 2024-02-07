#!/usr/bin/env python3

# Class for Node
class Node:
	'''
	NodeID: Unique Identifier for each Node
	isSlow: Boolean value stating if the node is slow or fast
	isLowCPU: Boolean value stating if the node has low or high CPU
	hashPower: Node's fraction of the total hashing power.
	PoWI: The interarrival time between blocks  on average
	status: Status of miner, possible status: {"free", "mining"}
	blocksSeen: Dictionary of blocks present in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): { "arrival_time": ~ , "Block": Block Object } }
	leafBlocks: Dictionary of blocks which are leaf nodes in the Node's Blockchain Tree, Structure = { BlockID (BlockHash): Block Object }
	peers: Contains information about the peers of the nodes, Structure = { Peer's NodeID : [ Peer's Node Object, propagation delay (rho_ij), link speed (c_ij) ], ... }
	heardTXNs: All the Transactions which are heard by this node.

	'''
	def __init__(self, nodeID, isSlow, isLowCPU, hashPower, PoWI):

		self.nodeID = nodeID
		self.isSlow = isSlow
		self.isLowCPU = isLowCPU
		self.hashPower = hashPower
		self.PoWI = PoWI
		self.status = "free"
		self.blocksSeen = dict()
		self.leafBlocks = dict()
		self.peers = dict()
		self.heardTXNs = []
