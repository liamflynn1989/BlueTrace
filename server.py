# import socket programming library 
import socket 
  
# import thread module 
from _thread import *
import threading 
import sys
import random
import string
from datetime import datetime,timedelta
import os
  
#print_lock = threading.Lock() 

#server_port, block_duration = int(sys.argv[1]),int(sys.argv[2])
server_port, block_duration = 12345,60


#Read credentials.txt
with open("credentials.txt") as f:
    lines = [line.rstrip().split() for line in f]
    
credentials = {key:value for [key,value] in lines}
 

#TempID
def generate_TempID(user):
    
    # printing digits
    letters = string.digits
    tempID = ''.join(random.choice(letters) for i in range(20))
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    exp_str = (now + timedelta(minutes=15)).strftime("%d/%m/%Y %H:%M:%S")
    ##with open(os.path.join(sys.path[0],'sample.txt'), 'a') as f:
    with open('sample.txt', 'a+') as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0 :
            file_object.write("\n")
        
        file_object.write(' '.join([user,tempID,now_str,exp_str]))
    
    return tempID

 
#Block User after 3 attempts
def block(user):
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    with open('blocked.txt', 'a+') as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0 :
            file_object.write("\n")
        
        file_object.write(' '.join([user,now_str]))

    


# thread function 
def sign_in(c): 
    
    #Login Phase
    msg = "Please input username"
    c.send(msg.encode('ascii')) 
    # data received from client 
    user = str(c.recv(1024).decode('ascii'))
    
    msg = "Please input password"
    c.send(msg.encode('ascii')) 
    passw = str(c.recv(1024).decode('ascii'))
    
    wrong_pass_count = 0
    
    while user not in credentials.keys() or credentials[user] != passw:
        msg = "Incorrect Password"
        wrong_pass_count += 1
        
        if wrong_pass_count >= 3:
            block(user)
            msg = "You have been blocked for 3 wrong attempts"
            c.send(msg.encode('ascii'))  
            #print_lock.release() 
            c.close()
            return 
            
        else:
            
            c.send(msg.encode('ascii'))     
                
            #Login Phase
            msg = "Please input username"
            c.send(msg.encode('ascii')) 
            # data received from client 
            user = str(c.recv(1024).decode('ascii'))
            
            msg = "Please input password"
            c.send(msg.encode('ascii'))
            passw = str(c.recv(1024).decode('ascii'))
                
            
    msg = "Success"
    c.send(msg.encode('ascii')) 
    tempID = generate_TempID(user)
    #Send TempID to user
    c.send(tempID.encode('ascii')) 
    #print_lock.release() 
    c.close() 
   

  

  
def Main(): 
    host = "" 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, server_port)) 
    print("socket binded to port", server_port) 
  
    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening") 
  
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        c, addr = s.accept() 
        # lock acquired by client 
        #print_lock.acquire() 
        print('Connected to :', addr[0], ':', addr[1]) 
  
        # Start a new thread and return its identifier 
        start_new_thread(sign_in, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 