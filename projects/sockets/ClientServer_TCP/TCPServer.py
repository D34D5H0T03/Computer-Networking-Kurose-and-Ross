from socket import *

serverPort = 12000

# SOCK_STREAM Denotes TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind to port 12000
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
        sentence = connectionSocket.recv(2048)
        modifiedSentence = sentence.decode().upper()
        
        connectionSocket.send(modifiedSentence.encode())
        connectionSocket.close()
        
except KeyboardInterrupt:
    print("\nServer Shutting down...")
    serverSocket.close()
