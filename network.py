import json
import socket


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.2.104"
        self.port = 3000
        self.addr = (self.server, self.port)
        self.bufferSize = 16384
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, data: str):
        try:
            bytesToSend = str.encode(data)
            # Send to server using created UDP socketa
            self.UDPClientSocket.sendto(bytesToSend, self.addr)

            msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
            # transform msg from server from string to dict
            msgFromServer = msgFromServer[0].decode('utf-8')
            msgFromServer = msgFromServer.replace("'", '"')  # replace single quotes with double quotes
            msgFromServer = msgFromServer.replace('"{', '{')  # replace single quotes with double quotes
            msgFromServer = msgFromServer.replace('}"', '}')  
            msg: dict = json.loads(msgFromServer)
            return msg
        except socket.error as e:
            print(e)
            return None