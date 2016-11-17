'''
Created on 17.11.2016

@author: Horst
'''

import socket
import multiprocessing
import datetime
import pickle
import nodist_helper
import time
from message import Message, MessageType
from builtins import bytes

class Node(object):
    '''
    classdocs
    '''


    def __init__(self, ID, neighbour=[]):
        self.ID = ID
        self.neighbour = neighbour
        self.neighboursCount = 0
   
    def printNode(self):
        print ("ID : ", self.ID)
        
    def printNeighbours(self):
        print("Neighbours from Node with ID: " , self.ID)
        for neighbour in self.neighbour:
            neighbour.printNode()


    def addNeighbourNode(self, node):
        if not node.ID in [n.ID for n in self.neighbour]:
            self.neighbour.append(node)
            self.neighboursCount += 1


class NodeServer(Node, multiprocessing.Process):
    
    def __init__(self, node_id, file, neighbour=[], start=True):
        multiprocessing.Process.__init__(self)
        Node.__init__(self, node_id, neighbour)
        self.file = file
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.online = start
        nodes = nodist_helper.readFromFile(file)
        self.host, self.port = nodist_helper.getAddress(nodes,node_id)
        
        
        if start: 
            nodist_helper.getRandomNeighbourToNode(nodes,self,3,file) ##### 
            self.start()
            
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            try: 
                print("ServerNode " + str(self.ID) + " wurde gestartet:", self.host, self.port)
                self.sock.bind((self.host, self.port))
                self.sock.listen()
                while self.online:
                    conn, addr = self.sock.accept()
                    with conn:
                        print("ServerNode " + str(self.ID) + ' Connected by', addr)
                        data, recv_time = conn.recv(1024), datetime.datetime.now()
                        if not data: break
                        conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                        print('Node ' + str(self.ID) + ' Server received Message at', recv_time)
                        msg = pickle.loads(data)
                        msg.printMessage()
                        self.handleMessages(msg, self.file)
            
            finally:
                self.sock.close()
    def closeNodeServer(self):
        self.sock.close()
        self.online = False

              
    def sendMsgToNode(self, node, msg):
        pickle_string = pickle.dumps(msg)
        pickle.loads(pickle_string)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((node.host, node.port))
                sock.sendall(pickle_string)
                data = sock.recv(1024)
            finally:
                sock.close()
                
            print('Node ' + str(self.ID) + ' Client Received', repr(data))
             
              
    def sendIDToNeighbourNodes(self):
        for node in self.neighbour:
            msg = Message(MessageType.ID, (self.ID, self.host, self.port), self.ID)
            self.sendMsgToNode(node, msg)
            
    def sendMsgToNeighbours(self,msg):
        for node in self.neighbour:
            self.sendMsgToNode(node, msg)

    def handleMessages(self, msg, file):
        if msg.m_type == MessageType.ID:
            self.addNeighbourNode(NodeServer(msg.sender_nodeID, file, start=False)) ####!!!!!!!!!!!!!!!!!!!!!!!!!
        elif msg.m_type == MessageType.sendID:
            self.sendIDToNeighbourNodes()
        elif msg.m_type == MessageType.shutdown:
            print(msg.m_type)
            self.closeNodeServer()
        elif msg.m_type == MessageType.shutdownAll:
            print(msg.m_type)
            self.sendMsgToNeighbours(msg)
            self.closeNodeServer()
        elif msg.m_type == MessageType.spreadMsg:
            print(msg.m_type)
            self.getSecret += 1
            if self.getSecret >= self.believingThreshold:
                self.believe = True
            if self.getSecret == 0:
                self.spread(msg, False)
        elif msg.m_type == MessageType.printNeighbours:
            self.printNeighbours()

              