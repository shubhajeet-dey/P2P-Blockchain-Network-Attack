#!/usr/bin/env python3
from transactions import TXN
from block import Block
import random

# Event class
class Event:
    '''
    timestamp: TimeStamp of the Event
    createdBy: The event is triggered by a parent event. Who executed the parent event (NodeID)?
    executedBy: The event needs to be executed by which node (nodeID)
    eventObject: Class Object which might be processed by this event
    eventType: Type of event, possible types: 
        "genesis block creation" --> ("genesis")
        "create transaction at node i" --> ("create", "TXN")
        "receive transaction at node i" --> ("receive", "TXN")
        "create block at node i" --> ("create", "block")
        "broadcast block at node i" -->  ("broadcast", "block")
        "receive block at node i" --> ("receive", "block")

    '''
    def __init__(self, timestamp, createdBy, executedBy, eventObject, eventType):
        self.timestamp = timestamp
        self.createdBy = createdBy
        self.executedBy = executedBy
        self.eventOject = eventObject
        self.eventType = eventType

    # Comparator function for priority queue (sorted by increasing order of timestamp)
    def __lt__(self, otherEvent):
        return self.timestamp < otherEvent.timestamp

    # Execute the Event based on eventType
    def execute(self, nodeArray):
        if self.eventType[0] == "genesis":
            self.create_genesis_block(nodeArray)

        elif self.eventType[0] == "create":
            if self.eventType[1] == "TXN":
                self.create_transaction(nodeArray)
            else:
                self.create_block(nodeArray)

        elif self.eventType[0] == "broadcast" and self.eventType[1] == "block":
            self.broadcast_block(nodeArray)

        else:
            if self.eventType[1] == "TXN":
                self.receive_transaction(nodeArray)
            else:
                self.receive_block(nodeArray)

    # Create genesis block
    def create_genesis_block(self, nodeArray):
        genesisTransactions = []

        # Adding a random amount from 500 - 1500 coins in each node
        for i in range(len(nodeArray)):
            amount = random.randint(500, 1500)
            # Here -1 means initial amount given, by God
            genesisTransactions.append(TXN(0, -1, nodeArray[i].nodeID, amount, False))

        # Creating the genesis block
        genesisBlock = Block(0, None, True, genesisTransactions)

        # Adding the genesis block in each node
        for i in range(len(nodeArray)):
            nodeArray[i].blocksSeen[genesisBlock.blockHash] = { "arrival_time": 0, "Block": genesisBlock }
            nodeArray[i].leafBlocks[genesisBlock.blockHash] = genesisBlock
            for txn in genesisTransactions:
                nodeArray[i].heardTXNs[txn.TXNID] = txn

        futureEvents = []

        # Adding future transactional events for all the nodes at timestamp 1
        for i in range(len(nodeArray)):
            futureEvents.append(Event(1, None, nodeArray[i].nodeID, None, ("create", "TXN")))

        # Adding future create Block events for all the nodes at timestamp 1
        for i in range(len(nodeArray)):
            futureEvents.append(Event(1, None, nodeArray[i].nodeID, None, ("create", "block")))

        # Random shuffling for randomness
        random.shuffle(futureEvents)
        return futureEvents

    # Create transaction at node i
    def create_transaction(self, nodeArray):
        txn = nodeArray[self.executedBy].create_transaction(nodeArray, self.timestamp)
        
        futureEvents = []

        # Transmit created transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        # Add event to create transaction after an exponential time gap (exponential interarrival time)
        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].next_create_transaction_delay())
        futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, None, ("create", "TXN")))

        return futureEvents

    # Receive transaction at node i
    def receive_transaction(self, nodeArray):
        # Retrieving the Transaction
        txn = self.eventObject

        # Loop-Less transaction forwarding
        # Checking if the transaction is already heard at this node
        # If heard then transaction is already processed (sent to peers) in the past
        if txn.TXNID in nodeArray[self.executedBy].heardTXNs:
            return

        nodeArray[self.executedBy].receive_transaction(txn)

        futureEvents = []

        # Transmit received transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # The receive event is created by the transmitting node, so ignoring it for Loop-Less transaction forwarding
            if peer == self.createdBy:
                continue

            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        return futureEvents

    # Create block at node i
    def create_block(self, nodeArray):
        
        # Node is busy mining other block (not free)
        if not (nodeArray[self.executedBy].status == "free"):
            return []

        block = nodeArray[self.executedBy].create_block(self.timestamp)

        futureEvents = []

        # Calculating timestamp of the future event (Broadcasting the created block after POW)
        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_POW_time())

        # Adding broadcast event in the future
        futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, block, ("broadcast", "block")))

        return futureEvents

    # Broadcast block at node i
    def broadcast_block(self, nodeArray):
        # Retrieving the Block
        block = self.eventObject

        futureEvents = []

        # If the same longest chain, broadcast the block
        if nodeArray[self.executedBy].broadcast_block(block, self.timestamp):

            # Size of the block in KBs
            blockSize = len(block.transactions)

            # Broadcast the new block to the peer nodes
            for peer in nodeArray[self.executedBy].peers.keys():

                # Calculating timestamp of the future event depending size of block
                future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                # Adding event to receive the block at the peers
                futureEvents.append(Event(future_timestamp, self.executedBy, peer, block, ("receive", "block")))

        # Adding an block creation event at same timestamp (broadcast event over)
        futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

        return futureEvents
