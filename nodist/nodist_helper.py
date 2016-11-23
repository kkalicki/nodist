'''
Created on 17.11.2016

@author: Horst
'''

import pickle
import socket
import random
from graphviz import Source, Graph
from node import NodeServer
from message import Message, MessageType

def readFromFile(file):            
    with open(file, 'r') as node_file:
        nodes=[]
        for s in node_file.read().splitlines():
            s=s.split()
            node_id = int(s[0])
            node_host, node_port = tuple(s[1].split(':'))
            nodes.append((node_id,(node_host, int(node_port))))
        node_file.close()
    return nodes

def sendMsgServer(host,port,m_type, msg_m, node_id, node_window):
    new_msg = Message(m_type, msg_m, node_id)
    pickle_string = pickle.dumps(new_msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(pickle_string)
            #data = sock.recv(1024)
        except OSError as err:
            node_window.add("OS error: {0}".format(err))
        except socket.error as exc:
            node_window.add("Caught exception socket.error : ", exc)
            node_window.add("Node " + host + str(port)+  " nicht erreichbar")
        finally:
            sock.close()
            
        #print('Client Received', repr(data))

def sendMsg(host,port,msg):
    pickle_string = pickle.dumps(msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(pickle_string)
            #data = sock.recv(1024)
        except OSError as err:
            print("OS error: {0}".format(err))
        except socket.error as exc:
            print("Caught exception socket.error : ", exc)
            print("Node " + host + str(port)+  " nicht erreichbar")
        finally:
            sock.close()
            
        #print('Client Received', repr(data))
    
def getAddress(nodes,node_id):
    for node in nodes:
            if (int(node[0])==node_id):
                return node[1]
    

def getRandomNeighbourToNode(nodes, node, neighbour_number, file):
    if len(nodes) > (neighbour_number):

        random_ids = []
        while(neighbour_number > len(random_ids)):
            random_node = nodes[random.randint(0, len(nodes) - 1)]
            new_ID = random_node[0]
            if new_ID != node.ID:
                if new_ID not in random_ids:
                    random_ids.append(new_ID)
                    
                    
        for random_id in random_ids:
            for n in nodes:
                if n[0] == random_id:
                    node.addNeighbourNode(NodeServer(n[0], file, start=False)) ####!!!!!!!!!!!!!!!!!!!!!!!!!

    
   


def graphFromFile(file):            
    with open(file, 'r') as dotfile:
        src = Source(dotfile.read())
        dotfile.close
    return src



def graphgen(nodes_raw,edges_max):
    dot = Graph(comment='Nodes', format='png')
    edges_actual=0
    stNodesIDs = []
    neighbours = []
    node_id=1
    while(edges_actual<edges_max):
        if (edges_actual<len(nodes_raw)-1):            
            j=node_id;
            if not stNodesIDs:
                stNodesIDs.append(j)
                neighbours.append((j,node_id))
            while(j==node_id):
                j=random.randint(1, len(nodes_raw))
            if not j in stNodesIDs:
                stNodesIDs.append(j)
                neighbours.append((j,node_id))
                dot.edge(str(node_id), str(j))
                edges_actual=edges_actual+1
            node_id=j # Einruecken fuer Eulerpfad
                
                
        else:        
            node_id = random.randint(1, len(nodes_raw))
            j=node_id;
            while(j==node_id):
                j=random.randint(1, len(nodes_raw))
            if (edges_actual>=edges_max):
                break
            else:
                if not(node_id, j) in neighbours: 
                    if not(j, node_id) in neighbours:
                        dot.edge(str(node_id), str(j))
                        edges_actual=edges_actual+1
                        neighbours.append((j,node_id))
             
    dot.view()
    dot.render()               
    return dot, neighbours


def getNeighboursFromGraph(graph,node_id):
    neighbour_ids=[]
    for str in graph.source.splitlines():
        if '--' in str: 
            str1 = str.strip(';').split()
            neighbour = [int(s) for s in str1 if s.isdigit()]
            #print(neighbour)
            if node_id in neighbour:
                if node_id == neighbour[0]:
                    neighbour_ids.append(neighbour[1])
                else:
                    neighbour_ids.append(neighbour[0])
                    
                    
    return neighbour_ids
                    

