# import socket programming library 
import socket 
  
# import thread module 
from _thread import *
import threading 
  
print_lock = threading.Lock() 



#Read credentials.txt
with open("credentials.txt") as f:
    lines = [line.rstrip().split() for line in f]
    
credentials = {key:value for [key,value] in lines}
  
# thread function 
def threaded(c): 
    
    #Login Phase
    msg = "Please input username"
    c.send(msg.encode('ascii')) 
    # data received from client 
    user = str(c.recv(1024).decode('ascii'))
    
    msg = "Please input password"
    c.send(msg.encode('ascii')) 
    passw = str(c.recv(1024).decode('ascii'))
    
    if user in credentials.keys() and credentials[user] == passw:
        msg = "Success"
        c.send(msg.encode('ascii')) 
    else:
        msg = "Fail"
        c.send(msg.encode('ascii')) 
        print_lock.release() 
   
    
    
    while True: 

            
        response = str(c.recv(1024).decode('ascii'))
        if response == 'y': 
            continue
        else:
            # lock released on exit 
            print_lock.release() 
            break
   
  
    # connection closed 
    c.close() 
  
  
def Main(): 
    host = "" 
  
    # reverse a port on your computer 
    # in our case it is 12345 but it 
    # can be anything 
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("socket binded to port", port) 
  
    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening") 
  
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        c, addr = s.accept() 
  
        # lock acquired by client 
        print_lock.acquire() 
        print('Connected to :', addr[0], ':', addr[1]) 
  
        # Start a new thread and return its identifier 
        start_new_thread(threaded, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 