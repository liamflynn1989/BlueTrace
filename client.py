# Import socket module 
import socket 
import sys



def try_login(s):
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
    return str(data.decode('ascii'))
  
  
def Main(): 
    # local host IP '127.0.0.1' 
    server_IP, server_port, client_udp_port = sys.argv[1],int(sys.argv[2]),sys.argv[3],

  
    # Define the port on which you want to connect 
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
  
    # connect to server on local computer 
    s.connect((server_IP,server_port)) 
    
    response = try_login(s)
    
    while response == "Incorrect Password":
        response = try_login(s)
        
        
    if response=="You have been blocked for 3 wrong attempts":
        pass
        
        
    

    while True: 
  
        # ask the client whether he wants to continue 
        ans = input('Do you want to continue(y/n) :') 
        if ans == 'y': 
            s.send(ans.encode('ascii')) 
            continue
        else: 
            s.send(ans.encode('ascii')) 
            print("here")
            break
    # close the connection 
    #s.close() 
    print("also here")
  
if __name__ == '__main__': 
    Main() 