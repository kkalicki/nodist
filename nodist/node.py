'''
Created on 17.11.2016

@author: Horst
'''

import socket
import multiprocessing
import datetime
import pickle#helper
import nodist_helper
from message import Message, MessageType
from node_window import NodeWindow

class Node(object):
    '''
    classdocs
    '''


    def __init__(self, ID):
        self.ID = ID
        self.neighbour = []
        self.neighboursCount = 0
   
    def printNode(self):
        print("ID : ", self.ID)
        
    def printNeighbours(self):
        print("Neighbours from Node with ID: " , self.ID)
        for neighbour in self.neighbour:
            neighbour.printNode()


    def addNeighbourNode(self, node):
        if self.ID == node.ID:
            print('kacke')
        if not node.ID in [n.ID for n in self.neighbour]:
            self.neighbour.append(node)
            self.neighboursCount += 1
            
    def addNeighboursToNode(self, nodes, neighbour_ids, file):
        for random_id in neighbour_ids:
            for n in nodes:
                if n[0] == random_id:
                    self.addNeighbourNode(NodeServer(n[0], file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!)


class NodeServer(Node, multiprocessing.Process):
    
    def __init__(self, node_id, file, graph_file='Graph.gv', start=True):
        multiprocessing.Process.__init__(self)
        Node.__init__(self, node_id)
        self.graph_file=graph_file
        self.online = start
        self.file = file
        self.getSecret = 0
        self.heard_from = []
        self.believe = False
        self.believingThreshold = 4
        self.last_status_print = datetime.datetime.now() + datetime.timedelta(minutes=-1)
        self.last_reset = datetime.datetime.now() + datetime.timedelta(minutes=-1)
        
        nodes_raw = nodist_helper.readFromFile(file)
        self.host, self.port = nodist_helper.getAddress(nodes_raw, node_id)
        
        if start: 
            graph = nodist_helper.graphFromFile(self.graph_file)
            # graph.view()
            # new_graph = nodist_helper.graphgen(nodes_raw, 40)[0]
            # new_graph.view()
            # new_graph.render()
            neighbour_ids = nodist_helper.getNeighboursFromGraph(graph, self.ID)
            self.addNeighboursToNode(nodes_raw, neighbour_ids, file)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #nodist_helper.getRandomNeighbourToNode(nodes_raw,self,3,file) ##### 
            self.start()
            
    
    def run(self):
            try: 
                node_window= NodeWindow()
                node_window.add("ServerNode " + str(self.ID) + " wurde gestartet:" + self.host + str(self.port))
                self.sock.bind((self.host, self.port))
                self.sock.listen()
                while self.online:
                    conn, addr = self.sock.accept()
                    with conn:
                        node_window.add("ServerNode " + str(self.ID) + ' Connected by' + str(addr))
                        data, recv_time = conn.recv(1024), datetime.datetime.now()
                        if not data: break
                        # conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                        node_window.add('Node ' + str(self.ID) + ' Server received Message at ' + str(recv_time))
                        msg = pickle.loads(data)
                        #msg.printMessage()
                        #if msg.m_created_from == 0: msg.m_created_from =self.ID
                        self.handleMessages(msg, self.file, node_window)
            except OSError as err:
                node_window.add("OS error: {0}".format(err))
            except socket.error as exc:
                node_window.add("Caught exception socket.error : " + str(exc))
            finally:
                self.sock.close()
    
    def closeNodeServer(self):
        self.online = False
        self.sock.close()
        
    def printNeighbours(self, node_window):
        node_window.add("Neighbours from Node with ID: " + str(self.ID))
        for neighbour in self.neighbour:
            neighbour.printNode(node_window)
            
    def printNode(self,node_window):
        node_window.add("ID : "+ str(self.ID)+" host : "+ self.host + " PORT :"+ str(self.port))


              
    def sendMsgToNode(self, node, m_type, msg_m, node_window):
        new_msg = Message(m_type, msg_m, self.ID)
        pickle_string = pickle.dumps(new_msg)
        pickle.loads(pickle_string)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((node.host, node.port))
                sock.sendall(pickle_string)
                # data = sock.recv(1024)
            except OSError as err:
                node_window.add("OS error: {0}".format(err))
            except socket.error as exc:
                node_window.add("Caught exception socket.error : " + str(exc))
                node_window.add("Node " + node.ID + " nicht erreichbar")
            finally:
                sock.close()
                
            # print('Node ' + str(self.ID) + ' Client Received', repr(data))
             
              
    def sendIDToNeighbourNodes(self, node_window):
        for node in self.neighbour:
            self.sendMsgToNode(node, MessageType.ID, (self.ID, self.host, self.port), node_window)
            
         
    def spread(self, msg,msg_m,node_window):
        for node in self.neighbour:
            if not node.ID == msg.sender_nodeID:
                self.sendMsgToNode(node, msg.m_type,msg_m, node_window)

    def handleMessages(self, msg, file, node_window):
        #if msg.m_type == MessageType.ID:
            #self.addNeighbourNode(NodeServer(msg.sender_nodeID, file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!
        
        if msg.m_type == MessageType.sendID:
            self.sendIDToNeighbourNodes(node_window)
            
        elif msg.m_type == MessageType.shutdown:
            node_window.add(str(msg.m_type))
            self.closeNodeServer()
            
        elif msg.m_type == MessageType.shutdownAll:
            node_window.add(msg.m_type)
            self.spread(msg, msg.m, node_window)
            self.closeNodeServer()
            
        elif msg.m_type == MessageType.spreadMsg:

            if self.getSecret == 0: 
                self.spread(msg,msg.m, node_window)   
            if self.getSecret >= self.believingThreshold:
                self.believe = True
                node_window.add("Glaube das Geruecht")
            self.heard_from.append(msg.sender_nodeID)       
            self.getSecret += 1
                
        elif msg.m_type == MessageType.status:
            diff = datetime.datetime.now() - self.last_status_print
            if diff.total_seconds() > 5:
                node_window.add("Status:")
                self.printNode(node_window)
                node_window.add("geruecht gehoert: " + str(self.getSecret))
                node_window.add(''.join(str(nid) for nid in self.heard_from))
                if self.believe: node_window.add("Ich glaube das Geruecht")
                self.spread(msg,msg.m, node_window)
                self.last_status_print = datetime.datetime.now()
            else:
                node_window.add("Statusnachricht nur alle 5 Sekunden")
        
        elif msg.m_type == MessageType.reset:
            diff = datetime.datetime.now() - self.last_reset
            if diff.total_seconds() > 5:
                self.getSecret=0
                self.believe=False
                node_window.add("reset done....")
                
        elif msg.m_type == MessageType.printNeighbours:
            self.printNeighbours(node_window)
            
        elif msg.m_type == MessageType.sendStatus:
            diff = datetime.datetime.now() - self.last_status_print
            if diff.total_seconds() > 20:
                
                self.spread(msg,msg.m,node_window)
                nn_ids = [n.ID for n in self.neighbour]
                nodist_helper.sendMsgServer('localhost', 42222, msg.m_type,self.getSecret,self.ID, node_window)
                self.last_status_print = datetime.datetime.now()
            else:
                node_window.add("senden der Statusnachricht an testserver nur alle 20 Sekunden")  
