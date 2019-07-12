from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct
from detector.processor import getCustomPulseApp
import numpy as np
import zlib
import cv2
import base64
import calendar
import time

HOST = "192.168.2.40"# input("Enter Host IP\n")
PORT = 3000
lnF = 640*480*3
CHUNK = 1024

class Server:

    def __init__(self):
        args = {
            "serial":None,
            "baud":None,
            "udp":None
        }
        self.pulse = getCustomPulseApp(args)
        
        self.addresses = {}
        self.threads = {}

    def Connections(self):
        while True:
            try:
                client, addr = server.accept()
                print("{} is connected!!".format(addr))
                self.addresses[client] = addr
                if len(self.addresses) >= 1:
                    for sockets in self.addresses:
                        if sockets not in self.threads:
                            self.threads[sockets] = True
                            sockets.send(("start").encode())
                            Thread(target=self.RecieveMedia, args=(sockets, )).start()
                else:
                    continue
            except:
                continue

    def ClientConnection(self,client):
        while True:
            try:
                lengthbuf = self.recvall(client, 4)
                length, = struct.unpack('!I', lengthbuf)
                self.recvall(client, length)
            except:
                continue

    def RecieveMedia(self,client):
        while True:
            try:
                lengthbuf = self.recvall(client,4)
                length, = struct.unpack('!I', lengthbuf)
                b64 = self.recvall64(client,length)
                file = 'image'+time.strftime("%H%M%S")+'.png'
        #        with open(file,"wb") as fh:
        #            fh.write(base64.decodebytes(b64))
                print("Recieving Media..")
                img = base64.b64decode(b64)
                print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))
                img_array = np.array(img, dtype = np.uint8)
                frame = cv2.imdecode(img_array, 1)
                self.pulse.process(frame)
            except Exception as e:
                print(e)
                continue

    def RecieveMediax(self,client):
        while True:
            try:
                lengthbuf = self.recvall(client,400)
                length, = struct.unpack('!I', lengthbuf)
                databytes = self.recvall(client,length)
                img = zlib.decompress(databytes)
                if len(databytes) == length:
                    print("Recieving Media..")
                    print("Image Frame Size:- {}".format(len(img)))
                    img = np.array(list(img))
                    img_array = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                    frame = cv2.imdecode(img_array, 1)
                    self.pulse.process(img_array)
                else:
                    print("Data CORRUPTED")
            except Exception as e:
                print(e)
                continue

    def broadcast(self, clientSocket, data_to_be_sent):
        try:
            self.processVideo(clientSocket, data_to_be_sent)
        except Exception as e:
             print(e)
       # for client in self.addresses:
       #     if client != clientSocket:
       #         client.sendall(data_to_be_sent)

    def processVideo(self, clientSocket, data_to_process):
        img = zlib.decompress(data_to_process)
        if len(data_to_process) == length:
            print("Recieving Media..")
            print("Image Frame Size:- {}".format(len(img)))
            img = np.array(list(img))
            img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
            frame = cv2.imdecode(img_array, 1)
            self.pulse.process(frame)
        else:
            print("Data CORRUPTED")

    def recvall(self, client, size):
        databytes = b''
        while len(databytes) != size:
            to_read = size - len(databytes)
            if to_read > (1000 * CHUNK):
                databytes += client.recv(1000 * CHUNK)
            else:
                databytes += client.recv(to_read)
        return databytes

    def recvall64(self, client, size):
        databytes  = b''
        while len(databytes) != size:
            to_read = size - len(databytes)
            if to_read > (1000 * CHUNK):
                databytes += client.recv(1000 * CHUNK)
            else:
                databytes += client.recv(to_read)
        return databytes

    def recvallx(self, client, BufferSize):
            databytes = b''
            i = 0
            while i != BufferSize:
                to_read = BufferSize - i
                if to_read > (1000 * CHUNK):
                    databytes = client.recv(1000 * CHUNK)
                    i += len(databytes)
                    self.broadcast(client, databytes)
                else:
                    if BufferSize == 4:
                        databytes += client.recv(to_read)
                    else:
                        databytes = client.recv(to_read)
                    i += len(databytes)
                    if BufferSize != 4:
                        self.broadcast(client, databytes)
            print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
            if BufferSize == 4:
                self.broadcast(client, databytes)
                return databytes
if __name__ == "__main__":
    App = Server()
    server = socket(family=AF_INET, type=SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
    except OSError:
        print("Server Busy")

    server.listen(2)
    print("Waiting for connection..")
    AcceptThread = Thread(target=App.Connections)
    AcceptThread.start()
    AcceptThread.join()
    server.close()
