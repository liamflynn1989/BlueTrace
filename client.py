# Import socket module 
from socket import *
import sys
from _thread import *
import time

#BlueTrace Protocol Version
version_id = 1

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

    

def periphery_mode(client_udp_port):


    clientSocket = socket(AF_INET, SOCK_DGRAM)
    
    message = "test msg"
    
    #Broadcast Beacon every 5 seconds for 1 minute
    for i in range(12):
        clientSocket.sendto(message.encode(),('localhost', client_udp_port))
        print(message)
        time.sleep(5)
        
    # Close the socket
    clientSocket.close()


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
            s.close()
            return





def Main(): 
    # local host IP '127.0.0.1' 
    server_IP, server_port, client_udp_port = sys.argv[1],int(sys.argv[2]),int(sys.argv[3])

  
    # Define the port on which you want to connect 
    s = socket(AF_INET,SOCK_STREAM) 
  
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
        print("  Central Mode")
        print("  Peripheral Mode")
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
            data = s.recv(20+19+19)
            tempID = str(data.decode('ascii'))
            print(tempID)
            print(tempID[0:20])
        elif ans == "Upload_contact_log":
            print("Uploading Contact Log")
            s.send(ans.encode('ascii'))
        elif ans == "Peripheral Mode":
            #Send Beacons via UDP
            periphery_mode(client_udp_port)

            
        elif ans == "Central Mode":
            #Waiting to recieve beacons
            central_mode(client_udp_port)
        else:
            print("Sorry I didn't understand your command")
        
        print()
        print()
        unused = input("Press enter to return to main menu")
        
        #Central or Peripheral State
        


if __name__ == '__main__': 
    Main() 