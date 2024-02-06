#!/usr/bin/env python3
from hashlib import sha256

# Class for Transaction
class TXN:
	'''
	TXNID: Unique Identifier for each Transaction
	creationTime: Creation time of the TXN.
	fromNode: Node from which the money is deduced. 
	toNode: Node to which recieves the payment.
	amount: Amount of the Transaction
	TXNString: String format of transaction
	isCoinbase: Boolean value representing if it is a coinbase transaction
	TXNsize: Size of Transaction (1 KB = (8 × 10^3 bits) = 8000 bits)

	'''
	def __init__(self, creationTime, fromNode, toNode, amount, TXNString, isCoinbase):
		self.creationTime = creationTime
		self.fromNode = fromNode
		self.toNode = toNode
		self.amount = amount
		self.TXNString = TXNString
		self.isCoinbase = isCoinbase
		self.TXNsize = 8000

		# Generating TXNID using TXN data
		TXNData = str(self.creationTime) + self.TXNString
		self.TXNID = sha256(TXNData.encode('utf-8')).hexdigest()