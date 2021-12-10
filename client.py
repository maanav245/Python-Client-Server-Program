from socket import *
import sys
import select
import threading
import time 

base_message = "\n> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT): "
logout = 0 

"""
A thread used to run the Client's udp server, which will accept files/videos from other clients
"""
class udp_server_Thread (threading.Thread):
    def __init__(self, threadID, udp_port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.udp_port = udp_port

    def run(self):
        
        UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
        UDPServerSocket.bind(('localhost', self.udp_port))
        while logout == 0: 
            
            name, addr = (UDPServerSocket).recvfrom(1024)
            filename, addr = (UDPServerSocket).recvfrom(1024)
            new_file = open(name.decode() + '_' + filename.decode(), 'ab')
            
            file_data, addr = (UDPServerSocket).recvfrom(1024)
            try: 
                while (file_data): 
                    new_file.write(file_data)
                    UDPServerSocket.settimeout(3)
                    file_data, addr = (UDPServerSocket).recvfrom(1024)
            except timeout: 
                print("> Received {} from {}".format(filename.decode(), name.decode()))
                print("> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):")
                new_file.close()
                UDPServerSocket.settimeout(None)
            
        UDPServerSocket.close()

"""
A thread used when the client wants to upload files to another client, while still being able to supply commands to the server
"""
class uploading_Thread (threading.Thread):
    def __init__(self, threadID, uip, uport, filename):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.uip = uip
        self.uport = uport
        self.filename = filename

    def run(self):
       
        str_uport = int(self.uport)
        requester = (self.uip, str_uport)
        new_sock = socket(AF_INET, SOCK_DGRAM)
        
        try: 
            f = open(self.filename, "rb")
        except: 
            print("> Invalid Filename")
            return 
        new_sock.sendto((self.threadID).encode(), requester)
        new_sock.sendto((self.filename).encode(), requester)       
        data = f.read(1024)
        print("> {} has been uploaded".format(self.filename))
        while data: 
            if (new_sock.sendto(data, requester)):
                data = f.read(1024)
        
        f.close()
        new_sock.close()
        return

"""
Information used to capture server info from comannd line arguements and start server
"""

serverName = sys.argv[1]  
serverPort = int(sys.argv[2]) 
udp_port = int(sys.argv[3])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

"""
First attempt at  logging into server
"""
Username = input("> Username: ")
while not Username:
    print("> Please enter Username")
    Username = input("> Username: ")
clientSocket.send(Username.encode())

Password = input("> Password: ")
while not Password:
    print("> Please enter Password")
    Password = input("> Password: ")



clientSocket.send(Password.encode())
blocked = 0
"""
Small while loop used to handle when password or username is incorrect
"""
while True: 
 
    data = clientSocket.recv(1024)
    print(data.decode(), end= "")
    skip = 0
    if data.decode() == "> Invalid Password. Your account has been blocked. Please try again later" or data.decode() == "> Your account is blocked due to multiple login failures. Please try again later":
        blocked = 1
        break 
    elif data.decode() == "> Welcome to TOOM!\n":
        break
    

    elif data.decode() == "> Invalid Login. Please try again\n":
        
        Username = input("> Username: ")
        while not Username:
            print("> Please enter Username")
            Username = input("> Username: ")
        
        Password = input("> Password: ")
        while not Password:
            print("> Please enter Password")
            Password = input("> Password: ")
        clientSocket.send(Username.encode())
        clientSocket.send(Password.encode())
        skip = 1

    elif skip == 0:
        response = input()
        while not response:
            
            response = input()
        clientSocket.send(response.encode())


"""
If the client has been able to login succesfully, the client can start to supply commands 
"""
if blocked == 0:

    clientSocket.send(str(udp_port).encode())
    udp_handler = udp_server_Thread(1, udp_port)
    udp_handler.daemon = True 
    udp_handler.start()

    while True: 

        data = clientSocket.recv(1024)
        print(data.decode())
        response = input()
        while not response:
            print("> Invalid Characters" + base_message)
            response = input()
        clientSocket.send(response.encode())
        command = response[0:4].strip() 
        
        if command == 'UPD': 
            """
            Used to handle when the client wants to upload files to another client
            """
            upd_list = response.split()
            
            udp_server_info1 = (clientSocket.recv(1024).decode())
            if udp_server_info1 != "> User not active or does not exist":
                udp_server_info = udp_server_info1.split()
                udp_server_ip = udp_server_info[0]
                udp_server_port = udp_server_info[1]
                uploader = uploading_Thread(Username, udp_server_ip, udp_server_port, upd_list[2])
                uploader.start()
            else: 
                print("> User not active or does not exist")
        if response == "OUT":
            clientSocket.close()
            print("> Bye, {}".format(Username))
            sys.exit()
            break

clientSocket.close()