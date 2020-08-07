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
        
        
    def send_msg(self,s,payload):
        #Send Message to Server
        if len(payload)>1024:
            header = str(len(payload))
        else:
            header = '0'
            msg = f'{header}|{str(payload)}'
            s.send(msg.encode('ascii'))
            return
            
        #Long messages are sent in chunks of 1024 characters
        charSent = 0
        msg = f'{header}|{str(payload)}'
        i = 0
        while charSent < (len(payload)+len(header)):
            print(i)
            cap = min(charSent+1024,len(payload)+len(header))
            chunk = msg[charSent:cap]
            
            sent = s.send(chunk.encode('ascii'))
            if sent == 0:
                raise RuntimeError("Connection Broken")
            charSent = charSent + sent
            i += 1
            
        
    def recv_msg(self,s,limit=1024):
        #limit is the character limit of the message
        #default is 1024 characters, add 7 chars for header
        msg = str(s.recv(limit+7).decode('ascii'))
        header,payload = msg.split('|')
        if header == '0':
            return payload
        
        #receiving long message in chunks of 1024 chars
        msg_len = int(header)
        
        while len(payload) < msg_len:
            payload += str(c.recv(limit).decode('ascii'))
        
        return payload
    

        
    def try_login(self,s):

        user_id = input("Username: ")
        #username sent to server
        self.send_msg(s,payload=user_id)
        self.id = user_id
        
        passw = input("Password: ")
        #password sent to server 
        self.send_msg(s,payload=passw)
        
        resp = self.recv_msg(s,1)
        return resp
  
    def retry_login(self,s):
    
        passw = input("Password: ")
        #password sent to server  
        self.send_msg(s,payload=passw)
        
        resp = self.recv_msg(s,1) 
        return resp
    
    def retrieve_tempID(self,s):
        #Option 1
        msg = '1'
        self.send_msg(s,payload=msg)
        tempID = self.recv_msg(s,21+21+21)
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
        
        print()
        print("Sending Beacon")
        clientSocket.sendto(message.encode(),(client_IP, self.udp_port))
            
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
            
            beacon = str(s.recv(21+21+21+1).decode('ascii'))
            
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
        
        now = datetime.now()
        now_str = now.strftime("%d/%m/%Y %H:%M:%S")
        
        with open(contact_log, 'a+') as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0 :
                file_object.write("\n")
            print()
            print(' '.join([tempID,tempID_start,tempID_exp]))
            file_object.write(' '.join([tempID,tempID_start,tempID_exp,now_str]))
        
    ## This runs at 3 minute intervals to remove old beacons
    def remove_old_contacts(self):
        while True:
            #Run cleanup every 3 minutes
            time.sleep(180)
            contact_log = "z5244712_contactlog.txt"
            
            with open(contact_log, "r+") as f:
                # First read the file line by line
                lines = f.readlines()
            
                # Go back at the start of the file
                f.seek(0)
                now_time = datetime.now().timestamp()
                # Filter out and rewrite lines
                for line in lines:
                    
                    contact_time = datetime.strptime(line[-20:].strip(),"%d/%m/%Y %H:%M:%S").timestamp()
                    if (now_time - contact_time)/60 < 3:
                    
                        f.write(line)
    
                # Truncate the remaining of the file
                f.truncate()
        
    def upload_contact_log(self,s):
        msg = '2'
        #s.send(msg.encode('ascii'))
        self.send_msg(s,payload=msg)
        
        contact_log = "z5244712_contactlog.txt"
        with open(contact_log, 'r') as file_object:
            data = file_object.read()
            self.send_msg(s,payload=data)
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
            msg = "0"
            usr.send_msg(s,payload=msg)
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
            start_new_thread(usr.remove_old_contacts, ())
        else:
            print("Sorry I didn't understand your command")
        
        print()
        print()
        _ = input("Press enter to return to main menu")
        
        


if __name__ == '__main__': 
    Main() 