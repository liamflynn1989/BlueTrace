# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 21:45:11 2020

@author: liamf
"""

from socket import *
from _thread import *
import threading 
import sys
import random
import string
from datetime import datetime,timedelta
import os
  
client_udp_port = 12001

def central_mode(client_udp_port):

    s = socket(AF_INET,SOCK_DGRAM) 
    s.bind(('localhost', client_udp_port)) 
    print("socket binded to port", client_udp_port) 
      
      
    # a forever loop until client wants to exit 
    while True: 
        
        data = s.recv(1024) 
        print(str(data.decode('ascii')))
        ans = input("Do you want to keep listening for beacons? (y/n)")
        
        if ans == 'n':
            break
        
    
    s.close() 
      
  
