# How to generate self-signed TLS certificates on Windows 11
Secure network communication between coordinator and nodes via WiFi network requires TLS certificates. These self-signed TLS certificates are generated with OpenSSL.
First, in Windows 11, install OpenSSL. Open a command prompt and execute:
`winget install ShiningLightProductions.OpenSSL3.1.0(64-bit)`
Then, add `C:\Program Files\OpenSSL-Win64\bin` to the `Path` under `System variables`. Now, open a new command prompt and check that openssl is reachable by typing `openssl`: you should be able to see a help message

# Generate the Authority Certificates
First, you need to become a certification authority. You will achieve this by generating a self-signed authority certificate:
`openssl genrsa -des3 -out CA.key 4096`
To protect this private certificate, a password is required: use 123456 or something stronger.
Then, generate the public certificate of the certification authority:
`openssl req -new -x509 -nodes -key CA.key -sha256 -days 3650 -out CA.cert.pem`
You will be asked to customize the certificate by providing several details, although these can be left blank.
Then, the public certificate of Certification Authority is required by the node in `der` (binary) format for use in micro-python. Thus:
`openssl x509 -outform der -in CA.cert.pem -out CA_public_certificate.der`

# Generate Coordinator's Certificates
Now, we can start generating the coordinator's certificates. First, the private certificate:
`openssl genrsa -out coordinator.private.key 4096`
Then, the public certificate. You will be asked to provide several details and, while most can be left blank, the `Common Name` must be filled in: during the handshake the client will check the certificate presented by the coordinator matches the "web address". Thus, make sure `naive.coordinator` is passed to `Common Name`:
`openssl req -new -key coordinator.private.key -out coordinator.csr`
Now, you will self-sign the coordinator's public certificate with the Certification Authority's private certificate:
`openssl x509 -req -in coordinator.csr -CAkey CA.key -CA CA.cert.pem -sha256 -days 3650 -CAcreateserial -out signed_coordinator.public.crt`
The coordinator's public self-signed certificate will then be chained with the Certification Authority's public certificate:
`type signed_coordinator.public.crt CA.cert.pem > chained_coordinator_CA.crt`

# Generate Node's Certificate
To achieve the secure communication, the node will also be authenticated by the coordinator. Thus, you will first generate a private certificate:
`openssl genrsa -out node.private.key 4096`
For use in micro-python, the node's private certificate needs to be converted to binary format:
`openssl rsa -in node.private.key -out node.private.der -outform DER`
Then, the public certificate. Again, you will be asked several details, which can be left blank:
`openssl req -new -key node.private.key -out node.csr`
The public certificate will also be signed by the Certification Authority's private certificate:
`openssl x509 -req -in node.csr -CAkey CA.key -CA CA.cert.pem -sha256 -days 3650 -CAcreateserial -out signed_node.public.crt`
And to be used in micro-python, the signed public certificate needs to be converted to binary format:
`openssl x509 -outform der -in signed_node.public.crt -out signed_node.public.der`

# Collect the files
Last step is identifying the files to be used: you have generated plenty of them.
The coordinator will make use of:
- chained_coordinator_CA.crt
- coordinator.private.key
- signed_node.public.crt

`SERVER_PUBLIC_CERTIFICATE = "chained_coordinator_CA.crt"`

`SERVER_PRIVATE_KEY = 'coordinator.private.key'`

`NODE_PUBLIC_CERTIFICATE = 'signed_node.public.crt'`

`context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)`

`context.verify_mode = ssl.CERT_REQUIRED`

`context.load_cert_chain(certfile=SERVER_PUBLIC_CERTIFICATE, keyfile=SERVER_PRIVATE_KEY)`

`context.load_verify_locations(cafile=NODE_PUBLIC_CERTIFICATE)
`

The node will make use of:
- CA_public_certificate.der
- node.private.der
- signed_node.public.der

`SERVER_SNI_HOSTNAME = 'naive.coordinator'`

`NODE_PRIVATE_KEY = 'node.private.der'`

`CA_PUBLIC_CERTIFICATE = "CA_public_certificate.der"`

`NODE_PUBLIC_CERTIFICATE = 'signed_node.public.der'`

`with open(NODE_PUBLIC_CERTIFICATE, 'rb') as node_public_certificate:`
	`node_public_certificate_data = node_public_certificate.read()`

`with open(NODE_PRIVATE_KEY, 'rb') as node_private_key:`
	`node_private_key_data = node_private_key.read()`

`with open(CA_PUBLIC_CERTIFICATE, 'rb') as CA_public_certificate:`
	`CA_public_certificate_data = CA_public_certificate.read()`

`connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)`

`connection.connect(socket.getaddrinfo(COORDINATOR_IP, COORDINATOR_PORT, 0, socket.SOCK_STREAM)[0][-1])`

`ssl_connection = ssl.wrap_socket(connection, server_side = False, key = node_private_key_data, cert = node_public_certificate_data, cadata = CA_public_certificate_data, cert_reqs = ssl.CERT_REQUIRED, server_hostname = SERVER_SNI_HOSTNAME, do_handshake = True)`

`stream_reader = asyncio.StreamReader(ssl_connection)`

`stream_writer = asyncio.StreamWriter(ssl_connection, {})`