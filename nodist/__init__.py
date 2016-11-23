import argparse
import nodist_helper
import subprocess
import sys
import time
from node import NodeServer
from nodistMenu import NodistMenu

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(prog="Nodist")
    parser.add_argument("FILE", help="file to read socket information", type=str)
    parser.add_argument("ID", help="ID of your node", type=int)
    parser.add_argument("--start", help="start directly server")

    
    

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
            
            
        #elif args.test:
            
            #nodist_helper.startTestServer(args.test, args.port, len(nodes_raw), len) 
            
        else:
            menu_int = 1
            while (menu_int != 0):
                try:
                    menu = NodistMenu(node_id, data, nodes_raw)
                    menu_int = menu.menu_int
                    '''
                    if menu_int == 0: break
                    if menu_int == 1:
                        node = NodeServer(node_id, data)
                    elif menu_int == 2:
                        for node in nodes_raw:
                            node = NodeServer(node[0], data)
                    
                    elif menu_int == 3:
                        msg = Message(MessageType.shutdown, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                        #nodist_helper.sendMsg(host, port, MessageType.shutdown, "Geiz ist Geil", 0)
                    
                    elif menu_int == 4:
                        msg = Message(MessageType.shutdownAll, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    
                    elif menu_int == 5:
                        msg = Message(MessageType.spreadMsg, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                        
                    elif menu_int == 6:                       
                        msg = Message(MessageType.printNeighbours, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                    
                    elif menu_int == 7:                       
                        msg = Message(MessageType.sendID, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)

                    elif menu_int == 8:                       
                        msg = Message(MessageType.status, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                        
                    elif menu_int == 9:                       
                        msg = Message(MessageType.reset, "Geiz ist Geil", 0)
                        nodist_helper.sendMsg(host, port, msg)
                        
                    elif menu_int == 10:
                        for node in nodes_raw:
                            node_id = node[0]
                            host, port = nodist_helper.getAddress(nodes_raw, node_id)                        
                            msg = Message(MessageType.reset, "Geiz ist Geil", 0)
                            nodist_helper.sendMsg(host, port, msg)
                        
                    elif menu_int == 11:
                        subprocess.Popen('py __init__.py data 5 --test Horst --port 41050', creationflags=subprocess.CREATE_NEW_CONSOLE)
                        
                    else:
                        print("Fehlerhafte Eingabe")
                    '''
                except ValueError:
                    print("Bitte eine Zahl eingeben!!")
                
                
        
    except ValueError:
        print("Bitte eine Zahl als ID eingeben!!")
