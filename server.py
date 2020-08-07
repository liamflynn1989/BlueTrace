from socket import *
from _thread import *
import sys
import random
import string
from datetime import datetime,timedelta
import os
  


server_port, block_duration = int(sys.argv[1]),int(sys.argv[2])
#server_port, block_duration = 12345,60
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
    inv_IDs = {v[0]: [k,' '.join([v[1],v[2]])] for k, v in tempIDs.items()}
    
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
    
    print("Contact Tracing Log:")
    for details in phoneNums:
        print(f"{details[0]},")
        print(f"{details[1]},")
        print(f"{details[2]};")
        print("")


#Send message to client c
def send_msg(c,payload):
    #Send Message to Server
    if len(payload)>1024:
        header = str(len(payload))
    else:
        header = '0'
        msg = f'{header}|{str(payload)}'
        c.send(msg.encode('ascii'))
        return
        
    #Long messages are sent in chunks of 1024 characters
    charSent = 0
    msg = f'{header}|{str(payload)}'
    
    while charSent < (len(payload)+len(header)):
        cap = min(charSent+1024,len(payload)+len(header))
        chunk = msg[charSent:cap]
        
        sent = c.send(chunk.encode('ascii'))
        if sent == 0:
            raise RuntimeError("Connection Broken")
        charSent = charSent + sent




#Recieve message from client c
def recv_msg(c,limit=1024):
    #limit is the character limit of the message
    #default is 1024 characters,allow some space for header
    msg = str(c.recv(limit+7).decode('ascii'))
    header,payload = msg.split('|')
    if header == '0':
        return payload
    
    #receiving long message in chunks of 1024 chars
    msg_len = int(header)
    while len(payload) < (msg_len-len(header)):
        payload += str(c.recv(limit).decode('ascii'))
    return payload
        
    



# thread function 
def manage_client(c): 
    
    #client login
    #User/Password limited to 24 characters
    user = recv_msg(c,24)
    passw = recv_msg(c,24)

    
    wrong_pass_count = 0
    
    blocked = get_blocked()
    
    if user in blocked and int(blocked[user]) > int(datetime.now().timestamp()):
        msg = "3"
        send_msg(c,payload=msg)
        return
    
    while user not in credentials.keys() or credentials[user] != passw:
        msg = "0"
        wrong_pass_count += 1
        
        if wrong_pass_count >= 3:
            block(user)
            msg = "2"
            send_msg(c,payload=msg)
            c.close()
            return 
            
        else:
            
            send_msg(c,payload=msg)   
                
            # data received from client 
            passw = recv_msg(c,24)
                
    
        
    msg = "1"
    send_msg(c,payload=msg)
    
    #### Logged-In Phase ####    
    while True:
            
        user_choice = recv_msg(c,1)
        
        if user_choice == "0":
            return
        elif user_choice == "1":
            tempID = generate_TempID(user)
            print("TempID:")
            print(tempID[0:20])
            send_msg(c,payload=tempID)
        elif user_choice == "2":
            contact_log = recv_msg(c)
            print(len(contact_log))
            phone_nums = recover_phone_numbers(contact_log)
            display_phone_numbers(phone_nums)

  
    c.close() 
   

  
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
        print(f"Connected to {addr[0]}:{addr[1]}") 
  
        # Start a new thread and return its identifier 
        start_new_thread(manage_client, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 