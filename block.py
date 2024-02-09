#!/usr/bin/env python3
import hashlib

class Block:
    '''
    timestamp: Creation time of the Block
    previousBlock: Previous/Parent Block object
    prevBlockHash: Previous/Parent Block Hash
    isGenesis: Boolean value stating whether this block is genesis block or not
    transactions: Set of transactions under this block (0th index stating coinbase)
    blockHash: Unique Identifier for each Block

    '''
    def __init__(self, timestamp, previousBlock, isGenesis) :
        self.timestamp = timestamp
        self.previousBlock = previousBlock
        self.prevBlockHash = previousBlock.blockHash
        self.isGenesis = isGenesis
        self.transactions = []
        self.blockHash = self.calculateBlockHash()
    
    def calculateBlockHash(self):
        txnStrings = ''.join(transaction.TXNString for transaction in self.transactions)
        blockData = str(self.timestamp) + txnStrings + str(self.prevBlockHash)
        blockHash = hashlib.sha256(blockData.encode('utf-8'))
        return blockHash.hexdigest()
    
    # def validateBlock(self):
        