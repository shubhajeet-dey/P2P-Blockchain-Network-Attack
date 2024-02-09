#!/usr/bin/env python3
from transactions import TXN
from block import Block

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
        "broadcast transaction at node i" --> ("broadcast", "TXN")
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
        if eventType[0] == "genesis":
            self.create_genisis_block(nodeArray)

        elif eventType[0] == "create":
            if eventType[1] == "TXN":
                self.create_transaction(nodeArray)
            else:
                self.create_block(nodeArray)

        elif eventType[0] == "broadcast":
            if eventType[1] == "TXN":
                self.broadcast_transaction(nodeArray)
            else:
                self.broadcast_block(nodeArray)

        else:
            if eventType[1] == "TXN":
                self.receive_transaction(nodeArray)
            else:
                self.receive_block(nodeArray)

    # Create genisis block
    # def create_genisis_block(self, nodeArray):


