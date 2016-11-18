'''
Created on 17.11.2016

@author: Horst
'''

import socket
import multiprocessing
import datetime
import pickle
import nodist_helper
from message import Message, MessageType

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
            
    def addNeighboursToNode(self, nodes, neighbour_ids, file):
        for random_id in neighbour_ids:
            for n in nodes:
                if n[0] == random_id:
                    self.addNeighbourNode(NodeServer(n[0], file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!)


class NodeServer(Node, multiprocessing.Process):
    
    def __init__(self, node_id, file, neighbour=[], graph_file=None, start=True):
        multiprocessing.Process.__init__(self)
        Node.__init__(self, node_id, neighbour)
        
        self.online = start
        self.file = file
        self.getSecret = 0
        self.believe = False
        self.believingThreshold = 4
        self.last_status_print = datetime.datetime.now() + datetime.timedelta(minutes=-1)
        self.last_reset = datetime.datetime.now() + datetime.timedelta(minutes=-1)
        
        nodes = nodist_helper.readFromFile(file)
        self.host, self.port = nodist_helper.getAddress(nodes, node_id)
        
        if start: 
            graph = nodist_helper.graphFromFile('Graph.gv')
            # graph.view()
            # new_graph = nodist_helper.graphgen(nodes, 40)[0]
            # new_graph.view()
            # new_graph.render()
            neighbour_ids = nodist_helper.getNeighboursFromGraph(graph, self.ID)
            self.addNeighboursToNode(nodes, neighbour_ids, file)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #nodist_helper.getRandomNeighbourToNode(nodes,self,3,file) ##### 
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
                        # conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                        print('Node ' + str(self.ID) + ' Server received Message at', recv_time)
                        msg = pickle.loads(data)
                        #msg.printMessage()
                        self.handleMessages(msg, self.file)
            
            finally:
                self.sock.close()
    
    def closeNodeServer(self):
        self.online = False
        self.sock.close()
        
    def printNode(self):
        print ("ID : ", self.ID, " host : ", self.host, " PORT :", self.port)


              
    def sendMsgToNode(self, node, msg):
        pickle_string = pickle.dumps(msg)
        pickle.loads(pickle_string)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((node.host, node.port))
                sock.sendall(pickle_string)
                # data = sock.recv(1024)
            except OSError as err:
                print("OS error: {0}".format(err))
            except socket.error as exc:
                print("Caught exception socket.error : ", exc)
                print("Node " + node.ID + " nicht erreichbar")
            finally:
                sock.close()
                
            # print('Node ' + str(self.ID) + ' Client Received', repr(data))
             
              
    def sendIDToNeighbourNodes(self):
        for node in self.neighbour:
            msg = Message(MessageType.ID, (self.ID, self.host, self.port), self.ID)
            self.sendMsgToNode(node, msg)
            
    def sendMsgToNeighbours(self, msg, sender=False):
        if sender:
            for node in self.neighbour:
                self.sendMsgToNode(node, msg)
        else:
            self.spread(msg) 
            
            
    def spread(self, msg):
        for node in self.neighbour:
            if not node.ID == msg.sender_nodeID:
                self.sendMsgToNode(node, msg)

    def handleMessages(self, msg, file):
        if msg.m_type == MessageType.ID:
            self.addNeighbourNode(NodeServer(msg.sender_nodeID, file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!
        
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
            if msg.sender_nodeID == 0:
                msg.sender_nodeID = self.ID

            if self.getSecret == 0: self.spread(msg)   
                         
            if self.getSecret >= self.believingThreshold:
                self.believe = True
                print("Glaube das Geruecht")
            self.getSecret += 1
                
        elif msg.m_type == MessageType.status:
            diff = datetime.datetime.now() - self.last_status_print
            if diff.total_seconds() > 5:
                print("Status:")
                self.printNode()
                print ("geruecht gehoert: ", self.getSecret)
                if self.believe: print ("Ich glaube das Geruecht")
                self.spread(msg)
                self.last_status_print = datetime.datetime.now()
            else:
                print("Statusnachricht nur alle 5 Sekunden")
        
        elif msg.m_type == MessageType.reset:
            diff = datetime.datetime.now() - self.last_reset
            if diff.total_seconds() > 5:
                self.getSecret=0
                self.believe=False
                print("reset done....")
                
        elif msg.m_type == MessageType.printNeighbours:
            self.printNeighbours()

              
