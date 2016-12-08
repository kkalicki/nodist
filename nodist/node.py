'''
Created on 17.11.2016

@author: Horst
'''

import socket
import multiprocessing
import datetime
import pickle  # helper
import nodist_helper
import threading
from message import Message, MessageType, NodeMessage
from multiprocessing import Queue

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
        if not node.ID in [n.ID for n in self.neighbour]:
            self.neighbour.append(node)
            self.neighboursCount += 1
            
    def addNeighboursToNode(self, nodes, neighbour_ids, file):
        for random_id in neighbour_ids:
            for n in nodes:
                if n[0] == random_id:
                    self.addNeighbourNode(NodeServer(n[0], file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!)


class NodeServer(Node, multiprocessing.Process):
    
    def __init__(self, node_id, file, graph_file='Graph.gv', start=True, believingThreshold=4):
        multiprocessing.Process.__init__(self)
        Node.__init__(self, node_id)
        self.messages = []
        self.msg_queue = Queue()
        self.graph_file = graph_file
        self.online = start
        self.file = file
        self.believe = False
        self.believingThreshold = believingThreshold
        for i in range(20):
            worker = threading.Thread(target=self.startQueue, args=(self.msg_queue,))
            worker.setDaemon(True)
            worker.start()
        # threading.Thread(self.startQueue, args=(self.msg_queue,)).start()
        
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
                # print("ServerNode " + str(self.ID) + " wurde gestartet:" + self.host + str(self.port))
                self.sock.bind((self.host, self.port))
                self.sock.listen()
                while self.online:
                    conn, addr = self.sock.accept()
                    with conn:
                        # print("ServerNode " + str(self.ID) + ' Connected by' + str(addr))
                        data, recv_time = conn.recv(1024), datetime.datetime.now()
                        if not data: break
                        # conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                        # print('Node ' + str(self.ID) + ' Server received Message at ' + str(recv_time))
                        
                        # msg.printMessage()
                        # if msg.m_created_from == 0: msg.m_created_from =self.ID
                        # self.handleMessage(msg)
                        threading.Thread(target=self.handleRequest, args=(data,)).start()
                        conn.close()
            except OSError as err:
                print("Node Server"+str(self.ID)+"OS error: {0}".format(err))
            except socket.error as exc:
                print("Caught exception socket.error : " + str(exc))
            finally:
                self.sock.close()
    
    def closeNodeServer(self):
        self.online = False
        self.sock.close()
        
    def printNeighbours(self):
        print("Neighbours ("+str(len(self.neighbour))+") from Node with ID: " + str(self.ID))
        for neighbour in self.neighbour:
            neighbour.printNode()
            
            
    def printNode(self):
        print("ID : " + str(self.ID) + " host : " + self.host + " PORT :" + str(self.port))


              
    def sendMsgToNode(self, node, msg):
        msg.sender_nodeID = self.ID
        msg.receiver_nodeID = node.ID
        

        pickle_string = pickle.dumps(msg)
        pickle.loads(pickle_string)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((node.host, node.port))
                sock.sendall(pickle_string)
                # data = sock.recv(1024)
            except OSError as err:
                print("Node Client "+str(self.ID)+" OS error: {0}".format(err))
                print("Node " + str(node.ID) + " nicht erreichbar")
            except socket.error as exc:
                print("Caught exception socket.error : " + str(exc))
                print("Node " + str(node.ID) + " nicht erreichbar")
            finally:
                sock.close()
                
            # print('Node ' + str(self.ID) + ' Client Received', repr(data))
             
              
    def sendIDToNeighbourNodes(self):
        for node in self.neighbour:
            msg = Message(MessageType.ID, (self.ID, self.host, self.port), self.ID, node.ID)
            self.sendMsgToNode(node, msg)
            
         
    def spread(self, msg):
        for node in self.neighbour:
            if not node.ID == msg.recieved_from:
                self.sendMsgToNode(node, msg.msg)
                
    def startQueue(self, msg_queue):
        """This is the worker thread function.
        It processes items in the queue one after
        another.  These daemon threads go into an
        infinite loop, and only exit when
        the main thread ends.
        """
        while True:
            msg = msg_queue.get()
            self.handleMessage(msg)
            # msg_queue.task_done()

    def handleRequest(self, data):
        msg = pickle.loads(data)
        found = False
        for node_message in self.messages:
            if msg == node_message.msg:
                node_message.counter += 1
                found = True
                break
        if found == False:
            self.messages.append(NodeMessage(msg))
            for node_message in self.messages:
                if msg == node_message.msg:
                    msg=node_message
                    break  
                
            if msg.msg.m_type == MessageType.sendStatus:
                for node_message in self.messages:
                    if node_message.msg.m_type == MessageType.spreadRumour:
                        msg.msg.m = (node_message.counter, len(self.neighbour))
                        break
                 
            self.msg_queue.put(msg)

            
            
    def handleMessage(self, msg):
        # if msg.m_type == MessageType.ID:
            #self.addNeighbourNode(NodeServer(msg.sender_nodeID, file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!
        
        if msg.msg.m_type == MessageType.sendID:
            self.sendIDToNeighbourNodes()
            
        elif msg.msg.m_type == MessageType.shutdown:
            print(str(self.ID) + str(msg.msg.m_type))
            self.closeNodeServer()
            
        elif msg.msg.m_type == MessageType.shutdownAll:
            print(msg.msg.m_type)
            self.spread(msg)
            self.closeNodeServer()
            
        elif msg.msg.m_type == MessageType.spreadRumour:
            self.spread(msg)   
                
        elif msg.msg.m_type == MessageType.status:
            print("Status:")
            self.printNode()
        
        elif msg.msg.m_type == MessageType.reset:
            self.messages = []
            self.messages.append(NodeMessage(msg))
            print("reset done....")
                
        elif msg.msg.m_type == MessageType.printNeighbours:
            self.printNeighbours()
            
        elif msg.msg.m_type == MessageType.sendStatus:
                nodist_helper.sendMsgServer('localhost', 42222, msg.msg.m_type, msg.msg.m, self.ID)
                self.spread(msg)
                
        #if not message sent queue put
