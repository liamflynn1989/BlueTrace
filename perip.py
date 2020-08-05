#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
from socket import *
import sys
import time

client_udp_port = 12001

def periphery_mode(client_udp_port):


    clientSocket = socket(AF_INET, SOCK_DGRAM)
    
    message = "test msg"
    
    #Broadcast Beacon every 5 seconds for 1 minute
    for i in range(12):
        clientSocket.sendto(message.encode(),('localhost', client_udp_port))
        print(message)
        time.sleep(5)
        
    # Close the socket
    clientSocket.close()

