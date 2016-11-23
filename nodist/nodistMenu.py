'''
Created on 22.11.2016

@author: Horst
'''

from node import NodeServer,Node
import socket
import nodist_helper
from message import Message,MessageType
import datetime
import threading
from node_window import NodeWindow
import pickle
import time

class NodistMenu(object):
    '''
    classdocs
    '''


    def __init__(self, node_id, file, nodes_raw):
        self.nodes_raw = nodes_raw
        self.file = file
        self.node_id = node_id
        self.host, self.port = nodist_helper.getAddress(self.nodes_raw, self.node_id)
                
        print("Nodist "+ str(node_id))
        menu_dict = dict(enumerate([("Beenden",None),
                           ("lokale Node starten",self.startNode),
                           ("alle Nodes starten",self.startAllNodes),
                           ("Node beenden",self.shutdownNode),
                           ("alle Nodes beenden",self.shutdownAllNodes),
                           ("Geruecht senden",self.sendRumour),
                           ("Nachbar",self.sendPrintNeighbours),
                           ("ID Nachbarn Senden",self.sendIDs),
                           ("Status",self.sendStatus),
                           ("Reset",self.sendReset),
                           ("Reset all",self.sendResetAll),
                           ("graphfile",self.getGraphFile),
                           ("graphgen",self.graphgen),
                           ("Start Testserver",self.startTestServer),
                           ("Sende jeden Status zum Testserver", self.sendStatusServer),
                           ("Start Tests",self.startTests)]
                               )
                     )
        
        
        
        for menu_int,menu_str in menu_dict.items():
            print(menu_int,menu_str[0])
        self.menu_int = int(input("->   :"))
        menu_choice = menu_dict.get(self.menu_int)
        print(menu_choice[0])
        if menu_choice != None:
            menu_choice[1]()

    
    def startNode(self):
        NodeServer(self.node_id,self.file)
    
    def startAllNodes(self):
        
        for node in self.nodes_raw:
            node = NodeServer(node[0], self.file)
    def startAllNodesTests(self, file, nodes_raw):
        
        for node in nodes_raw:
            node = NodeServer(node[0], file)
    
    def shutdownNode(self):
        msg = Message(MessageType.shutdown, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def shutdownAllNodes(self):
        msg = Message(MessageType.shutdownAll, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendRumour(self):
        msg = Message(MessageType.spreadMsg, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendPrintNeighbours(self):
        msg = Message(MessageType.printNeighbours, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendIDs(self):
        msg = Message(MessageType.sendID, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendStatus(self):
        msg = Message(MessageType.status, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
        
    def sendStatusServer(self):
        msg = Message(MessageType.sendStatus, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendReset(self):
        msg = Message(MessageType.reset, "Geiz ist Geil", 0)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendResetAll(self):
        for node in self.nodes_raw:
            node_id = node[0]
            host, port = nodist_helper.getAddress(self.nodes_raw, node_id)                        
            msg = Message(MessageType.reset, "Geiz ist Geil", 0)
            nodist_helper.sendMsg(host, port, msg)
    
    
    def getGraphFile(self):
        pass
    
    def graphgen(self):
        nodist_helper.graphgen(self.nodes_raw, 10)
    
    def startTests(self):
        self.startTestServer()
        file = 'data5'
        nodes_raw = nodist_helper.readFromFile(file)
        m_max = (len(nodes_raw) * (len(nodes_raw)-1))/2
        #nodist_helper.graphgen(nodes_raw, m_max)
        time.sleep(1)
        new_msg = Message(MessageType.startTest,(1,len(nodes_raw)),0)
        nodist_helper.sendMsg('localhost', 42222, new_msg)
        time.sleep(1)
        self.startAllNodesTests(file, nodes_raw)
        
        time.sleep(20)
        self.sendRumour()
        time.sleep(40)
        self.sendStatusServer()
        time.sleep(40)
        self.shutdownAllNodes()
        time.sleep(1)

    
    def startTestServer(self, start=True):
        if start:
            start=False
            threading.Thread(target=self.startTestServer, args=(start,)).start()
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try: 
                    host, port = 'localhost', 42222
                    node_window= NodeWindow()
                    node_window.add("Testserver wurde gestartet:" + host +' '+ str(port))
                    sock.bind((host, port))
                    sock.listen()
                    test_rslt = {}
                    count=0
                    length = 1000
                    while True:
                        conn, addr = sock.accept()
                        with conn:
                            node_window.add("Testserver Connected b"+ str(addr))
                            data, recv_time = conn.recv(1024), datetime.datetime.now()
                            if not data: break
                            msg = pickle.loads(data)
                            #msg.printMessage()
                            if msg.m_type == MessageType.startTest:
                                count=0
                                test = msg.m[0]
                                length = msg.m[1]
                                test_rslt = {}
                            if msg.m_type == MessageType.sendStatus:
                                test_rslt[msg.sender_nodeID]=msg.m
                                #node_window.add(str(msg.m))
                            if len(test_rslt) == length:
                                node_window.add(str(test_rslt))                            
                                
                            # conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                finally:
                    sock.close()    
