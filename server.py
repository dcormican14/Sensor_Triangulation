import socket
import select
import pickle
import time

class Server:
    def __init__(self, h_len=10, port=8887):
        self.HEADER_LENGTH = h_len
        self.IP = socket.gethostname()
        self.PORT = port

        # Create a server Socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # List of sockets for select.select()
        self.sockets_list = [self.server_socket]

        # List of connected clients - socket as a key, user header and name as data
        self.clients = {}

    # Handles message receiving
    def receive_message(self, client_socket):
        try:
            # Receive our "header" containing message length, it's size is defined and constant
            self.message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(self.message_header):
                return False
            message_length = int(self.message_header.decode('utf-8').strip())
            return {'header': self.message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def toggle_on(self, toggle_on=True):
        if toggle_on:
            # For a server using 0.0.0.0 means to listen on all available interfaces, useful to
            # connect locally to 127.0.0.1 and remotely to LAN interface IP
            self.server_socket.bind(('', self.PORT))
            self.server_socket.listen()
            print(f'Listening for connections on {self.IP}:{self.PORT}...')
        else:
            self.server_socket.close()
            print(f'socket on {self.IP}:{self.PORT} is closed')

    def listen(self):
        read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
        # Iterate over notified sockets
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                # Accept new connection
                client_socket, client_address = self.server_socket.accept()
                # Client should send his name right away, receive it
                user = self.receive_message(client_socket)

                # Checks for disconnect
                if user is False:
                    continue

                # Save user data
                self.sockets_list.append(client_socket)
                self.clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
            # Else existing socket is sending a message
            else:
                # Receive message
                message = self.receive_message(notified_socket)

                # If False, client disconnected, cleanup
                if message is False:
                    print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))

                    # Cleanup user data
                    self.sockets_list.remove(notified_socket)
                    del self.clients[notified_socket]
                    continue

                # Get user data
                user = self.clients[notified_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {pickle.loads(message["data"])}')

                # Iterate over connected clients and broadcast message to users
                for client_socket in self.clients:
                    # But don't sent it to sender
                    if client_socket != notified_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        # It's not really necessary to have this, but will handle some socket exceptions just in case
        for notified_socket in exception_sockets:
            # User data cleanup
            self.sockets_list.remove(notified_socket)
            del self.clients[notified_socket]


# EXAMPLE CODE FOR CONSTRUCTING AND RUNNING A SERVER.
# 
# s=Server(h_len=10,
#          port=8887,)
# s.toggle_on()
# while True:
#     s.listen()
