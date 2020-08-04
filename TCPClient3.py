# Import socket module 
import socket 
  
  
def Main(): 
    # local host IP '127.0.0.1' 
    host = '127.0.0.1'
  
    # Define the port on which you want to connect 
    port = 12345
  
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
  
    # connect to server on local computer 
    s.connect((host,port)) 
    
    
    data = s.recv(1024) 
    print(str(data.decode('ascii'))) 
    msg = input("Username: ")
    # message sent to server 
    s.send(msg.encode('ascii')) 
    data = s.recv(1024) 
    print(str(data.decode('ascii'))) 
    msg = input("Password: ")
    # message sent to server 
    s.send(msg.encode('ascii')) 
    
    data = s.recv(1024) 
    print(str(data.decode('ascii'))) 
  

    while True: 
  
        # ask the client whether he wants to continue 
        ans = input('Do you want to continue(y/n) :') 
        if ans == 'y': 
            s.send(ans.encode('ascii')) 
            continue
        else: 
            s.send(ans.encode('ascii')) 
            break
    # close the connection 
    s.close() 
  
if __name__ == '__main__': 
    Main() 