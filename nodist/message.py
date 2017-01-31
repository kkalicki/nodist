import datetime
from enum import Enum
import uuid

class MessageType(Enum):
    '''
    Enumeration for message types
    '''
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
    newNeighbour=11
    trustMsg=12
    
class Message:
    '''
    Eine Message hat eine einzigartige UUID die nicht veraendert wird.
    Alle Daten die ausgetauscht werden sind Messages
    '''
    def __init__(self, m_type, msg, sender_NodeID, receiver_NodeID):
            self.msg_id = uuid.uuid4()
            self.m = msg
            self.m_type = m_type
            self.sender_nodeID = sender_NodeID
            self.receiver_nodeID = receiver_NodeID
            self.m_created_at = datetime.datetime.now() #initial
            self.m_created_from = sender_NodeID #initial
            self.sent = 0
            
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
    '''
    Messages werden von einem Knoten als NodeMessages abgespeichert
    '''
    def __init__(self, msg, counter=1):
        self.msg = msg
        self.counter = counter
        self.nm_created_at = datetime.datetime.now() #initial
        self.recieved_from = msg.sender_nodeID #initial
        
    def __str__(self):
        return str(self.__dict__)    
    