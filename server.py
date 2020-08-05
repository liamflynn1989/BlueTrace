from socket import *
from _thread import *
import threading 
import sys
import random
import string
from datetime import datetime,timedelta
import os
  


#server_port, block_duration = int(sys.argv[1]),int(sys.argv[2])
server_port, block_duration = 12345,60


#Read credentials.txt
with open("credentials.txt") as f:
    lines = [line.rstrip().split() for line in f]
    
credentials = {key:value for [key,value] in lines}



def get_tempIDs():
    #Read currently blocked users
    with open("tempIDs.txt") as f:
        lines = [line.rstrip().split() for line in f]
        
    tempIDs = {key:[value,start_date,start_time,exp_date,exp_time] for [key,value,start_date,start_time,exp_date,exp_time] in lines}

    return tempIDs  

def write_tempID_to_DB(user,tempID,now_str,exp_str):
    with open('tempIDs.txt', 'a+') as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0 :
            file_object.write("\n")
        
        file_object.write(' '.join([user,tempID,now_str,exp_str]))
        


#TempID
def generate_TempID(user):
    
    #Check if the current TempID is still valid for the user
    tempIDs = get_tempIDs()
    
    if user in tempIDs:
        exp_time = datetime.strptime(' '.join(tempIDs[user][3:]),"%d/%m/%Y %H:%M:%S").timestamp()
        if datetime.now().timestamp() < exp_time:
            #Valid tempID exists
            return ''.join(tempIDs[user])
    
    #Valid TempID does not exist, so we generate a new one
    letters = string.digits
    tempID = ''.join(random.choice(letters) for i in range(20))
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    exp_str = (now + timedelta(minutes=15)).strftime("%d/%m/%Y %H:%M:%S")
    #Add new tempID to database
    write_tempID_to_DB(user,tempID,now_str,exp_str)

    
    return ''.join([tempID,now_str,exp_str])

 
#Block User after 3 attempts
def block(user):
    exp = int(datetime.now().timestamp()) + block_duration
    with open('blocked.txt', 'a+') as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0 :
            file_object.write("\n")
        
        file_object.write(' '.join([user,str(exp)]))

def get_blocked():
    #Read currently blocked users
    with open("blocked.txt") as f:
        lines = [line.rstrip().split() for line in f]
        
    blocked = {key:value for [key,value] in lines}

    return blocked    


# thread function 
def manage_client(c): 
    
    # data received from client 
    user = str(c.recv(1024).decode('ascii'))
    passw = str(c.recv(1024).decode('ascii'))
    
    wrong_pass_count = 0
    
    blocked = get_blocked()
    
    if user in blocked and int(blocked[user]) > int(datetime.now().timestamp()):
        msg = "Your account is blocked due to multiple login failures. Please try again later"
        c.send(msg.encode('ascii')) 
    
    while user not in credentials.keys() or credentials[user] != passw:
        msg = "Invalid Password. Please try again"
        wrong_pass_count += 1
        
        if wrong_pass_count >= 3:
            block(user)
            msg = "Invalid Password. Your account has been blocked. Please try again later"
            c.send(msg.encode('ascii'))  
            c.close()
            return 
            
        else:
            
            c.send(msg.encode('ascii'))     
                
            # data received from client 
            passw = str(c.recv(1024).decode('ascii'))
                
    ##User is logged in        
    msg = "Success"
    c.send(msg.encode('ascii'))
    
    while True:
        
        user_choice = str(c.recv(1024).decode('ascii'))
        
        if user_choice == 'logout':
            return
        elif user_choice == "Download_tempID":
            tempID = generate_TempID(user)
            print("TempID:")
            print(tempID[0:20])
            c.send(tempID.encode('ascii')) 
        elif user_choice == "Upload_contact_log":
            ans = 'okay'
            c.send(ans.encode('ascii')) 

  
    c.close() 
   
#-------------------------------------------------------------------

def long_send(msg):
    totalsent = 0
    while totalsent < MSGLEN:
        sent = self.sock.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def long_receive(self):
    chunks = []
    bytes_recd = 0
    while bytes_recd < MSGLEN:
        chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)
  
#-------------------------------------------------------------------
  
def Main(): 
    host = "" 
    s = socket(AF_INET,SOCK_STREAM) 
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
        print('Connected to :', addr[0], ':', addr[1]) 
  
        # Start a new thread and return its identifier 
        start_new_thread(manage_client, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 