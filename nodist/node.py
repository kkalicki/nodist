import socket
import multiprocessing
import datetime
import pickle  # helper
import nodist_helper
import threading
from message import Message, MessageType, NodeMessage
from multiprocessing import Queue
import configparser


class Node(object):
    '''
    Oberklasse Node besteht aus einer ID und hat Nachbarn 
    '''

    def __init__(self, ID):
        self.ID = ID
        self.neighbour = []
   
    def printNode(self):
        print("ID : ", self.ID)
        
    def printNeighbours(self):
        print("Neighbours from Node with ID: " , self.ID)
        for neighbour in self.neighbour:
            neighbour.printNode()


    def addNeighbourNode(self, node):
        '''
        fuegt einen Nachbarn hinzu, wenn er noch kein Nachbar ist
        '''
        if not node.ID in [n.ID for n in self.neighbour]:
            self.neighbour.append(node)
            
    def addNeighboursToNode(self, nodes, neighbour_ids, file):
        '''
        fuegt Nachbarn hinzu aus einer Liste hinzu
        '''
        for random_id in neighbour_ids:
            for n in nodes:
                if n[0] == random_id:
                    self.addNeighbourNode(NodeServer(n[0], file, start=False))  ####!!!!!!!!!!!!!!!!!!!!!!!!!)



