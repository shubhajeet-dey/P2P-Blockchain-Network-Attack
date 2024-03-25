#!/usr/bin/env python3
from transactions import TXN
from block import Block
import random
import secrets

# Event class
class Event:
    '''
    eventID: Unique Identifier for each Event
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
    Now, as attackers are present, the events will change as these:
        "create transaction at attacker node i" --> ("create", "TXN")
        "receive transaction at attacker node i" --> ("receive", "TXN")
        "create block at attacker node i" --> ("create", "block")
        "Mining finished for a block at attacker node i" -->  ("finished", "block")
        "receive block at attacker node i" --> ("receive", "block")
    '''
    def __init__(self, timestamp, createdBy, executedBy, eventObject, eventType):
        self.eventID = secrets.token_hex(32)
        self.timestamp = timestamp
        self.createdBy = createdBy
        self.executedBy = executedBy
        self.eventObject = eventObject
        self.eventType = eventType

    # Comparator function for priority queue (sorted by increasing order of timestamp)
    def __lt__(self, otherEvent):
        return self.timestamp < otherEvent.timestamp

    # Execute the Event based on eventType
    def execute(self, nodeArray):

        # Checking if event is related to a attack node
        if (self.executedBy is not None) and (type(nodeArray[self.executedBy]).__name__ == "AttackNode"):
            
            # Printing to terminal
            print("EVENT: Timestamp: " + str(self.timestamp) + " milliseconds, Type: " + self.eventType[0] + " " + self.eventType[1] + " at attack node " + str(self.executedBy) + " : ", end='')

            if self.eventType[0] == "create":
                if self.eventType[1] == "TXN":
                    return self.create_transaction_attack_node(nodeArray)
                else:
                    return self.create_block_attack_node(nodeArray)

            elif self.eventType[0] == "finished" and self.eventType[1] == "block":
                return self.finished_block_attack_node(nodeArray)

            else:
                if self.eventType[1] == "TXN":
                    return self.receive_transaction_attack_node(nodeArray)
                else:
                    return self.receive_block_attack_node(nodeArray)


        else:
            # Printing to terminal
            print("EVENT: Timestamp: " + str(self.timestamp) + " milliseconds, Type: " + self.eventType[0] + (" block creation : " if self.eventType[0] == "genesis" else " " + self.eventType[1] + " at node " + str(self.executedBy) + " : "), end='')
            
            if self.eventType[0] == "genesis":
                return self.create_genesis_block(nodeArray)

            elif self.eventType[0] == "create":
                if self.eventType[1] == "TXN":
                    return self.create_transaction(nodeArray)
                else:
                    return self.create_block(nodeArray)

            elif self.eventType[0] == "broadcast" and self.eventType[1] == "block":
                return self.broadcast_block(nodeArray)

            else:
                if self.eventType[1] == "TXN":
                    return self.receive_transaction(nodeArray)
                else:
                    return self.receive_block(nodeArray)

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
        cancelledEvents = []

        # Adding future transactional events for all the nodes at timestamp 1
        for i in range(len(nodeArray)):
            futureEvents.append(Event(1, None, nodeArray[i].nodeID, None, ("create", "TXN")))

        # Adding future create Block events for all the nodes at timestamp 1
        for i in range(len(nodeArray)):
            futureEvents.append(Event(1, None, nodeArray[i].nodeID, None, ("create", "block")))

        # Random shuffling for randomness
        random.shuffle(futureEvents)

        print("Successful!")

        return futureEvents, cancelledEvents

    # Create transaction at attack node i
    def create_transaction_attack_node(self, nodeArray):
        txn = nodeArray[self.executedBy].create_transaction(nodeArray, self.timestamp)
        
        futureEvents = []
        cancelledEvents = []

        # Transmit created transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        # Add event to create transaction after an exponential time gap (exponential interarrival time)
        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].next_create_transaction_delay())
        futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, None, ("create", "TXN")))

        print("Successful!")

        return futureEvents, cancelledEvents

    # Create transaction at node i
    def create_transaction(self, nodeArray):
        txn = nodeArray[self.executedBy].create_transaction(nodeArray, self.timestamp)
        
        futureEvents = []
        cancelledEvents = []

        # Transmit created transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        # Add event to create transaction after an exponential time gap (exponential interarrival time)
        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].next_create_transaction_delay())
        futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, None, ("create", "TXN")))

        print("Successful!")

        return futureEvents, cancelledEvents

    # Receive transaction at attack node i
    def receive_transaction_attack_node(self, nodeArray):
        # Retrieving the Transaction
        txn = self.eventObject

        # Loop-Less transaction forwarding
        # Checking if the transaction is already heard at this node
        # If heard then transaction is already processed (sent to peers) in the past
        if txn.TXNID in nodeArray[self.executedBy].heardTXNs:
            print("Already Heard!")
            return [], []

        nodeArray[self.executedBy].receive_transaction(txn)

        futureEvents = []
        cancelledEvents = []

        # Transmit received transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # The receive event is created by the transmitting node, so ignoring it for Loop-Less transaction forwarding
            if peer == self.createdBy:
                continue

            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        print("Successful!")

        return futureEvents, cancelledEvents

    # Receive transaction at node i
    def receive_transaction(self, nodeArray):
        # Retrieving the Transaction
        txn = self.eventObject

        # Loop-Less transaction forwarding
        # Checking if the transaction is already heard at this node
        # If heard then transaction is already processed (sent to peers) in the past
        if txn.TXNID in nodeArray[self.executedBy].heardTXNs:
            print("Already Heard!")
            return [], []

        nodeArray[self.executedBy].receive_transaction(txn)

        futureEvents = []
        cancelledEvents = []

        # Transmit received transaction to peer nodes
        for peer in nodeArray[self.executedBy].peers.keys():
            # The receive event is created by the transmitting node, so ignoring it for Loop-Less transaction forwarding
            if peer == self.createdBy:
                continue

            # Calculating timestamp of the future event, size of txn is 1KB
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(1, peer))

            # Adding event to receive the transaction at the peers
            futureEvents.append(Event(future_timestamp, self.executedBy, peer, txn, ("receive", "TXN")))

        print("Successful!")

        return futureEvents, cancelledEvents

    # Create block at attack node i
    def create_block_attack_node(self, nodeArray):
        
        # Node is busy mining other block (not free)
        if not (nodeArray[self.executedBy].status == "free"):
            print("Node busy!")
            return [], []

        futureEvents = []
        cancelledEvents = []

        # Node a state zero dash (racing condition b/w honest's and attacker's chains)
        if nodeArray[self.executedBy].atStateZero_ :
            block = nodeArray[self.executedBy].create_block_at_state_zero_dash(self.timestamp, nodeArray)

            # Calculating timestamp of the future event (Broadcasting the created block after POW)
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_POW_time())

            # Adding finished event in the future
            futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, block, ("finished", "block")))
            nodeArray[self.executedBy].futureEvents = [futureEvents[-1].eventID]

        else:
            # For other states the block is generated on longest chain (both including private and public) 
            block = nodeArray[self.executedBy].create_block(self.timestamp, nodeArray)

            # Calculating timestamp of the future event (Broadcasting the created block after POW)
            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_POW_time())

            # Adding finished event in the future
            futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, block, ("finished", "block")))
            nodeArray[self.executedBy].futureEvents = [futureEvents[-1].eventID]

        print("Successful!")

        return futureEvents, cancelledEvents

    # Create block at node i
    def create_block(self, nodeArray):
        
        # Node is busy mining other block (not free)
        if not (nodeArray[self.executedBy].status == "free"):
            print("Node busy!")
            return [], []

        block = nodeArray[self.executedBy].create_block(self.timestamp, nodeArray)

        futureEvents = []
        cancelledEvents = []

        # Calculating timestamp of the future event (Broadcasting the created block after POW)
        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_POW_time())

        # Adding broadcast event in the future
        futureEvents.append(Event(future_timestamp, self.executedBy, self.executedBy, block, ("broadcast", "block")))
        nodeArray[self.executedBy].futureBroadCastEvent = futureEvents[-1].eventID

        print("Successful!")

        return futureEvents, cancelledEvents

    # Mining on block finishes at attack node i
    def finished_block_attack_node(self, nodeArray):
        # Retrieving the Block
        block = self.eventObject

        futureEvents = []
        cancelledEvents = []

        # Node a state zero dash (racing condition b/w honest's and attacker's chains)
        if nodeArray[self.executedBy].atStateZero_ :

            # If the longest chain, broadcast the block (attacker wins and makes his/her block public)
            if nodeArray[self.executedBy].broadcast_block_at_state_zero_dash(block, self.timestamp):

                # Size of the block in KBs
                blockSize = len(block.transactions)

                # Broadcast the new block to the peer nodes
                for peer in nodeArray[self.executedBy].peers.keys():

                    # Calculating timestamp of the future event depending size of block
                    future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                    # Adding event to receive the block at the peers
                    futureEvents.append(Event(future_timestamp, self.executedBy, peer, block, ("receive", "block")))

                print("Successful!")
            else:
                print("Failed! (Not Longest Chain)")

            # Adding an block creation event at same timestamp (broadcast event over)
            futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

            return futureEvents, cancelledEvents

        else:
            # If the same longest chain, add block into the private chain
            if nodeArray[self.executedBy].finished_block(block, self.timestamp):
                print("Successful!")
            else:
                print("Failed! (Not Longest Chain)")

            # Adding an block creation event at same timestamp (mining event over)
            futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

            return futureEvents, cancelledEvents

    # Broadcast block at node i
    def broadcast_block(self, nodeArray):
        # Retrieving the Block
        block = self.eventObject

        futureEvents = []
        cancelledEvents = []

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

            print("Successful!")
        else:
            print("Failed! (Not Longest Chain)")

        # Adding an block creation event at same timestamp (broadcast event over)
        futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

        return futureEvents, cancelledEvents

    # Receive block at attack node i
    def receive_block_attack_node(self, nodeArray):
        # Retrieving the Block
        block = self.eventObject

        # Loop-Less Block forwarding
        # Checking if the block is already heard at this node
        # If heard then block is already processed in the past
        if block.blockHash in nodeArray[self.executedBy].blocksTree:
            print("Already Heard!")
            return [], []

        futureEvents = []
        cancelledEvents = []

        # If valid block then change the state
        if nodeArray[self.executedBy].validate_block(self.timestamp, block, nodeArray):

            # If node is not doing any selfish mining or if the LVC exceeds the length of the selfish miner’s private chain then start a new attack on the last block of the longest chain visible.
            if (nodeArray[self.executedBy].lastBlock is None) or (nodeArray[self.executedBy].lastBlock.depth < block.depth):
                
                nodeArray[self.executedBy].privateChainExists = False
                nodeArray[self.executedBy].lastBlock = None
                cancelledEvents.extend(nodeArray[self.executedBy].futureEvents)
                nodeArray[self.executedBy].futureEvents = []
                nodeArray[self.executedBy].atStateZero_ = False
                nodeArray[self.executedBy].status = "free"

                # Making private blocks public for better visualization
                for privateBlock in nodeArray[self.executedBy].privateChain:

                    # Adding block to public block Tree
                    nodeArray[self.executedBy].blocksTree[privateBlock[1].blockHash] = { "arrival_time": privateBlock[0], "Block": privateBlock[1] }

                    if privateBlock[1].previousBlock.blockHash in nodeArray[self.executedBy].leafBlocks:
                        nodeArray[self.executedBy].leafBlocks.pop(privateBlock[1].previousBlock.blockHash)
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]
                    else:
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]

                    # Size of the block in KBs
                    blockSize = len(privateBlock[1].transactions)

                    # Transmitting the block to the peer nodes
                    for peer in nodeArray[self.executedBy].peers.keys():

                        # Calculating timestamp of the future event depending size of block
                        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                        # Adding event to receive the block at the peers
                        futureEvents.append(Event(future_timestamp, self.executedBy, peer, privateBlock[1], ("receive", "block")))

                nodeArray[self.executedBy].privateChain = []

            # Block of same depth or lower as starting block (block from which attack start) --> No change
            elif (not nodeArray[self.executedBy].privateChainExists):
                
                pass

            else:
                # Private chain exists

                # Starting Block Depth
                startingDepth = nodeArray[self.executedBy].privateChain[0][1].previousBlock.depth

                # New block is appended in part lower than or equal to starting block (block from which attack start) --> No change
                if block.depth <= startingDepth:
                    pass

                # If the lead of the selfish miner was 1 block over the LVC, and the lead now becomes zero (1 --> 0')
                elif (nodeArray[self.executedBy].lastBlock.depth == block.depth):
                
                    nodeArray[self.executedBy].privateChainExists = False
                    nodeArray[self.executedBy].atStateZero_ = True

                    # Making private block public (1 --> 0')
                    privateBlock = nodeArray[self.executedBy].privateChain[0]

                    # Adding block to public block Tree
                    nodeArray[self.executedBy].blocksTree[privateBlock[1].blockHash] = { "arrival_time": privateBlock[0], "Block": privateBlock[1] }

                    if privateBlock[1].previousBlock.blockHash in nodeArray[self.executedBy].leafBlocks:
                        nodeArray[self.executedBy].leafBlocks.pop(privateBlock[1].previousBlock.blockHash)
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]
                    else:
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]

                    # Size of the block in KBs
                    blockSize = len(privateBlock[1].transactions)

                    # Transmitting the block to the peer nodes
                    for peer in nodeArray[self.executedBy].peers.keys():

                        # Calculating timestamp of the future event depending size of block
                        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                        # Adding event to receive the block at the peers
                        futureEvents.append(Event(future_timestamp, self.executedBy, peer, privateBlock[1], ("receive", "block")))

                    nodeArray[self.executedBy].privateChain = []

                # If the lead of the selfish miner over the LVC is 2 blocks and then one block gets added to the LVC (New lead = 1) (2 --> 0)
                elif (nodeArray[self.executedBy].lastBlock.depth - 1 == block.depth):

                    nodeArray[self.executedBy].privateChainExists = False
                    nodeArray[self.executedBy].lastBlock = None
                    nodeArray[self.executedBy].atStateZero_ = False

                    # Making private blocks public and broadcasting immediately
                    for privateBlock in nodeArray[self.executedBy].privateChain:

                        # Adding block to public block Tree
                        nodeArray[self.executedBy].blocksTree[privateBlock[1].blockHash] = { "arrival_time": privateBlock[0], "Block": privateBlock[1] }

                        if privateBlock[1].previousBlock.blockHash in nodeArray[self.executedBy].leafBlocks:
                            nodeArray[self.executedBy].leafBlocks.pop(privateBlock[1].previousBlock.blockHash)
                            nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]
                        else:
                            nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]

                        # Size of the block in KBs
                        blockSize = len(privateBlock[1].transactions)

                        # Transmitting the block to the peer nodes
                        for peer in nodeArray[self.executedBy].peers.keys():

                            # Calculating timestamp of the future event depending size of block
                            future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                            # Adding event to receive the block at the peers
                            futureEvents.append(Event(future_timestamp, self.executedBy, peer, privateBlock[1], ("receive", "block")))

                    nodeArray[self.executedBy].privateChain = []

                # If the lead of the selfish miner over the LVC is greater than 2, as soon as the LVC increases in length by 1 block, then the selfish miner makes public one more block (i --> i-1, i >= 3)
                elif (nodeArray[self.executedBy].lastBlock.depth - block.depth >= 2):

                    nodeArray[self.executedBy].atStateZero_ = False

                    # Making a block (first block in private chain) public and broadcasting it
                    privateBlock = nodeArray[self.executedBy].privateChain[0]
                    nodeArray[self.executedBy].privateChain.pop(0)

                    # Adding block to public block Tree
                    nodeArray[self.executedBy].blocksTree[privateBlock[1].blockHash] = { "arrival_time": privateBlock[0], "Block": privateBlock[1] }

                    if privateBlock[1].previousBlock.blockHash in nodeArray[self.executedBy].leafBlocks:
                        nodeArray[self.executedBy].leafBlocks.pop(privateBlock[1].previousBlock.blockHash)
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]
                    else:
                        nodeArray[self.executedBy].leafBlocks[privateBlock[1].blockHash] = privateBlock[1]

                    # Size of the block in KBs
                    blockSize = len(privateBlock[1].transactions)

                    # Transmitting the block to the peer nodes
                    for peer in nodeArray[self.executedBy].peers.keys():

                        # Calculating timestamp of the future event depending size of block
                        future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                        # Adding event to receive the block at the peers
                        futureEvents.append(Event(future_timestamp, self.executedBy, peer, privateBlock[1], ("receive", "block")))

            print("Successful!")
        else:
            print("Failed! Invalid Block")

        # Adding an block creation event at same timestamp (validation event over)
        futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

        return futureEvents, cancelledEvents

    # Receive block at node i
    def receive_block(self, nodeArray):
        # Retrieving the Block
        block = self.eventObject

        # Loop-Less Block forwarding
        # Checking if the block is already heard at this node
        # If heard then block is already processed (validated and sent to peers) in the past
        if block.blockHash in nodeArray[self.executedBy].blocksSeen:
            print("Already Heard!")
            return [], []

        futureEvents = []
        cancelledEvents = []

        # If valid block then transmit to peers
        if nodeArray[self.executedBy].validate_block(self.timestamp, block, nodeArray):

             # Size of the block in KBs
            blockSize = len(block.transactions)

            # Transmitting the block to the peer nodes
            for peer in nodeArray[self.executedBy].peers.keys():

                # The receive event is created by the transmitting node, so ignoring it for Loop-Less Block forwarding
                if peer == self.createdBy:
                    continue

                # Calculating timestamp of the future event depending size of block
                future_timestamp = self.timestamp + round(nodeArray[self.executedBy].calculate_latency(blockSize, peer))

                # Adding event to receive the block at the peers
                futureEvents.append(Event(future_timestamp, self.executedBy, peer, block, ("receive", "block")))

            # Checking if the added block is now the longest chain and cancelling broadcast event in future for this node if true (Mining shifted to longest chain)
            if nodeArray[self.executedBy].status == "mining" and block.depth >= nodeArray[self.executedBy].depthOfMiningBlock:
                cancelledEvents.append(nodeArray[self.executedBy].futureBroadCastEvent)
                nodeArray[self.executedBy].status = "free"
                nodeArray[self.executedBy].futureBroadCastEvent = None
                nodeArray[self.executedBy].depthOfMiningBlock = -1

            print("Successful!")
        else:
            print("Failed! Invalid Block")

        # Adding an block creation event at same timestamp (validation event over)
        futureEvents.append(Event(self.timestamp, self.executedBy, self.executedBy, None, ("create", "block")))

        return futureEvents, cancelledEvents