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
        else:
            menu_int = 1
            while (menu_int != 0):
                try:
                    menu = NodistMenu(node_id, data, nodes_raw)
                    menu_int = menu.menu_int
                except ValueError:
                    print("Bitte eine Zahl eingeben!!")
    except ValueError:
        print("Bitte eine Zahl als ID eingeben!!")
