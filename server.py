from socket import *
import threading
import time
import signal
import os
import sys
from datetime import datetime
import signal

"""
Global Variables:
    base_message -> a string used repeatedly throughout the program
    messages -> A list of dictionaries used to store messages and their information 
    users -> A list of dictionaries used to store user information
"""
base_message = "\n> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD): "
messages = []
users = []

def message_transfer():
    """
    Function used to transfer records of messages from messages list into messagelog.txt 
    """
    msg_log = open("messagelog.txt", 'w')
    
    for message in messages: 
        position = messages.index(message) + 1
        string2 = "{}; {}; {}; {}; {}\n".format(position, message['date'], message['username'], message['message'], message["edited"])
        msg_log.write(string2)


def message_op(username, message, csocket): 
    """
    username -> username of client making request 
    message -> message made by client 
    csocket -> TCP socket used to communicate back with client

    A function used to handle message requests from the client, and store them appropriately in messages list data 
    structure as a dictionary.
    Errors will be called whenever the the client is unauthorised or ha an invalid message
    """
    new_dict = {
        'date': "",
        'username': "",
        'message': "",
        'edited': "no"
    }
    today = datetime.now()
    new_dict['date'] = str(today.strftime("%d %b %Y %H:%M:%S"))
    if message.isspace() == True:
        csocket.send(("> Invalid Message, try again" + base_message).encode())
        print('> {} attempted to post Message #{} "{}" at {}. Invalid Message.'.format(username, len(messages), message, new_dict['date']))
        return
    new_dict['message'] = message 
    new_dict['username'] = username
    messages.append(new_dict)
    message_transfer()
    string1 = "> Message #{} posted at {}".format(len(messages), new_dict['date'])
    csocket.send((string1 + base_message).encode()) 
    print('> {} posted Message #{} "{}" at {}.'.format(username, len(messages), message, new_dict['date']))

