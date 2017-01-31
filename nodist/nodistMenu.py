from node import NodeServer
import socket
import nodist_helper
from message import Message,MessageType
import datetime
import threading
import pickle
import configparser

class NodistMenu(object):
    '''
    Stellt das Menue von dem Programm dar.
    Beim initialisieren wird das menue ausgerufen
    '''


    def __init__(self, node_id, file, nodes_raw):
        self.nodes_raw = nodes_raw
        self.file = file
        self.node_id = node_id
        self.host, self.port = nodist_helper.getAddress(self.nodes_raw, self.node_id)
        self.runningNodes = []
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
                
        print("Nodist "+ str(node_id))
        menu_dict = dict(enumerate([("Beenden",),
                           ("lokale Node starten",self.startNode),
                           ("alle Nodes starten",self.startAllNodes),
                           ("Node beenden",self.shutdownNode),
                           ("alle Nodes beenden",self.shutdownAllNodes),
                           ("Geruecht senden",self.sendRumour),
                           ("vertraute Nachrichten",self.showTrustedMsgs),
                           ("Nachbarn ausgeben",self.sendPrintNeighbours),
                           ("ID Nachbarn Senden",self.sendIDs),
                           ("Status",self.sendStatus),
                           ("Reset",self.sendReset),
                           ("Reset all",self.sendResetAll),
                           ("graphgen",self.graphgen),
                           ("Start Testserver",self.startTestServer),
                           ("jeden Status zum Testserver", self.sendStatusServer),
                           ("beende Testserver", self.shutdownServer),
                           ("Status vom Testserver", self.statusServer)]
                               )
                     )
        
        
        
        for menu_int,menu_str in menu_dict.items():
            print(menu_int,menu_str[0])
        self.menu_int = int(input("->   :"))
        menu_choice = menu_dict.get(self.menu_int)
        print(menu_choice[0])
        if menu_choice != menu_dict[0]:
            if menu_choice != None:
                menu_choice[1]()


    
    def startNode(self):
        '''
        startet den Startknoten mit zugehoerigen Server 
        '''
        NodeServer(self.node_id,self.file)
    
    def startAllNodes(self):
        '''
        startet alle Knoten mit zugehoerigen Server 
        '''
        for node in self.nodes_raw:
            node = NodeServer(node[0], self.file)

    def shutdownNode(self):
        '''
        sendet eine Nachricht um den Startknoten zu beenden
        '''
        msg = Message(MessageType.shutdown, "Shutdown", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def shutdownAllNodes(self):
        '''
        sendet eine Nachricht zum Startknoten um alle Knoten zu beenden
        '''
        msg = Message(MessageType.shutdownAll, "Shutdown", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
   
    def sendRumour(self):
        '''
        sendet eine Geruecht zum Startknoten um es zu verbreiten
        '''
        msg = Message(MessageType.spreadRumour, "Geiz ist Geil", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def showTrustedMsgs(self):
        '''
        sendet eine Nachricht zum Startknoten um seine vertrauten Nachrichten auszugeben
        '''
        msg = Message(MessageType.trustMsg, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
        
    def sendPrintNeighbours(self):
        '''
        sendet eine Nachricht zum Startknoten um seine Nachbarn auszugeben
        '''
        msg = Message(MessageType.printNeighbours, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendIDs(self):
        '''
        sendet eine Nachricht zum Startknoten um seinen Nachbarn seine ID zu senden
        '''
        msg = Message(MessageType.sendID, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendStatus(self):
        '''
        sendet eine Nachricht zum Startknoten um seinen Status auszugeben
        '''
        msg = Message(MessageType.status, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
        
    def sendStatusServer(self):
        '''
        sendet eine Nachricht zum Startknoten um seinen Status an den Testserver zu senden
        '''
        msg = Message(MessageType.sendStatus, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)

    def statusServer(self):
        '''
        sendet eine Nachricht zum Testserver um seinen Status anauszugeben
        '''
        msg = Message(MessageType.status, "", 0, self.node_id)
        nodist_helper.sendMsg('localhost', 42222, msg)
  
   
    def sendReset(self):
        '''
        sendet eine Nachricht zum Startknoten zu resetten
        '''
        msg = Message(MessageType.reset, "", 0, self.node_id)
        nodist_helper.sendMsg(self.host, self.port, msg)
    
    def sendResetAll(self):
        '''
        sendet eine Nachricht zu allen Knoten  um sie zu resetten
        '''
        for node in self.nodes_raw:
            node_id = node[0]
            host, port = nodist_helper.getAddress(self.nodes_raw, node_id)                        
            msg = Message(MessageType.reset, "", 0, self.node_id)
            nodist_helper.sendMsg(host, port, msg)
    
    
    def graphgen(self):
        '''
        generiert einen neuen Graphen
        '''
        edges = int(input("Anzahl Kanten angeben:"))
        nodist_helper.graphgen(self.nodes_raw, edges)
        


    def testServerHandler(self, msgs, data):
        '''
        Handler um die empfangenen Daten auszuwerten
        '''
        msg = pickle.loads(data)
        #msg.printMessage()
        table = '\n'
        sum=0
        if msg.m_type == MessageType.status:
            if msgs == []:
                print("Nothing received")
            else:
                msgs_sort = sorted(msgs, key=lambda msg:msg.sender_nodeID)
                for m in msgs_sort:
                    table += '\t' + str(m.sender_nodeID)
                
                table += '\n'
                for m in msgs_sort:
                    table += '\t' + str(m.m[0])
                    sum += m.m[0]
                
                table += '\t' + str(sum)
                table += '\n'
                print(table)
                del msgs[:]
        if msg.m_type == MessageType.shutdown:
            self.TestserverOnline = False
        else:
            msgs.append(msg)
            
    

    def startTestServer(self, start=True):
        '''
        Startet einen Testserver der von allen Knoten Daten empfaengt und sie zur Auswertung ausgibt
        '''
        if start:
            start=False
            self.TestserverOnline = True
            threading.Thread(target=self.startTestServer, args=(start,)).start()
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try: 
                    host, port = self.config['DEFAULT']['Testserver'], int(self.config['DEFAULT']['TestserverPort'])
                    print("Testserver wurde gestartet:" + host +' '+ str(port))
                    sock.bind((host, port))
                    sock.listen()
                    msgs = []
                    while self.TestserverOnline:
                        conn, addr = sock.accept()
                        with conn:
                            #print("Testserver Connected b"+ str(addr))
                            data, recv_time = conn.recv(1024), datetime.datetime.now()
                            if not data: break
                            
                            
                            threading.Thread(target=self.testServerHandler, args=(msgs, data,)).start()
                            conn.close()
                            # conn.send(b'Alles klar von Node '+ bytes(str(self.ID),'utf-8'))
                finally:
                    sock.close()    
                    
                    
    def shutdownServer(self):
        '''
        beendet den testserver
        '''
        self.TestserverOnline = False
        msg = Message(MessageType.shutdown, "", 0, self.node_id)
        nodist_helper.sendMsg(self.config['DEFAULT']['Testserver'], int(self.config['DEFAULT']['TestserverPort']), msg)
