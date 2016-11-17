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
    spreadMsg = 2
    shutdown = 3
    shutdownAll = 4
    neighbour = 5
    printNeighbours = 6
    
class Message:
    

        msg_id=1
    
        def __init__(self, m_type, msg, sender_NodeID):
            self.msg_id = uuid.uuid4()
            self.sender_nodeID = sender_NodeID
            self.m = msg
            self.m_type = m_type
            self.m_created_at = datetime.datetime.now()
            self.m_created_from = sender_NodeID #initial
        def printMessage(self):
            print("____________________________________________________________")
            print("Message ID: " + str(self.msg_id))
            print("Message Sender NodeID: " + str(self.sender_nodeID))
            print("Message Type: " + str(self.m_type))
            print("Message: " + str(self.m))
            print("Message created at: " + str(self.m_created_at))
            print("Message created from: " + str(self.m_created_from))
            print("____________________________________________________________")