class NodeServer(Node, multiprocessing.Process):
    '''
    erbt von Node und multiprocessing.Process
    startet einen eigenen Prozess wenn start=True ist
    wird erweitert um host und port um gegebenfalls einen Server im neuen Prozess zu starten
    liest seine Nachbarn durch die Graph_file aus
    speichert alle Nachrichten die Empfangen werden in einer Liste ab
    '''
    

    def __init__(self, node_id, file, start=True):
        multiprocessing.Process.__init__(self, daemon=True)
        Node.__init__(self, node_id)
        
        self.nodes_raw = nodist_helper.readFromFile(file)
        self.host, self.port = nodist_helper.getAddress(self.nodes_raw, node_id)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.graph_file=self.config['DEFAULT']['Graphfile']
        if start: 
            self.messages = []
            self.online = start
            self.file = file
            self.trusted_messages = []
            #nodist_helper.getRandomNeighbourToNode(nodes_raw,self,3,file) ##### 
            self.setNeighbours(self.graph_file,file)
            self.start()
            
    #startet neuen Prozess
    def run(self):
            try: 
                
                # print("ServerNode " + str(self.ID) + " wurde gestartet:" + self.host + str(self.port))
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.msg_queue = Queue()
                #for i in range(3):
                worker = threading.Thread(target=self.startQueue, args=(self.msg_queue,))
                worker.setDaemon(True)
                worker.start()
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
                        
                        threading.Thread(target=self.handleRequest, args=(data,)).start()
                        conn.close()
            except OSError as err:
                print("Node Server" + str(self.ID) + "OS error: {0}".format(err))
            except socket.error as exc:
                print("Caught exception socket.error : " + str(exc))
            finally:
                self.sock.close()
                self.online = False
    
    def closeNodeServer(self):
        '''
        schliesst den socket
        '''
        self.online = False
        # Trick 17 :)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        
    def setNeighbours(self, graph_file,file):
        '''
        sucht die Nachbarn aus der Graphfile aus und speichert sie im Knoten ab
        '''
        graph = nodist_helper.graphFromFile(graph_file)
        neighbour_ids = nodist_helper.getNeighboursFromGraph(graph, self.ID)
        self.addNeighboursToNode(self.nodes_raw, neighbour_ids, file)

        
    def printNeighbours(self):
        print("Neighbours (" + str(len(self.neighbour)) + ") from Node with ID: " + str(self.ID))
        for neighbour in self.neighbour:
            neighbour.printNode()
            
            
    def printNode(self):
        print("ID : " + str(self.ID) + " host : " + self.host + " PORT :" + str(self.port))


              
    def sendMsgToNode(self, node, msg):
        '''
        sendet eine Message
        Sender und Empfaenger der Nachricht werden aktualisiert
        nachricht als picklestring verpackt und an den angegebenen Knoten versendet
        schickt die Nachricht wieder in die Queue wenn sie nicht versendet werden konnte
        
        '''
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
                msg.sent += 1
                if msg.sent < 5: 
                    self.msg_queue.put(msg)
                else:
                    print("Caught exception socket.error : " + str(err))
                    print("Node Client" + str(node.ID) + " nicht erreichbar")
                if msg.sent < 5: self.msg_queue.put(msg)
            except socket.error as exc:
                msg.sent += 1
                if msg.sent < 5: 
                    self.msg_queue.put(msg)
                else:
                    print("Caught exception socket.error : " + str(err))
                    print("Node Client" + str(node.ID) + " nicht erreichbar")
            finally:
                sock.close()
                
            # print('Node ' + str(self.ID) + ' Client Received', repr(data))
             
              
    def sendIDToNeighbourNodes(self):
        '''
        sendet die ID an alle Nachbarn
        '''
        for node in self.neighbour:
            msg = Message(MessageType.ID, (self.ID, self.host, self.port), self.ID, node.ID)
            self.sendMsgToNode(node, msg)
            
         
    def spread(self, msg):
        '''
        sendet an alle Nachbarn eine Nachricht ausser an den Nachbarn, 
        von dem man die Nachricht bekommen hat
        '''
        for node in self.neighbour:
            if not node.ID == msg.recieved_from:
                self.sendMsgToNode(node, msg.msg)
                
    def startQueue(self, msg_queue):
        '''
        Worker der als Deamon die Queue abarbeitet, 
        endet mit dem Mainthread
        '''
        while True:
            msg = msg_queue.get()
            self.handleMessage(msg)
            # msg_queue.task_done()

    def handleRequest(self, data):
        '''
        Bearbeitet die empfangenen Daten
        decodiert sie zur Message
        haengt nachricht in die Queue an zum abarbeiten,
        wenn sie nicht schonmal empfangen wurde        
        '''
        msg = pickle.loads(data)
        msg.sent = 0
        # msg.printMessage()
        found = False
        
        for node_message in self.messages:
            if msg == node_message.msg:
                found = True
                node_message.counter += 1
                if msg.m_type == MessageType.spreadRumour:
                    if node_message.counter == int(self.config['DEFAULT']['BelievingTreshould']):
                        if not node_message in self.trusted_messages:
                            self.trusted_messages.append(node_message)
                break
            
        if found == False:
            node_msg = NodeMessage(msg)
            self.messages.append(node_msg)
            
            '''
            self.messages.append(NodeMessage(msg))
            for node_message in self.messages:
                if msg == node_message.msg:
                    msg = node_message
                    break  
            '''    
            if node_msg.msg.m_type == MessageType.sendStatus:
                for node_message in self.messages:
                    if node_message.msg.m_type == MessageType.spreadRumour:
                        node_msg.msg.m = (node_message.counter, len(self.neighbour))
                        break
                    
            '''
            if node_msg.msg.m_type == MessageType.newNeighbour:
                self.messages = []
                self.neighbour = []
                self.setNeighbours(msg.msg.m, self.file)
            '''
            if node_msg.msg.m_type == MessageType.printNeighbours:
                self.printNeighbours()
                
            if node_msg.msg.m_type == MessageType.reset:
                self.trusted_messages=[]
                self.messages = []
                self.messages.append(node_msg)
            else:
                self.msg_queue.put(node_msg)

            
            
    def handleMessage(self, msg):
        '''
        Reagiert auf die eingegangende Message
        fuehrt eine Funktion entsprechend des Nachrichtentyps aus
        '''
        if isinstance(msg, Message):  # Sendet erneut eine Message, da sie nicht versendet werden konnte
            self.sendMsgToNode(NodeServer(msg.receiver_nodeID, self.file, start=False), msg)
        
        
        elif msg.msg.m_type == MessageType.sendID:
            self.sendIDToNeighbourNodes()
            
        elif msg.msg.m_type == MessageType.shutdown:
            self.closeNodeServer()
            
        elif msg.msg.m_type == MessageType.shutdownAll:
            self.spread(msg)
            self.closeNodeServer()
            
        elif msg.msg.m_type == MessageType.spreadRumour:
            self.spread(msg)   
                
        elif msg.msg.m_type == MessageType.status:
            print("Status:")
            self.printNode()
            
        elif msg.msg.m_type == MessageType.trustMsg:
            print("vertraute Nachrichten:")
            for t_msg in self.trusted_messages:
                t_msg.msg.printMessage()
        

        elif msg.msg.m_type == MessageType.sendStatus:
                nodist_helper.sendMsgServer(self.config['DEFAULT']['Testserver'], int(self.config['DEFAULT']['TestserverPort']), msg.msg.m_type, msg.msg.m, self.ID)
                self.spread(msg)
