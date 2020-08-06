# Import socket module 
from socket import *
import sys
from _thread import *
import time
from datetime import datetime,timedelta

#BlueTrace Protocol Version
version_id = 1
client_IP = '127.0.0.1'


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
            

    def peripheral_mode(self,s):
    

        clientSocket = socket(AF_INET, SOCK_DGRAM)
        #Will get new tempID from server if current one has expired
        self.get_tempID(s)
        message = ' '.join([self.tempID,self.tempID_start,self.tempID_end])
        
        #Broadcast Beacon every 5 seconds for 1 minute
        print()
        print("Sending Beacons in the background every 15 seconds for 1 minute")
        for i in range(4):
            clientSocket.sendto(message.encode(),(client_IP, self.udp_port))
            time.sleep(15)
            
        # Close the socket
        clientSocket.close()


    def central_mode(self,s):
    
        s = socket(AF_INET,SOCK_DGRAM) 
        s.bind((client_IP, self.udp_port)) 
        
        
        #Erase contact log
        contact_log = "z5244712_contactlog.txt"
        file = open(contact_log,"w")
        file.close()

        print()
        print("Now listening for beacons in the background")
          
        # a forever loop until client wants to exit 
        while True: 
            
            beacon = str(s.recv(21+21+21).decode('ascii')) 
            
            #extract start and end time from beacon
            beacon_start = datetime.strptime(beacon[21:40],"%d/%m/%Y %H:%M:%S").timestamp()
            beacon_end = datetime.strptime(beacon[41:60],"%d/%m/%Y %H:%M:%S").timestamp()
            now = datetime.now().timestamp()
            
            #If beacon is valid, add to contact log
            if now > beacon_start and now < beacon_end:
            
                self.add_to_contact_log(beacon)

            
    def add_to_contact_log(self,beacon):
        contact_log = "z5244712_contactlog.txt"
        tempID = beacon[0:20]
        tempID_start = beacon[21:40]
        tempID_exp = beacon[41:60]
        
        with open(contact_log, 'a+') as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0 :
                file_object.write("\n")
            print()
            print(' '.join([tempID,tempID_start,tempID_exp]))
            file_object.write(' '.join([tempID,tempID_start,tempID_exp]))
        
    ## This runs at 3 minute intervals to remove
    ## old beacons
    def remove_old_contacts(self):
        pass
        
    def upload_contact_log(self,s):
        msg = '2'
        s.send(msg.encode('ascii')) 
        
        contact_log = "z5244712_contactlog.txt"
        with open(contact_log, 'r') as file_object:
            data = file_object.read()
            s.send(data.encode('ascii')) 
            print(data)
    


def Main(): 

    if len(sys.argv)!=4:
        print("3 Command line arguments are required")
        print("Expected usage:")
        print("python client.py server_IP server_port client_udp_port")
        return 
    
    
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
            logout_msg = "0"
            s.send(logout_msg.encode('ascii')) 
            return
        elif ans == "Download_tempID":
            print()
            usr.retrieve_tempID(s)
            print(usr.tempID)
        elif ans == "Upload_contact_log":
            print("Uploading Contact Log")
            usr.upload_contact_log(s)
        elif ans == "Peripheral Mode":
            #Send Beacons via UDP
            start_new_thread(usr.peripheral_mode, (s,))
            
        elif ans == "Central Mode":
            #Waiting to recieve beacons
            start_new_thread(usr.central_mode, (s,))
        else:
            print("Sorry I didn't understand your command")
        
        print()
        print()
        _ = input("Press enter to return to main menu")
        
        


if __name__ == '__main__': 
    Main() 