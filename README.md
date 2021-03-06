# Python-Client-Server-Program
    Program Design
        The client.py program and the server.py program were both implemented using Python 3.7. 
    Client.py:
        The file does not rely on any other files only requirement is user input
    Server.py:
        This file requires the credentials.txt file in order to authorise connecting clients. It will also create 2 
        separate files, userlog.txt and messagelog.txt, used to store information about clients and server 
        data. These 2 files will be cleared each time a server start and will not persist data. 
    Application Layer Message Format
        Messages are transferred between Clients and the Server in simple UTF-8 encoding. This was 
        selected as it was very easy to implement and does not require a large amount of data compared to 
        other Application Layer Message format’s including JSON format. Simple loops where implemented 
        on both ends so that after a response is received, a message would be sent back. In the case the 
        response from the client was empty or only contained operators such as newlines or tabs, the client 
        would output a ‘try again’ message and not send the response. The UTF-8 messages received at both 
        ends will then be decoded into ASCII by the respective program and in most cases presented to the 
        reader in an appropriate format. 
# Brief Description
    Server:
        The server program works through the command:
        Python3.7 server.py {server_port} {number_of_consecutive_failed_attempts}
        Once this command is given, the server will initiate a TCP socket used to listen to incoming requests 
        on the given port, ‘server port’. There is no timeout when listening for requests and the maximum 
        number of requests the server can hold in it’s buffer is 5. Once the server establishes a TCP 
        connection with a client, it will invoke the login process. The client will supply its credentials and the 
        server will check them by comparing them to the data given in credentials.txt. The client is able to 
        login and unlimited amount of time, being that both the username and password supplied by the 
        client is incorrect. If the client provides the right username however the wrong password, a 
        security measure will initiate giving the client {number_of_consecutive_failed_attempts} to get 
        the right password. If the client fails all these attempts he is blocked and any client trying to login 
        with that username afterwards will also be blocked for 10 seconds, regardless of the IP. 
        Once the user is able to successfully login, a new thread is created to handle the incoming 
        commands from that client, while also allowing the server to listen for incoming connections. This is 
        a very simple implementation of threads and is done by using the ‘threading’ module from python. 
        Every authorised client will be supplied their own threading class where they can input and send as 
        many commands they want. 
        For handling the messages the server stores a simple list data structure is used:
        messages = []
        Where every element in that ‘messages’ list is a dictionary in the form: 
        new_dict = {
        'date': date, #Date in which message is posted 
        'username': username, #Username of user who posted message (supplied 
        MSG command)
        'message': message, #message itself, a string 
        'edited': edited #’Yes’ or ‘No’ to know if message has been edited or 
        not
        }
        Similarly information about users is stored as: 
        users = []
        Where every element in that list is a dictionary: 
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
    Client
        The client works by first sending the server a TCP connection. It then initiates the login process 
        handling all the scenarios given in the spec. Once the login procedure is finished, it will begin the 
        command process, where it converts input from the user into UTF-8 and sends it to the server. The 
        client program also handles the uploading of files using UDP packets. After each time a client is able 
        to login successfully, a new thread class using the ‘threading’ module is allocated for listening to UPD 
        packets uploaded by another client. This is useful as it allows the client to still communicate with the 
        server even when it is downloading a video file. Also, each time a client wants to upload a video to 
        another active client, it first communicates with the server to find information about active clients 
        and once authorised sends the file through UDP packets on a new thread. This is so that the client 
        can communicate with the server still while uploading. Once the client send the ‘OUT’ command, it 
        will end both threads no matter what and close the program. 
# Trade-offs
    1. The server can only handle 5 clients logging in at a time. It does not support simultaneous 
    logins and will not work. It will process each TCP connection 1 at a time, meaning if 1 person 
    logs in and then another, the second person cannot supply their credentials until the first 
    person has 
    2. Program can only run on python3.7 and onwards
    3. The P2P connection is not always reliable due to UDP. Videos received by clients may be of 
    poor quality, whenever the connection is congested.
# Improvements/Extensions
    1. Spam Prevention. Code can be simply implemented to prevent a user from spamming 
    the server with messages. This can be done by measuring the amount of messages a 
    user posts in a given timeframe, and if the user goes over, the user will be given a 
    warning. Further warnings will cause a ban 
    2. Offensive Filter. Any messages which contain swear words or common insults can be 
    blocked from being posted on the server. This can be done by having a file which 
    contains offensive words and phrases, and every message wanting to be posted can be 
    checked with in the file.
    3. Global access. The code can be deployed on a data server making it accessible from 
    anywhere in the world. A frontend can then be built so that users can access the 
    program through their browsers or as a program. 
    4. Multi-processing. Currently multi-threading is used, however this does not allow users to 
    concurrently login and be concurrently served. This can be implemented using Pythons 
    Multi-processing module. Also, a new way to handle data must also be implemented to 
    support multi-processing.
    5. A better system of authorisation. Passwords and username don’t have many restrictions. 
    One of the possible restrictions which can be used to improve security is to make special 
    characters and upper case characters mandatory for passwords. 
    6. Register feature