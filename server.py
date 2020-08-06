from socket import *
from _thread import *
import sys
import random
import string
from datetime import datetime,timedelta
import os
  


#server_port, block_duration = int(sys.argv[1]),int(sys.argv[2])
server_port, block_duration = 12345,60
server_IP = '127.0.0.1'


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
            print(''.join(tempIDs[user]))
            return ' '.join(tempIDs[user])
    
    #Valid TempID does not exist, so we generate a new one
    digits = string.digits
    tempID = ''.join(random.choice(digits) for i in range(20))
    now = datetime.now()
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    exp_str = (now + timedelta(minutes=15)).strftime("%d/%m/%Y %H:%M:%S")
    #Add new tempID to database
    write_tempID_to_DB(user,tempID,now_str,exp_str)

    print(''.join([tempID,now_str,exp_str]))
    return ' '.join([tempID,now_str,exp_str])

 
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


## Recover phone numbers to contact from tempIDs
def recover_phone_numbers(contact_log):

    contacts = set()
    for line in contact_log.splitlines():
        tempID = line.split(" ")[0]
        contacts.add(tempID)
 
        
    tempIDs = get_tempIDs()
    inv_IDs = {v[0]: [k,v[1],v[2]] for k, v in tempIDs.items()}
    
    phoneNums = []
    
    for contact in contacts:
        
        try:
            phoneNum = inv_IDs[contact]
            phoneNums.append(phoneNum+[contact])
        except:
            print(f"Could not find Phone Number for {contact}")
        
    return phoneNums

#Print contact details to the Server Terminal
def display_phone_numbers(phoneNums):
    if(len(phoneNums)==0):
        print("No contacts to contact")
        return
    
    for details in phoneNums:
        print(f"{details[0]},")
        print(f"{details[1]},")
        print(f"{details[2]};")
        print("")



# thread function 
def manage_client(c): 
    
    #client login
    #User/Password limited to 24 characters
    user = str(c.recv(24).decode('ascii'))
    passw = str(c.recv(24).decode('ascii'))

    
    wrong_pass_count = 0
    
    blocked = get_blocked()
    
    if user in blocked and int(blocked[user]) > int(datetime.now().timestamp()):
        msg = "3"
        c.send(msg.encode('ascii')) 
        return
    
    while user not in credentials.keys() or credentials[user] != passw:
        msg = "0"
        wrong_pass_count += 1
        
        if wrong_pass_count >= 3:
            block(user)
            msg = "2"
            c.send(msg.encode('ascii'))  
            c.close()
            return 
            
        else:
            
            c.send(msg.encode('ascii'))     
                
            # data received from client 
            passw = str(c.recv(24).decode('ascii'))
                
    
        
    msg = "1"
    c.send(msg.encode('ascii'))
    
    #### Logged-In Phase ####    
    while True:
            
        user_choice = str(c.recv(1).decode('ascii'))
        
        if user_choice == "0":
            return
        elif user_choice == "1":
            tempID = generate_TempID(user)
            print("TempID:")
            print(tempID[0:20])
            c.send(tempID.encode('ascii')) 
        elif user_choice == "2":
            contact_log = c.recv(1024).decode('ascii')
            phone_nums = recover_phone_numbers(contact_log)
            display_phone_numbers(phone_nums)

  
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

    s = socket(AF_INET,SOCK_STREAM) 
    s.bind((server_IP, server_port)) 
    print("socket binded to port", server_port) 
  
    # put the socket into listening mode 
    s.listen(5) 
    print("Server has started") 
  
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        c, addr = s.accept() 
        # lock acquired by client 
        print(f"Connected to {addr[0]}:{addr[1]}") 
  
        # Start a new thread and return its identifier 
        start_new_thread(manage_client, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 