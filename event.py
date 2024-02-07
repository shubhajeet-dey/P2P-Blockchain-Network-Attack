#!/usr/bin/env python3

# Event class
class Event:
    '''
    timestamp: TimeStamp of the Event
    createdBy: The event is triggered by a parent event. Who triggered the parent event (NodeID)?
    eventType: Type of event, possible types: {"genesis block creation", "create transaction at node i", "receive transaction at node i", "create block at node i", "broadcast block at node i", "receive block at node i"}  
    '''
    def __init__(self, eventType, timestamp, createdBy):
        self.eventType = eventType
        self.timestamp = timestamp
        self.createdBy = createdBy

    def __lt__(self, otherEvent):
        return self.timestamp < otherEvent.timestamp

