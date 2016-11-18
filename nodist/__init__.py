import argparse
import nodist_helper
import subprocess
import sys
import time
from node import NodeServer
from message import Message, MessageType

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(prog="Nodist")
    parser.add_argument("FILE", help="file to read socket information", type=str)
    parser.add_argument("ID", help="ID of your node", type=int)
    parser.add_argument("--start", help="start directly server")
    parser.add_argument("--graph", help="open graphviz source file")
    
    

    args = parser.parse_args()
    
    
    data = args.FILE

    try:
        node_id = int(args.ID)
        nodes_raw = nodist_helper.readFromFile(data)
        host, port = nodist_helper.getAddress(nodes_raw, node_id)  
        if (args.start == 'true'):
                    
            node = NodeServer(node_id, data)
            # msg = Message(MessageType.sendID,"Geiz ist Geil", 0)
            # nodist_helper.sendMsg(host,port, msg)
            
            
            
        else:
            menu = 1
            while (menu != 0):
                try:
                    menu = nodist_helper.menu()
                    if menu == 0: break
                    if menu == 1:
                        subprocess.Popen('py __init__.py data 5 --start true', creationflags=subprocess.CREATE_NEW_CONSOLE)
                    elif menu == 2:
                        for node in nodes_raw:
                            id_str = str(node[0])
                            subprocess.Popen("py __init__.py data " + id_str + " --start true", creationflags=subprocess.CREATE_NEW_CONSOLE)
                    
                    elif menu == 3:
                        msg = Message(MessageType.shutdown, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    
                    elif menu == 4:
                        msg = Message(MessageType.shutdownAll, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    
                    elif menu == 5:
                        msg = Message(MessageType.spreadMsg, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                        
                    elif menu == 6:                       
                        msg = Message(MessageType.printNeighbours, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    
                    elif menu == 7:                       
                        msg = Message(MessageType.sendID, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)

                    elif menu == 8:                       
                        msg = Message(MessageType.status, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    elif menu == 9:                       
                        msg = Message(MessageType.reset, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    elif menu == 10:
                        for node in nodes_raw:
                            node_id = node[0]
                            host, port = nodist_helper.getAddress(nodes_raw, node_id)                        
                            msg = Message(MessageType.reset, "Geiz ist Geil", 0)
                            nodist_helper.sendMsg(host, port, msg)
                        
                    else:
                        print("Fehlerhafte Eingabe")
                except ValueError:
                    print("Bitte eine Zahl eingeben!!")
                
                
        
    except ValueError:
        print("Bitte eine Zahl als ID eingeben!!")
