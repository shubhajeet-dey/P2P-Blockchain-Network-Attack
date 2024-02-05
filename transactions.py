#!/usr/bin/env python3
from hashlib import sha256

# Class for Transaction
class TXN:
	'''
	TXNID: Unique Identifier for each Transaction
	creationTime: Creation time of the TXN.
	fromNode: Node from which the money is deduced. 
	toNode: Node to which recieves the payment.
	TXNString: String format of transaction
	isCoinbase: Boolean value representing if it is a coinbase transaction
	TXNsize: Size of Transaction (1 KB = (8 × 10^3 bits) = 8000 bits)

	'''
	def __init__(self, creationTime, fromNode, toNode, TXNString, isCoinbase):
		self.creationTime = creationTime
		self.fromNode = fromNode
		self.toNode = toNode
		self.TXNString = TXNString
		self.isCoinbase = isCoinbase
		self.TXNsize = 8000


		self.TXNID = hashlib.sha256(str.encode('utf-8')).hexdigest()