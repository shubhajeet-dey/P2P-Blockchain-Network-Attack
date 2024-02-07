#!/usr/bin/env python3
import hashlib

class blocks:
    def __init__(self, blockType, timestamp, minerNode, prevBlockHash) :
        self.blockType = blockType
        self.timestamp = timestamp
        self.minerNode = minerNode
        self.prevBlockHash = prevBlockHash
        self.transactions = []
        self.blockHash = self.calculateBlockHash()
    
    def calculateBlockHash(self):
        txnStrings = ''.join(transaction.TXNString for transaction in self.transactions)
        concatenatedString = str(self.timestamp) + txnStrings + str(self.prevBlockHash)
        blockHash = hashlib.sha256(concatenatedString.encode('UTF-8'))
        return blockHash.hexdigest
    
    def validateBlock(self):
        