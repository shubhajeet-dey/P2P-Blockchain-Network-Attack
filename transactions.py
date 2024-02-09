#!/usr/bin/env python3
import secrets

# Class for Transaction
class TXN:
	'''
	TXNID: Unique Identifier for each Transaction
	creationTime: Creation time of the TXN.
	fromNode: Node from which the money is deduced. 
	toNode: Node to which recieves the payment.
	amount: Amount of the Transaction
	isCoinbase: Boolean value representing if it is a coinbase transaction
	TXNString: String format of transaction
	TXNsize: Size of Transaction (1 KB = (8 × 10^3 bits) = 8000 bits)

	'''
	def __init__(self, creationTime, fromNode, toNode, amount, isCoinbase):
		self.creationTime = creationTime
		self.fromNode = fromNode
		self.toNode = toNode
		self.amount = amount
		self.isCoinbase = isCoinbase
		self.TXNsize = 8000

		# Generating TXNID
		self.TXNID = secrets.token_hex(32)

		if not self.isCoinbase:
			self.TXNString = self.TXNID + ': ' + str(self.fromNode) + ' pays ' + str(self.toNode) + ' ' + str(self.amount) + ' coins'
		else:
			self.TXNString = self.TXNID + ': ' + str(self.toNode) + ' mines ' + str(self.amount) + ' coins'