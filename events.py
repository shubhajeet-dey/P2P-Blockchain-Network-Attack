#!/usr/bin/env python3

class events:

    def __init__(self, eventType, timestamp, createdBy):
        self.eventType = eventType
        self.timestamp = timestamp
        self.createdBy = createdBy

    def __lt__(self,otherEvent):
        return self.timestamp < otherEvent.timestamp

