import socket
import ssl
import sys
import argparse

# Change here the default values
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, help='Port to connect to', default=9999)
parser.add_argument('--password', type=str, help='Pre-shared key', default="123456789")
parser.add_argument('--private-key-path', type=str, help='Server\'s key path', default="key.pem")
parser.add_argument('--public-key-path', type=str, help='Server\'s certificate path', default="cert.pem")

args = parser.parse_args()

class SocketServer:
    """
    A simple socket server that binds to a specified host and port,
    accepts one connection, and sends commands to the connected client.
    """
    def __init__(self, host="0.0.0.0", port=args.port):
        """
        Initialize the server with a host and port.
        Initializes the TLS context
        """
        self.host = host
        self.port = port
        self.socket = None

        self.tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.tls_context.load_cert_chain(certfile=args.public_key_path, keyfile=args.private_key_path) 

    def create_socket(self):
        """
        Create the socket for the server.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket created successfully.")
        except socket.error as error:
            print(f"Socket creation error: {error}")
            sys.exit(1)

    def bind_socket(self):
        """
        Bind the socket to the host and port, and start listening for connections.
        """
        try:
            print(f"Binding to port: {self.port}")
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print("Socket is now listening for connections.")
        except socket.error as error:
            print(f"Socket binding error: {error}")
            sys.exit(1)

    def accept_connection(self):
        """
        Accept an incoming connection and handle communication.
        """
        try:
            conn, address = self.socket.accept()
            print(f"Connection established with IP: {address[0]} on Port: {address[1]}")
            # Use TLS context from before
            conn = self.tls_context.wrap_socket(conn, server_side=True)
            print("TLS Handshake completed.")
            # Client auth
            self.check_client_password(conn)

            # Handle Ctrl+C, Ctrl+D
            try:
                self.send_commands(conn)
            except KeyboardInterrupt:
                print("Exiting.")
                self.socket.close()
            except EOFError:
                print("Exiting.")
                self.socket.close()

            conn.close()
        except socket.error as error:
            print(f"Error accepting connection: {error}")

    def send_commands(self, conn):
        """
        Send commands to the connected client.
        Type 'quit' to end the session.
        """
        while True:
            command = input("Enter command: ")
            if command.lower() in ["quit", "exit"]:
                print("Closing connection and shutting down server.")
                conn.close()
                self.socket.close()
                sys.exit(0)
            elif command.strip():
                try:
                    conn.send(command.encode())
                    client_response = conn.recv(1024).decode('utf-8')
                    print(client_response, end="")
                except socket.error as error:
                    print(f"Error during communication: {error}")
                    conn.close()
                    break

    def check_client_password(self, conn):
        """
        After the TLS handshake, the first thing the client needs to do is to
        send the PSK. If incorrect, connection is closed.
        """
        psk = conn.recv(1024).decode()
        if psk != args.password:
            conn.close()
            self.socket.close()
            raise Exception("Invalid PSK. Is the client the real one? Exiting.")
        print("Client authenticated correctly using PSK.")

def main():
    server = SocketServer()
    server.create_socket()
    server.bind_socket()

    # Handle Ctrl+C, Ctrl+D
    try:
        server.accept_connection()
    except KeyboardInterrupt:
        print("Exiting.")
        server.socket.close()
    except EOFError:
        print("Exiting.")
        server.socket.close()

if __name__ == "__main__":
    main()
