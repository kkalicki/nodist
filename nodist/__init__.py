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
    

    args = parser.parse_args()
    
    
    data = args.FILE

    try:
        node_id = int(args.ID)
        if (args.start=='true'):
                    
            node = NodeServer(node_id,data)
            
            msg = Message(MessageType.Neighbour,"Geiz ist Geil", 0)
            nodist_helper.sendInitSpreadMsg(node, msg)
            
        else:
            menu = 1
            while (menu!=0):
                try:
                    menu = nodist_helper.menu()
                    if menu == 1:
                        subprocess.Popen('py __init__.py data 5 --start true', creationflags = subprocess.CREATE_NEW_CONSOLE)
                    else:
                        print("Fehlerhafte Eingabe")
                except ValueError:
                    print("Bitte eine Zahl eingeben!!")
                
                
        
    except ValueError:
        print("Bitte eine Zahl als ID eingeben!!")