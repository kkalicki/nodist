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
        print ("ID : ")


class NodeServer(Node, multiprocessing.Process):
    
    def __init__(self, node_id, file, neighbour=[], start=True):
        multiprocessing.Process.__init__(self)
        Node.__init__(self, node_id, neighbour)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.online = start
        nodes = nodist_helper.readFromFile(file)
        for node in nodes:
            if (int(node[0])==self.ID):
                self.host, self.port = node[1]
        if start: self.start()
            
    
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
                        #self.handleMessages(msg)
            
            finally:
                self.sock.close()
              