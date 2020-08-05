# Import socket module 
import socket 
import sys



def try_login(s):

    msg = input("Username: ")
    #username sent to server 
    s.send(msg.encode('ascii')) 
    
    msg = input("Password: ")
    #password sent to server 
    s.send(msg.encode('ascii')) 
    
    data = s.recv(1024) 
    print(str(data.decode('ascii')))
    return str(data.decode('ascii'))
  
def retry_login(s):


    
    msg = input("Password: ")
    #password sent to server 
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
    
    while response == "Invalid Password. Please try again":
        response = retry_login(s)
        
        
    if response=="Invalid Password. Your account has been blocked. Please try again later":
        return 
    
    if response=="Your account is blocked due to multiple login failures. Please try again later":
        return 
        
    #Client has successfully logged in    
    print('Welcome to the BlueTrace Simulator!')
    ans = ''
    while ans != "logout":
        # ask the client what they would like to do
        print("Your Options are:")
        print("")
        print("  Download_tempID")
        print("  Upload_contact_log")
        print("  logout")
        print("")
        
        ans = input('Type your choice: ') 
        if ans == 'logout':
            print("Logging Out")
            s.send(ans.encode('ascii')) 
            return
        elif ans == "Download_tempID":
            print()
            s.send(ans.encode('ascii')) 
            data = s.recv(1024) 
            print(str(data.decode('ascii')))
            
            
        elif ans == "Upload_contact_log":
            print("Uploading Contact Log")
            s.send(ans.encode('ascii')) 
        else:
            print("Sorry I didn't understand your command")
        
        print()
        print()
        unused = input("Press enter to return")


if __name__ == '__main__': 
    Main() 