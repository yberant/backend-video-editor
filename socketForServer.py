import os
import socket


STR_FORMAT = "utf-8"
PORT = 4443
IP = socket.gethostbyname(socket.gethostname())
ADRESS = (IP, PORT)
MEDIA_DIR = "media"

#corre en servidor y recibe requests de otro servidor
class SocketForServer:

    def __init__(self):
        self.media_dir = MEDIA_DIR

        while True:

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self.server.bind(ADRESS)
                print("escuchando")
                self.server.listen()
                conn, _ = self.server.accept()
                print(f"socket conectado con otro servidor")

                #recibo mensaje de entrada
                req_msg = conn.recv(100).decode(STR_FORMAT)
                if req_msg == "SERVER_CLI::U THERE":
                    pass

            except:
                print("conexión fallida")
                self.server.close()

