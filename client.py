# Import socket module 
from socket import *
import sys
from _thread import *
import time
from datetime import datetime,timedelta

#BlueTrace Protocol Version
version_id = 1

# def try_login(s):

#     msg = input("Username: ")
#     #username sent to server 
#     s.send(msg.encode('ascii')) 
    
#     msg = input("Password: ")
#     #password sent to server 
#     s.send(msg.encode('ascii')) 
    
#     data = s.recv(1) 

#     return str(data.decode('ascii'))



class User:
    def __init__(self,udp_port):
        self.id = None
        self.udp_port = udp_port
        self.tempID = None
        #Initialize tempID start,end time with arbitrary time in the past
        self.tempID_start = "01/01/2000 00:00:00"
        self.tempID_end = "01/01/2000 00:00:00"
        
        
        
    def try_login(self,s):

        user_id = input("Username: ")
        #username sent to server 
        s.send(user_id.encode('ascii'))
        self.id = user_id
        
        passw = input("Password: ")
        #password sent to server 
        s.send(passw.encode('ascii')) 
        
        resp = s.recv(1) 
        return str(resp.decode('ascii'))
  
    def retry_login(self,s):
    
        msg = input("Password: ")
        #password sent to server 
        s.send(msg.encode('ascii')) 
        
        resp = s.recv(1) 
        return str(resp.decode('ascii'))
    
    def retrieve_tempID(self,s):
        #Option 1
        msg = '1'
        s.send(msg.encode('ascii')) 
        data = s.recv(21+21+21)
        tempID = str(data.decode('ascii'))
        self.tempID = tempID[0:20]
        self.tempID_start = tempID[21:40]
        self.tempID_end = tempID[41:60]
        
        
    def get_tempID(self,s):
        
        #Check if current tempID is still valid
        exp_time = datetime.strptime(self.tempID_end,"%d/%m/%Y %H:%M:%S").timestamp()
        if datetime.now().timestamp() < exp_time:
            pass
        else:
            #If tempID not valid, ask server for new one
            self.retrieve_tempID(s)
        
        

    

    def periphery_mode(self,s):
    

        clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.get_tempID(s)
        message = self.tempID
        
        #Broadcast Beacon every 5 seconds for 1 minute
        print()
        print("Sending Beacons every 5 seconds for 1 minute")
        for i in range(12):
            clientSocket.sendto(message.encode(),('localhost', self.udp_port))
            time.sleep(5)
            
        # Close the socket
        clientSocket.close()


    def central_mode(self,s):
    
        s = socket(AF_INET,SOCK_DGRAM) 
        s.bind(('localhost', self.udp_port)) 

        print()
        print("Now listening for beacons")
          
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
    
    #Instantiate user with udp_port
    usr = User(client_udp_port)
    
    response = usr.try_login(s)
    
    while response == "0":
        print("Invalid Password. Please try again")
        response = usr.retry_login(s)
        
        
    if response=="2":
        print("Invalid Password. Your account has been blocked. Please try again later")
        return 
    
    if response=="3":
        print("Your account is blocked due to multiple login failures. Please try again later")
        return 
        
    #Client has successfully logged in    
    print('Welcome to the BlueTrace Simulator!')
    ans = ''
    while ans != "logout":
        # ask the client what they would like to do
        print("Your Options are:")
        print("")
        #Option 1
        print("  Download_tempID")
        #Option 2
        print("  Upload_contact_log")
        #Option 3
        print("  Central Mode")
        #Option 4
        print("  Peripheral Mode")
        #Option 0
        print("  logout")
        print("")
        
        ans = input('Type your choice: ') 
        if ans == 'logout':
            print("Logging Out")
            s.send(ans.encode('ascii')) 
            return
        elif ans == "Download_tempID":
            print()
            usr.retrieve_tempID(s)
            print(usr.tempID)
        elif ans == "Upload_contact_log":
            print("Uploading Contact Log")
            s.send(ans.encode('ascii'))
        elif ans == "Peripheral Mode":
            #Send Beacons via UDP
            start_new_thread(usr.periphery_mode, (s,))
            time.sleep(1)
            
        elif ans == "Central Mode":
            #Waiting to recieve beacons
            usr.central_mode(s)
        else:
            print("Sorry I didn't understand your command")
        
        print()
        print()
        unused = input("Press enter to return to main menu")
        
        


if __name__ == '__main__': 
    Main() 