import socket
import os
import sys
from typing import final
import paramiko
from concatter import Concatter
from segmentFinder import DATE_FORMAT, SegmentFinder
from datetime import datetime, timedelta
#from pydub import AudioSegment
from ffprobe import FFProbe

from dotenv import load_dotenv


load_dotenv()


#durante test de serv-serv. este se corre en windows

PORT=os.getenv("PORT")#7555
STR_FORMAT = "utf-8"
DATE_FORMAT = "%Y-%m-%d %H-%M-%S"
#TODO: CAMBIAR POR socket.gethostbyname(socket.gethostname())
IP = os.getenv("IP")#sys.argv[1] #"172.17.202.149"#socket.gethostbyname(socket.gethostname())
ADRESS = (IP, PORT)
#TODO: ACTUALMENTE COMO SE TRABAJA EN LOCAL SE USA OTRA CARPETA MEDIA PARA SIMULAR LOS ARCHIVOS LOCALES DE OTRO SERVIDOR REMOTO (EN COMUNICACIÓN SERVIDOR). CAMBIAR A MEDIA PARA FUTURO
MEDIA_DIR = os.getenv("MEDIA_DIR")#"media2" 
#TODO: VER TEMA DE SEGURIDAD CON ESTO 
MIRROR_PASS_SSH = os.getenv("MIRROR_PASS_SSH")
MIRROR_USER_SSH = os.getenv("MIRROR_USER_SSH")
MIRROR_PORT_SSH = os.getenv("MIRROR_PORT_SSH")

#TODO: CAMBIAR ESTO. IP DESDE CUAL SE RECIBIRÁ SOLICITUDES DE SEGMENTOS Y A LA CUAL HAY QUE MANDAR
MIRROR_IP = "192.168.169.243"#socket.gethostbyname(socket.gethostname())#"172.17.202.149"

