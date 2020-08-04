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
    
    
    #this should do a check if the current TempID is still valid
    
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
            #print_lock.release() 
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
            print(tempID)
            c.send(tempID.encode('ascii')) 
        elif user_choice == "Upload_contact_log":
            ans = 'okay'
            c.send(ans.encode('ascii')) 
        
        
        
        
        
        
       
        
        
        
        #Send TempID to user
        c.send(tempID.encode('ascii')) 
  
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
        start_new_thread(manage_client, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 