def message_remove(csocket, username, messagenumber, timestamp):
    """
    csocket -> Port, Address used to communicate back to client 
    username -> username of client 
    messagenumber -> requested messagenumber for message which client wants to remove 
    timestamp -> The time in which the client posted the message, the client wants to remove

    Simple function used to remove message from data and update messagelog.txt
    Errors will be called whenever the timestamp, username and messagenumber does not match
    """ 
    today = datetime.now()
    if messagenumber.isnumeric() == True and int(messagenumber) <= len(messages):
        messagenumber = int(messagenumber)
        if messages[messagenumber - 1]['date'] == timestamp and messages[messagenumber - 1]['username'] == username: 
            
            today = datetime.now()
            string1 = "> Message #{} deleted at {}".format(messagenumber, str(today.strftime("%d %b %Y %H:%M:%S")))
            print('> {} deleted Message #{} "{}" at {}.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            csocket.send((string1 + base_message).encode()) 
            messages.remove(messages[messagenumber - 1])
        elif messages[messagenumber - 1]['date'] != timestamp:
            csocket.send(("> Invalid Timestamp, try again" + base_message).encode())
            print('> {} attempted to delete Message #{} "{}" at {}. Invalid timestamp.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            return 
        elif messages[messagenumber - 1]['username'] != username:
            csocket.send(("> Not authorised, try again" + base_message).encode())
            print('> {} attempted to delete Message #{} "{}" at {}. Authorisation fails.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            return
        message_transfer()
    else: 
        csocket.send(("> Invalid Message Number, try again" + base_message).encode())
        print('> {} attempted to delete Message #{} "{}" at {}. Invalid Message No.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
        return
def message_edt(csocket, username, messagenumber, timestamp, new_msg):
    """
    csocket -> Port, Address used to communicate back to client 
    username -> username of client 
    messagenumber -> requested messagenumber for message which client wants to edit
    timestamp -> The time in which the client posted the message, the client wants to edit
    new_msg -> The new message which will replace original message

    Simple function used to edit message from data and update messagelog.txt
    Errors will be called whenever the timestamp, username and messagenumber does not match and when new_msg is invalid
    """ 
    today = datetime.now()
    if messagenumber.isnumeric() == True and int(messagenumber) <= len(messages):
        messagenumber = int(messagenumber)
        if messages[messagenumber - 1]['date'] == timestamp and messages[messagenumber - 1]['username'] == username and new_msg.isspace() == False: 
            
            messages[messagenumber - 1]["edited"] = "yes"
            today = datetime.now()
            messages[messagenumber - 1]['date'] = str(today.strftime("%d %b %Y %H:%M:%S"))
            string1 = "> Message #{} edited at {}".format(messagenumber, str(today.strftime("%d %b %Y %H:%M:%S")))
            csocket.send((string1 + base_message).encode()) 
            print('> {} edited Message #{} "{}" at {}.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            messages[messagenumber - 1]["message"] = new_msg
        elif messages[messagenumber - 1]['date'] != timestamp:
            csocket.send(("> Invalid Timestamp, try again" + base_message).encode())
            print('> {} attempted to edit Message #{} "{}" at {}. Invalid timestamp.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            return 
        elif messages[messagenumber - 1]['username'] != username:
            csocket.send(("> Authorisation Failed, try again" + base_message).encode())
            print('> {} attempted to edit Message #{} "{}" at {}. Authorisation Failed.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            return
        elif new_msg.isspace() == True: 
            csocket.send(("> Invalid Message, try again" + base_message).encode())
            print('> {} attempted to edit Message #{} "{}" at {}. Invalid Message.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
            return
            
        message_transfer()
    else: 
        csocket.send(("> Invalid Message Number, try again" + base_message).encode())
        print('> {} attempted to edit Message #{} "{}" at {}. Invalid Message Number.'.format(username, messagenumber, messages[messagenumber - 1]["message"], str(today.strftime("%d %b %Y %H:%M:%S"))))
        return

def message_rdm(csocket, username, timestamp): 
    """
    csocket - used to communicate back with client 
    username - username of client 
    timestamp -> the time in which the client requests message to be sent

    Simple function to return the number of messages posted in the server after a certain time.
    Error will be raised whenever the arguements are invalid
    """
    i = 0
    string_sent = ""

    try:
        chosen_time = datetime.strptime(timestamp, "%d %b %Y %H:%M:%S")
    except:
        csocket.send(("> Invalid Timestamp" + base_message).encode())
        print("> {} attempted to issue RDM command. Invalid Timestamp".format(username))
        return
    for message in messages: 
        comp = datetime.strptime(message["date"] , "%d %b %Y %H:%M:%S")
        if chosen_time < comp:
                i = 1
                string1 = '#{}; {}; "{}" posted at {}\n'.format(messages.index(message) + 1, message["username"], message["message"], message['date'])
                string_sent = string_sent + string1
                
    if i == 0: 
        print("> {} issued RDM command".format(username))
        print("> Return messages:")
        csocket.send(("> No new messages" + base_message).encode()) 
        print("No messages")
    else:
        csocket.send(((string_sent.rstrip('\n')) + base_message).encode()) 
        print("> {} issued RDM command".format(username))
        print("> Return messages:")
        print(string_sent)

def user_retrieve(): 
    """
    Function to transport information from credentials.txt into the users list data structure
    """
    with open("credentials.txt", "r") as credentials:
        for line in credentials:
            
            cred_list = line.split()
            user_dict = {
                'username': cred_list[0].strip(),
                'pass': cred_list[1].strip(),
                'banned': False,
                'time': -1, 
                'active': False,
                'success_time': -1,
                'IP': "",
                'UDP_Port': -1, 
                
            }

            users.append(user_dict)

def user_active_post():
    """
    Function used to update the userlog.txt file using server data
    """
    y = 1
    user_log = open("userlog.txt", 'w')
    for user in users: 
        if user["active"] == True: 
            string = "{}; {}; {}; {}; {}\n".format(y, user["success_time"], user["username"], user["IP"], user["UDP_Port"])
            user_log.write(string)
            y += 1

def send_ATU(csocket, username): 
    """
    csocket -> used to communicate with client 
    username -> username of client

    Function used to return active users and information about them 
    """
    user_log = open("userlog.txt", 'r')
    y = 0
    main_string = ""
    for user in users: 
        if user["active"] == True and user["username"] != username: 
            y = 1
            string = "{}; {}; {}; active since {}.\n".format(user["username"], user["IP"], user["UDP_Port"], user["success_time"])
            main_string += string  

    if y == 0: 
        print("> {} issued ATU command".format(username))
        print("> Return active user list:")
        csocket.send(("> No current active users" + base_message).encode())
        print("> No current active users")
    else:
        csocket.send((main_string + base_message).encode())
        print("> {} issued ATU command".format(username))
        print("> Return active user list:")
        print(main_string)

"""
A class thread used to handle incoming commands from client, while still allowing the server to accept requests from other clients
"""

class userThread (threading.Thread):
    def __init__(self, threadID, username, clientSocket):
        """
        threadID -> used to identify thread
        username -> username of client 
        clientSocket -> used to communicate with client
        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.username = username
        self.clientSocket =  clientSocket
    

    def run(self):

        self.clientSocket.send("> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD): ".encode())
        while True:
            
            """
            used to decode messages from client, which are sent as UTF-8
            """
            data1 = self.clientSocket.recv(1024)
            bit_data = data1.decode()
            command = bit_data[0:4].strip()
            
            """
            If statements used to separate between different commands. The information is then passed onto the relevant functions 
            listed at the start of the code
            """

            if command == 'MSG': 
                if not bit_data[4:]:
                    self.clientSocket.send(("> No message supplied, please try again" + base_message).encode())
                else:
                    arguem = bit_data[4:]
                    message_op(self.username, arguem, self.clientSocket)

            elif command == 'DLT': 
                if not bit_data[4:]:
                    self.clientSocket.send(("> Message number not supplied, try again" + base_message).encode())
                elif not bit_data[7:]:
                    self.clientSocket.send(("> Timestamp not supplied, try again" + base_message).encode())
                else:
                    mnumber = bit_data[5]
                   
                    tstamp = bit_data[7:27]
                    message_remove(self.clientSocket, self.username, mnumber, tstamp)
            
            elif command == "EDT":
                if not bit_data[4:]:
                    self.clientSocket.send("> Message number not supplied, try again" + base_message.encode())
                elif not bit_data[26:]:
                    self.clientSocket.send(("> Timestamp not supplied, try again" + base_message).encode())
                elif not bit_data[27:]:
                    self.clientSocket.send(("> Message not supplied, try again" + base_message).encode())
                else:
                    mnumber = bit_data[5]
                   
                    tstamp = bit_data[7:27]
                    msg_new = bit_data[28:]
                    message_edt(self.clientSocket, self.username, mnumber, tstamp, msg_new)

            elif command == "OUT":
                for user in users: 
                    if user["username"] == self.username:
                       
                        user["active"] = False 
                        user_active_post()
                print("> {} logout".format(self.username))
                break

            elif command == "RDM":
                if not bit_data[4:24]:
                    self.clientSocket.send(("> Timestamp not supplied, try again" + base_message).encode())
                else: 
                    tstamp = bit_data[4:24]
                    message_rdm(self.clientSocket, self.username, tstamp)

            elif command == "UPD": 
                info_list = bit_data.split()
                found = 0
                for user in users: 
                    if user["username"] == info_list[1] and user["active"] == True: 
                        self.clientSocket.send(("{} {}".format(user["IP"], user["UDP_Port"])).encode())

                        found = 1
                        time.sleep(1)
                if found == 0: 
                    self.clientSocket.send(("> User not active or does not exist").encode())
                time.sleep(1)
                self.clientSocket.send("> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD): ".encode())
            
            elif command == "ATU": 
                send_ATU(self.clientSocket, self.username)

            else: 
                self.clientSocket.send(("> Invalid Command" + base_message).encode())


          
"""
Below is information used to set up server info
login_attemps -> no. of times a user can fail login, until the user is banned for 10 seconds
"""

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(("localhost",serverPort))
serverSocket.listen(5)
user_retrieve()
login_attempts = int(sys.argv[2])
credentials = open("credentials.txt", "r") 

"""
Simple while loop used to accept incoming TCP connections from clients
"""

while True:

    connectionSocket, addr = serverSocket.accept()        
    while True:
    
        break_off = 0
        
        Username = connectionSocket.recv(1024)
 
        Password = connectionSocket.recv(1024)
  
        
        x = ' '
        Combo = [(Username.decode()).strip(), (Password.decode()).strip()] 
        for user in users:
            """
            checks if client is banned or not. IF not, if the username and pass are correct, the client is passed along to its
            own thread where it can give commands
            """
            if Combo[0] == user["username"] and user["banned"] == True and int(time.time() - user['time']) < 10:
                connectionSocket.send("> Your account is blocked due to multiple login failures. Please try again later".encode())
                break_off = 1
                break

            elif Combo[0] == user["username"] and Combo[1] == user["pass"]:
                connectionSocket.send("> Welcome to TOOM!\n".encode())
                user["UDP_Port"] = (connectionSocket.recv(1024)).decode()
                user["active"] = True
                today1 = datetime.now()  
                user["success_time"] = str(today1.strftime("%d %b %Y %H:%M:%S"))
                user["IP"] = addr[0]
                user_active_post()
                new_user = userThread(1, Username.decode(), connectionSocket)
                new_user.start()
                break_off = 1
                break
            elif Combo[0] == user["username"] and Combo[1] != user["pass"]:
                """
                If the client enters the correct username but incorrect password, he is given login_attemps (int) to correctly enter 
                the password. If the client fails all those times, the client will be banned for 10 seconds. If the client 
                got it correct, the client is passed to a thread where the client can give commands
                """
                failed_attempts = 1
                connectionSocket.send("> Invalid Password. Please try again\n> Password: ".encode())
                while failed_attempts != login_attempts:
                    resent_Password = connectionSocket.recv(1024)
                    resent_Password = (resent_Password.decode()).strip()

                    if resent_Password == user["pass"]: 
                        connectionSocket.send("> Welcome to TOOM!\n".encode())
                        user["UDP_Port"] = (connectionSocket.recv(1024)).decode()
                        user["active"] = True
                        today1 = datetime.now()  
                        user["success_time"] = str(today1.strftime("%d %b %Y %H:%M:%S"))
                        user["IP"] = addr[0]
                        user_active_post()
                        new_user = userThread(1, Username.decode(), connectionSocket)
                        new_user.start()
                        break_off = 1
                        break
                    else:
                        
                        failed_attempts += 1
                        if failed_attempts == login_attempts:
                            user['banned'] = True
                            user['time'] = time.time()
                            connectionSocket.send("> Invalid Password. Your account has been blocked. Please try again later".encode())
                            break_off = 1
                            break
                        connectionSocket.send("> Invalid Password. Please try again\n> Password: ".encode())


                
                break

        if break_off == 1:
            break
        else: 
            connectionSocket.send("> Invalid Login. Please try again\n".encode())

       
serverSocket.close() 