import socket
from _thread import *
from tkinter import *


# Client data processing thread
def threaded(client_socket, addr):
    global chat_log # Set it as a global variable inside the function
    chat_log['state'] = 'normal'   # Set Text widget state to editable state
    chat_log.insert("end", 'Connected by :'+ addr[0] + ':' + str(addr[1]) + '\n')  # Display client IP and port in text widget
    chat_log['state'] = 'disabled'  # Set text widget status to uneditable

    # c in for c in c_list: is the client_socket method 'sendall' of this object.
    # Send to all connected clients
    # The sendall() function is a high-level method and python method.
    # The sendall() function sends all buffer contents of the requested data. If not, an exception is thrown.
    # sendall() also uses send() internally, but just calls send() until all are sent.
    for c in c_list:
        c.sendall(('[System] ' + str(addr[1]) + ' 님이 접속하였습니다.').encode())
    while 1:
        try:
            data = client_socket.recv(1024) # Python code waits until a message is actually received on the socket
            chat_log['state'] = 'normal'    # Set the state of the textwidget to normal
            # Display the received value in the text widget
            chat_log.insert("end", 'Received from ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + str(data.decode()) + '\n')
            chat_log['state'] = 'disabled'  # Set the state of the text widget to disabled

            # for c in c_list:
                # c.sendall((str(addr[1]) + ' : ' + data.decode()).encode())  # Send data to all connected clients
            client_socket.send((str(addr[1]) + ' : ' + data.decode()).encode()) # Send data to the connected client


            st = str(data.decode()) # Convert received data to string
            lst = list(st.split(',')) # Separate each string with a comma and put it in a list
            cnt = len(lst) # number of lists
            for i in range(cnt):
                lst[i] = lst[i].strip() # remove whitespace
                if i == 0:
                    lst[i] = lst[i].upper() # First string is capitalized

            if lst[0] == 'PUT': # -----------PUT
                c_dic[lst[1]] = lst[2] # store key-value in dictionary
            elif lst[0] == 'GET': # -----------GET
                if lst[1] in c_dic: # key value exists in dictionary
                    s = c_dic[lst[1]] # Value corresponding to dictionary key
                    # Send the value corresponding to the key to the client
                    client_socket.send((str(addr[1]) + ' : ' + 'value = '+ s).encode())

                    chat_log['state'] = 'normal' # Display what was sent to the client in a server-side text widget
                    chat_log.insert("end", 'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + s + '\n')
                    chat_log['state'] = 'disabled'
                else: # When a key doesn't exist in the dictionary
                    s = 'none'
                    client_socket.send((str(addr[1]) + ' : ' + 'value = ' + s).encode()) # send no value to client
                    chat_log['state'] = 'normal' # Display what was sent to the client in a server-side text widget
                    chat_log.insert("end", 'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + s + '\n')
                    chat_log['state'] = 'disabled'

            elif lst[0] == 'DELETE': # -----------delete
                if lst[1] in c_dic: # key value exists in dictionary
                    del c_dic[lst[1]] # delete key-value
                    client_socket.send((str(addr[1]) + ' : ' + 'Deleted key value').encode()) # Send delete details to client

                    chat_log['state'] = 'normal' # Display what was sent to the client in a server-side text widget
                    chat_log.insert("end", 'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + 'Deleted key value' + '\n')
                    chat_log['state'] = 'disabled'
                else: # When a key doesn't exist in the dictionary
                    # value does not exist send to client
                    client_socket.send((str(addr[1]) + ' : ' + 'not existed key value').encode())
                    chat_log['state'] = 'normal' # Display what was sent to the client in a server-side text widget
                    chat_log.insert("end", 'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + 'not existed key value' + '\n')
                    chat_log['state'] = 'disabled'

            elif lst[0] == 'LIST': # -----------List
                if len(c_dic): # If at least one dictionary value exists
                    s1 = list(c_dic.keys()) # Convert keys to list
                    s2 = list(c_dic.values()) # Convert the values to a list
                    ln = len(c_dic)
                    s =''
                    for i in range(ln): # Create a string by enumerating the list to be sent to the client with key:value
                        s = s + s1[i] + ':'+ s2[i] + ' '
                    s = s.strip() # remove whitespace

                    client_socket.send((str(addr[1]) + ' : ' +'LIST ' + s).encode()) # Send list to client
                    chat_log['state'] = 'normal' # Display what was sent to the client in a server-side text widget
                    chat_log.insert("end", 'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + 'LIST ' + s + '\n')
                    chat_log['state'] = 'disabled'
                else: # If the dictionary value doesn't exist
                    s = 'none data'
                    client_socket.send((str(addr[1]) + ' : ' +'LIST ' + s).encode()) # send that list doesn't exist to client
                    chat_log['state'] = 'normal' # Display what was sent to the client in the server-side text widget
                    chat_log.insert("end",'Sended to     ' + addr[0] + ' : ' + str(addr[1]) + ' :: ' + 'LIST ' + s + '\n')
                    chat_log['state'] = 'disabled'
            else:
                pass

        except ConnectionResetError as e: # exception handling
            c_list.remove(client_socket)    # Delete client socket on exception
            for c in c_list:
                c.sendall(('[System] '+ str(addr[1]) + ' 님이 나갔습니다.').encode()) # Send deleted client socket information when an exception occurs

            chat_log['state'] = 'normal'    # Set the state of the text widget to the normal state where data can be inserted
            # Display the client socket being deleted as an exception in the text widget
            chat_log.insert("end", 'Disconnected by ' + addr[0] + ':' + str(addr[1]) + '\n')
            chat_log['state'] = 'disabled'
            break
    client_socket.close() # Release the socket when the client disconnects

# Create server connection setup thread when server button is clicked
def server_open():
    # Get the IP and port values of the server from the entry widget, which is a simple one-line text box
    host = ip_entry.get(); port = int(port_entry.get())
    start_new_thread(make_server,(host,port))   # Create a thread waiting for client connection
    open_button['state'] = 'disabled'  # Disable server open button widget state
    ip_entry['state'] = 'readonly'  # IP entry widget status: read only
    port_entry['state'] = 'readonly'  # port entry widget status: read only

# Execute function when close button is clicked
def server_close():
    exit()  # Shut down the window

def make_server(host, port):
    global server_socket    # Set it as a global variable inside the function
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create socket object

    # Needed to resolve WinError 10048 error that the port is busy and cannot be connected
    # Understand this as setting SO_REUSEADDR (Allow binding to ports already in use) of SOL_SOCKET of the server socket to 1 (True)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))   # Bind is an act of connecting a socket, a program interface, and a port, a network resource.

    server_socket.listen()  # listen: This method is a blocking function that waits for a client to connect to the bound port.

    chat_log['state'] = 'normal'   # The default state of the Text widget is NORMAL, which allows the user to edit, add, insert or edit text content.
    chat_log.insert("end", 'Server Start\n')   # insert string at the end
    chat_log['state'] = 'disabled'  # The status of the Text widget is set to disabled such as editing, additional insertion, etc.

    while 1:
        # accept: A socket is a separate object from the initially created socket, and it is a window through which a connection is established with a client to actually send and receive data.
        # client_socket is the first return value, addr is the second return value
        client_socket, addr = server_socket.accept()

        c_list.append(client_socket)   # Add the client_socket object to the list.
        start_new_thread(threaded, (c_list[-1], addr))  # Create a communication processing thread for the requested client socket, the thread argument is c_list last value, address

c_dic = dict()  # Global variable (declared outside the function) creates an empty dictionary and stores the data of the connected client as a dictionary
c_list = [] # Global variable (declared outside the function) creates an empty list, stores all connected client sockets
close = False   # global variable (declared outside the function)
server_socket = None    # global variable (declared outside the function)

s_root = Tk()  # tkinter is a standard Python interface to GUIs and can create Window windows, tkinter.Tk() returns a window instance.
s_root.geometry('500x500')  # set window size
s_root.title('Server')  # set window title name
s_root.resizable(False, False)  # Fix window frame

Label(s_root, text = 'Server IP : ').place(x=20, y=20)  # Create server IP label and set location
Label(s_root, text = 'Port       : ').place(x=20, y=40) # Create server port label and set location

ip_entry = Entry(s_root, width=14, text = '127.0.0.1'); ip_entry.place(x=83, y=21)  # Create server IP entry widget and set location
ip_entry.insert(0, '127.0.0.1')  # Insert server IP entry widget value
port_entry = Entry(s_root, width=5, text = '9999'); port_entry.place(x=83, y=42) # Create port entry widget and set location
port_entry.insert(0, '8000') # Insert value of port entry widget
open_button = Button(s_root, text = 'Server Open', command=server_open); open_button.place(x=380, y=18)   # Create open button widget and set its location

chat_log = Text(s_root, width=65, height=29, state = 'disabled', spacing2=2); chat_log.place(x=20, y=80) # Create text widget and set its location

close_button = Button(s_root,text = 'Server Close', command=server_close); close_button.place(x=380, y=45)  # Create a close button widget and set its location
# Create widgets in multiple modules, not behind the Tkinter code, set triggers, and use them at the end of the execution flow to 'keep waiting' for user input
s_root.mainloop()