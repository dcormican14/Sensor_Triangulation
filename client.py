import socket
import errno
import sys
import pickle
import time

# Data received from the server is found in the format:
# Username Length >> Username >> Message length >> Message


class Client:
    def __init__(self, h_len=10, server_hostname=socket.gethostname(), port=8887, u_name="unspecified"):
        self.HEADER_LENGTH = h_len
        self.IP = socket.gethostname()
        self.PORT = port
        self.my_username = u_name
        self.server_hostname = server_hostname
        self.data = "Test"

        # Create a client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size,
        # that we encode to bytes as well
        self.username = self.my_username.encode('utf-8')
        self.username_header = f"{len(self.username):<{self.HEADER_LENGTH}}".encode('utf-8')

    def set_data(self, new_data="Test"):
        self.data = new_data
        return self.data

    def toggle_on(self, toggle_on=True):
        if toggle_on:
            # start sending from client socket
            self.client_socket.connect((self.server_hostname, self.PORT))
            self.client_socket.setblocking(False)
            # self.client_socket.settimeout(5)
            self.client_socket.send(self.username_header + self.username)
        else:
            self.client_socket.close()

    def send(self, local_data="Test"):
        # Wait for user to input a message
        message = pickle.dumps(self.set_data(local_data))  # input(f'{self.my_username} > ')

        # If message is not empty - send it
        if message:
            # Encode message to bytes with header
            # message = message.encode('utf-8')
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)

        try:
            # Loops over received messages
            while True:
                # Receive and decode the header (length of username and username of data)
                username_header = self.client_socket.recv(self.HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')

                # Receive and decode the message (anything after username is the sent data)
                message_header = self.client_socket.recv(self.HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')

                # Print message and username
                print(f'{username} > {message}')

        # Handles exceptions as errors and displays the error
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # This triggers when nothing is received
        except Exception as e:
            # Any other exception - something happened, exit
            print(f'Reading error: '.format(str(e)))
            sys.exit()


# EXAMPLE CODE FOR CONSTRUCTING AND RUNNING A CLIENT.
#
# c=Client(h_len=10,
#          server_hostname="DylanPC",
#          port=8887,
#          u_name="Test",)
# c.toggle_on()
# while True:
#     t = time.time()
#     c.send(local_data=str(t))
#     time.sleep(1)
