'''
Nodist Helper
Allgemeine Methoden zur Unterstuetzung fuer das Programm
'''

import pickle
import socket
import random
from graphviz import Source, Graph
from node import NodeServer
from message import Message, MessageType

def readFromFile(file): 
    '''Oeffnet eine Datei und liest node_id, host und port aus
    '''
    with open(file, 'r') as node_file:
        nodes=[]
        for s in node_file.read().splitlines():
            s=s.split()
            node_id = int(s[0])
            node_host, node_port = tuple(s[1].split(':'))
            nodes.append((node_id,(node_host, int(node_port))))
        node_file.close()
    return nodes

def sendMsgServer(host,port,m_type, msg_m, node_id):
    '''erstellt eine Message,
    erzeugt aus der Message einen picklestring
    verbindet sich mit dem angegebenen host und port
    und versendet die Nachricht
    '''
    new_msg = Message(m_type, msg_m, node_id, 0)
    pickle_string = pickle.dumps(new_msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(pickle_string)
            #data = sock.recv(1024)
        except OSError as err:
            print("TESTSERVER OS error: {0}".format(err))
        except socket.error as exc:
            print("Caught exception socket.error : ", exc)
            print("Node " + host + str(port)+  " nicht erreichbar")
        finally:
            sock.close()
            
        #print('Client Received', repr(data))

def sendMsg(host,port,msg):
    '''erzeugt aus einer Message einen picklestring
    verbindet sich mit dem angegebenen host und port
    und versendet die Nachricht
    '''
    pickle_string = pickle.dumps(msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(pickle_string)
            #data = sock.recv(1024)
        except OSError as err:
            print("OS error: {0}".format(err))
            print(" nicht erreichbar")
        except socket.error as exc:
            print("Caught exception socket.error : ", exc)
            print(host + str(port)+  " nicht erreichbar")
        finally:
            sock.close()
            
        #print('Client Received', repr(data))
    
def getAddress(nodes_raw,node_id):
    '''
    sucht fuer eine gegebene node id, den host und port aus einer Liste mit nodes_raw aus
    '''
    for node in nodes_raw:
            if (int(node[0])==node_id):
                return node[1]
    raise BaseException("node not found in file") 
    

def setRandomNeighboursToNode(nodes_raw, node, neighbour_number, file):
    '''
    sucht fuer einen Knoten zufaellige Nachbarn
    '''
    if len(nodes_raw) > (neighbour_number):

        random_ids = []
        while(neighbour_number > len(random_ids)):
            random_node = nodes_raw[random.randint(0, len(nodes_raw) - 1)]
            new_ID = random_node[0]
            if new_ID != node.ID:
                if new_ID not in random_ids:
                    random_ids.append(new_ID)
                    
                    
        for random_id in random_ids:
            for n in nodes_raw:
                if n[0] == random_id:
                    node.addNeighbourNode(NodeServer(n[0], file, start=False)) ####!!!!!!!!!!!!!!!!!!!!!!!!!

    
   


def graphFromFile(file):
    '''
    liest eine datei aus und erstellt daraus das GraphViz Objekt Source
    '''            
    with open(file, 'r') as dotfile:
        src = Source(dotfile.read())
        dotfile.close
    return src



def graphgen(nodes_raw,edges_max):
    '''
    generiert einen graphViz Graphen mit gegebenen anzahl Kanten aus einer liste mit Knoten
    gibt den graph und eine Liste mit allen nachbarn aus
    '''
    dot = Graph(comment='Nodes', format='png')
    edges_actual=0
    stNodesIDs = []
    neighbours = []
    node_id=1
    # Erst alle Knoten abdecken (erstelle auspannenden Baum)
    while(edges_actual<edges_max):
        if (edges_actual<len(nodes_raw)-1):            
            random_node_id=node_id;
            if not stNodesIDs:
                stNodesIDs.append(random_node_id)
                neighbours.append((random_node_id,node_id))
            while(random_node_id==node_id):
                random_node_id=random.randint(1, len(nodes_raw))
            if not random_node_id in stNodesIDs:
                stNodesIDs.append(random_node_id)
                neighbours.append((random_node_id,node_id))
                dot.edge(str(node_id), str(random_node_id))
                edges_actual=edges_actual+1
            node_id=random_node_id # Einruecken fuer Eulerpfad
                
        #Random anderen Knoten auffuellen        
        else:        
            node_id = random.randint(1, len(nodes_raw))
            random_node_id=node_id;
            while(random_node_id==node_id):
                random_node_id=random.randint(1, len(nodes_raw))
            if (edges_actual>=edges_max):
                break
            else:
                if not(node_id, random_node_id) in neighbours: 
                    if not(random_node_id, node_id) in neighbours:
                        dot.edge(str(node_id), str(random_node_id))
                        edges_actual=edges_actual+1
                        neighbours.append((random_node_id,node_id))
    #Source.gv generieren und Graph anzeigen         
    dot.view()
    dot.render()               
    return dot, neighbours


def getNeighboursFromGraph(graph,node_id):
    '''
    sucht aus dem Graph die Nachbarids zu einem gegeben Knoten aus
    erstellt eine Liste aller Nachbarn durch Zerlegung des Strings des Graphen
    '''
    neighbour_ids=[]
    for str in graph.source.splitlines():
        if '--' in str: 
            str1 = str.strip(';').split()
            neighbour = [int(s) for s in str1 if s.isdigit()]
            if node_id in neighbour:
                if node_id == neighbour[0]:
                    neighbour_ids.append(neighbour[1])
                else:
                    neighbour_ids.append(neighbour[0])
                    
                    
    return neighbour_ids
                    

