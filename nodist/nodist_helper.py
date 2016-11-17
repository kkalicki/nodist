'''
Created on 17.11.2016

@author: Horst
'''

import pickle
import socket


def menu():
    print("Nodist ")
    print("1: lokale Node starten")
    print("2: alle Nodes starten")
    print("3: Node beenden")
    print("4: alle Nodes beenden")
    print("5: Geheimnis senden")
    print("6: Nachbar")
    print("0: Beenden")
    menu = input("->   :")
    return int(menu)


def sendInitSpreadMsg(node, msg):
    pickle_string = pickle.dumps(msg)
    pickle.loads(pickle_string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((node.host, node.port))
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
   


