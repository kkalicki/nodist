'''
Created on 28.10.2016

@author: Horst
'''
import datetime
from enum import Enum
import uuid

class MessageType(Enum):
    ID = 0
    sendID = 1
    spreadRumour = 2
    shutdown = 3
    shutdownAll = 4
    neighbour = 5
    printNeighbours = 6
    status = 7
    reset = 8
    sendStatus=9
    startTest=10
    
class Message:

        def __init__(self, m_type, msg, sender_NodeID, receiver_NodeID):
            self.msg_id = uuid.uuid4()
            self.sender_nodeID = sender_NodeID
            self.receiver_nodeID = receiver_NodeID
            self.m = msg
            self.m_type = m_type
            self.m_created_at = datetime.datetime.now() #initial
            self.m_created_from = sender_NodeID #initial
            
        def __eq__(self, other):
            return self.msg_id == other.msg_id
        
        def __str__(self):
            return str(self.__dict__)
            
            
        def printMessage(self):
            print("____________________________________________________________")
            print("Message ID: " + str(self.msg_id))
            print("Message Sender NodeID: " + str(self.sender_nodeID))
            print("Message Receiver NodeID: " + str(self.receiver_nodeID))
            print("Message Type: " + str(self.m_type))
            print("Message: " + str(self.m))
            print("Message created at: " + str(self.m_created_at))
            print("Message created from: " + str(self.m_created_from))
            print("____________________________________________________________")
            
            
class NodeMessage:
    def __init__(self, msg, counter=1):
        self.msg = msg
        self.counter = counter
        self.nm_created_at = datetime.datetime.now() #initial
        self.recieved_from = msg.sender_nodeID #initial
        
    def __str__(self):
        return str(self.__dict__)    
    