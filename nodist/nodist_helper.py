'''
Created on 17.11.2016

@author: Horst
'''

import pickle
import socket
import random
from node import NodeServer


def menu():
    print("Nodist ")
    print("1: lokale Node starten")
    print("2: alle Nodes starten")
    print("3: Node beenden")
    print("4: alle Nodes beenden")
    print("5: Geheimnis senden")
    print("6: Nachbar")
    print("7: ID Nachbarn Senden")
    print("0: Beenden")
    menu = input("->   :")
    return int(menu)


def sendMsg(host,port, msg):
    pickle_string = pickle.dumps(msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            sock.sendall(pickle_string)
            data = sock.recv(1024)
        finally:
            sock.close()
            
        print('Client Received', repr(data))
        
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

    
   


