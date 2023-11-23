from email import utils
import json
import socket

msgFromClient       = "Hello i am client"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("127.0.0.1", 3000)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
# transform msg from server from string to dict
msgFromServer = msgFromServer[0].decode('utf-8') 
msgFromServer = msgFromServer.replace("'", '"')  # replace single quotes with double quotes
msgFromServer = json.loads(msgFromServer)
msg = "Message from Server {}".format(msgFromServer)

print(msg)