class Main:

    def closeConnection(self):
        if self.conn != None:
            self.conn.shutdown(0)
            self.conn.close()
            #self.serverSocket.close()
            print("conexión cerrada")


    def __init__(self):
        
        self.conn = None

        while True:

            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                print(f"vinculando dirección: {ADRESS}")
                self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.serverSocket.bind(ADRESS)
                print(f"escuchando desde dirección: {ADRESS}")

                self.serverSocket.listen()


                conn, _= self.serverSocket.accept()
                self.conn = conn
                print(f"socket conectado")

            except Exception as E:
                print("conexión fallida: ",str(E))
                self.closeConnection()
                continue

            try:

                #recibo mensaje de entrada
                req_msg = self.conn.recv(100).decode(STR_FORMAT)
                #mensaje debe ser CLI::HELLO  o SERV::HELLO
                if len(req_msg.split("::")) != 2:
                    serv_msg = "INVALID"
                    self.conn.send(serv_msg.encode(STR_FORMAT))
                    self.closeConnection()
                    continue

                requestor, req_message = req_msg.split("::")
                if req_message != "HELLO":
                    serv_msg = "INVALID MESSAGE"
                    self.conn.send(serv_msg.encode(STR_FORMAT))
                    self.closeConnection()
                    continue

                if requestor == "CLIENT":
                    print("conectado con cliente")
                    self.handleClient()
                elif requestor == "SERVER":
                    print("conectado con otro servidor")
                    self.handleServer()
                else:
                    serv_msg = "INVALID REQUESTOR"
                    self.conn.send(serv_msg.encode(STR_FORMAT))
                    self.closeConnection()

            except Exception as E:
                print("conexión interrumpida por un error ",E)
                self.closeConnection()
                continue

            

    def handleClient(self):
        res_msg = "OK"
        self.conn.send(res_msg.encode(STR_FORMAT))
        print("!!!")
        #espero la query con segmento solicitado
        files_msg = self.conn.recv(2000).decode(STR_FORMAT) # TODO: DISCUTIR EL TAMAÑO DEL BUFFER?
        print("mensaje de solicitud de archivos segmento")

        if len(files_msg.split("::")) != 4:
            res_msg = "INVALID REQUEST FORMAT"
            self.conn.send(res_msg.encode(STR_FORMAT))
            self.closeConnection()
            return

        else:
            res_msg = "WORKING"
            self.conn.send(res_msg.encode(STR_FORMAT))

        '''
        name = "Adn.air.cl"
        timestamp_start = "2022-09-01 23-40-00"
        timestamp_end = "2022-09-02 03-40-00"
        extention = "mp3"
        '''
        segmentFinder = SegmentFinder()#FileRequester()


        channel_name, timestamp_start, timestamp_end, extention = files_msg.split("::")
        segments = segmentFinder.get_media(channel_name, extention,timestamp_start,timestamp_end)

        requested_duration = str(datetime.strptime(timestamp_end, DATE_FORMAT) - datetime.strptime(timestamp_start, DATE_FORMAT))

        
        concatter = Concatter()
        file_name = f"{channel_name}_{timestamp_start}_{timestamp_end}.{extention}"
        file_dir = concatter.concatSegments(channel_name, segments, file_name)

        print("concatenado archivo: ",file_name)    

        if file_dir != None:
            #print("a")
            file_size =  os.stat(file_dir).st_size/(1024*1024)

            segments_indicators = []
            for segment in segments:
                if segment['location'] == "local":
                    segments_indicators.append(f"{segment['time_start']}_{segment['time_start']}")
            #print("b")
            segments_string = "__".join(segments_indicators)

            #print("c")
            duration = FFProbe(file_dir).metadata['Duration']

            final_msg = f"VIDEO CONCATED::{file_name}::{file_size}::{duration}/{requested_duration}::{segments_string}"
            

        else:
            final_msg = "ERROR: COULDNT CONCAT SEGMENTS"

        print("enviando mensaje de cierre", final_msg)
        self.conn.send(final_msg.encode(STR_FORMAT))

        self.closeConnection()
        



        #espero la query con segmento solicitado
    #se comunica con servidopr para enviar archivos
    def handleServer(self):
        res_msg = "OK"
        self.conn.send(res_msg.encode(STR_FORMAT))

        #espero la query con archivos solicitados
        files_msg = self.conn.recv(4000).decode(STR_FORMAT) # TODO: DISCUTIR EL TAMAÑO DEL BUFFER?
        print("mensaje de solicitud de archivos recibido")

        #chequeo si el formato está correcto
        for file_data in files_msg.split("::")[1:]:
            if len(file_data.split("__")) != 2:#formato incorrecto
                res_msg = "INVALID REQUEST FORMAT"
                self.conn.send(res_msg.encode(STR_FORMAT))
                self.closeConnection()
                return

        channel_name =  files_msg.split("::")[0]


        #mando un working
        res_msg = "WORKING"
        self.conn.send(res_msg.encode(STR_FORMAT))


        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=MIRROR_IP, username=MIRROR_USER_SSH, password=MIRROR_PASS_SSH, port=MIRROR_PORT_SSH)

        
        sftp_client = ssh.open_sftp()
        print(sftp_client)

        transfered_files = []

        for file_data in files_msg.split("::")[1:]:
            file_name, file_dst_dir = file_data.split("__")
            

            #reviso si el archivo solicitado está en este servidor
            file_dir_local = os.path.join(os.path.join(MEDIA_DIR, channel_name), file_name)
            print("revisando si está: ",file_dir_local)
            if os.path.exists(file_dir_local):
                print("transfiriendo a ",file_dst_dir)
                #sftp_client.get(file_dir_local,file_dst_dir)
                sftp_client.put(file_dir_local, file_dst_dir)
                transfered_files.append(file_name)

        sftp_client.close()
        ssh.close()

        done_msg = f"FILES TRANSFERED::{'__'.join(transfered_files)}"
        self.conn.send(done_msg.encode(STR_FORMAT))
        print("listo, cerrando conexión")
        self.closeConnection()




                
                
            
        

if __name__ == "__main__":
    Main()

'''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname="172.17.195.77", username="yoelgu",password='123yoel',port=22)
    
    sftp_client = ssh.open_sftp()
    #TODO: CAMBIAR ESTO OARA CUANDO SE MONTE A SERVIDOR

    server_media_dir = "/mnt/c/users/yoelg/Desktop/pega - Izimedia/backend editor video/mediaserver2/media"
    sftp_client.chdir(server_media_dir)

    tmp_dir = os.path.join(os.getcwd(), "tmp")#TODO: CAMBIAR ESTO TAMBIÉN?.
    
    sftp_client.get("algo.txt",os.path.join(tmp_dir, "algo.txt"))

    sftp_client.close()
    ssh.close()

'''