from socket import *

def requestParser(httpRequest):
    # split header from body
    header, body = httpRequest.split("\r\n\r\n", 1)
    # split individual lines
    header_lines = header.split("\r\n")
    # get the path
    requestLine = header_lines[0]
    method, path, version = requestLine.split(" ", 2)
    
    # get filename
    filename = path.split("/", 1)[-1]
    
    # fallback
    if filename == "":
        filename = "index.html"
        
    return filename

def responseCrafter(filename : str) -> bytes:
    try:
        with open(filename, 'rb') as f:
            body = f.read()
            status_line = b"HTTP/1.1 200 OK\r\n"
    except FileNotFoundError:
        body = b"<h1>404 Not Found</h1>"
        status_line = b"HTTP/1.1 404 Not Found\r\n"
        
    headers = (
        b"Content-Type: text/html; charset=utf-8\r\n" +
        f"Content-Length: {len(body)}\r\n".encode('utf-8') +
        b"Connection: close\r\n\r\n"
    )
    
    response = status_line + headers + body
    
    return response
    
        
serverPort = 8080

# SOCK_STREAM Denotes TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

# telling os that the port is immedietly reusable
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Bind to port 8080
serverSocket.bind(('', serverPort))

# TCP requires listening for incoming connection. the 1 parameter defines maximum queued connection
serverSocket.listen(1)

print("TCP Server ready to recieve...")

try:
    while True:
        # This part performs the TCP handshake (SYN, SYN-ACK, ACK), then returns a new socket and address
        connectionSocket, addr = serverSocket.accept()
        print(f"Connection established with {addr}")
        
        # we use recv with an established connection
        incoming = connectionSocket.recv(2048)
        if not incoming:
            connectionSocket.close()
            continue
            
        httpRequest = incoming.decode()
        print(httpRequest)
        
        file = requestParser(httpRequest)
        response = responseCrafter(file)
        
        connectionSocket.sendall(response)
        connectionSocket.close()
        
except KeyboardInterrupt:
    print("\nServer Shutting down...")
    serverSocket.close()
