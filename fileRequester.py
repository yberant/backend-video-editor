import paramiko
import socket
import os

STR_FORMAT = "utf-8"

#TODO: CAMBIAR ESTO PARA CUANDO SE HAGA DEPLOY. ¿SEGURIDAD?
MIRROR_IP = os.getenv("MIRROR_IP")#"192.168.1.10"# #socket.gethostbyname(socket.gethostname()) #"172.17.202.149" 
MIRROR_PORT = os.getenv("MIRROR_PORT")#7555
MEDIA_FOLDER = os.getenv("MEDIA_DIR")#"media"

#TODO: pedirle al socket del servidor cosas

class FileRequester:

    def __init__(self,tmp_dir="tmp"):
        self.tmp_dir = tmp_dir


    #setea una conexión a otro servidor. También se autentica siguiendo un protocolo
    def setConnection(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        adress = (MIRROR_IP, MIRROR_PORT)
        try:
            conn.connect(adress)
            print("socket conectado, enviando mensaje de entrada")

            #mensaje de entrada
            msg = "SERVER::HELLO"
            conn.send(msg.encode(STR_FORMAT))

            #recibo respuesta
            response = conn.recv(100).decode(STR_FORMAT)
            print(f"recibida respuesta: {response}")

            if response != "OK":
                print("acceso denegado")
                conn.close()
                exit()

            print("conectado a servidor")

            self.conn = conn
            return self.conn

        except:
            print("conexión fallida")
            return None

    #cierra la conexión
    def closeConnection(self):
        if self.conn != None:
            self.conn.close()

    #recibo una lista de diccionarios, reviso si están en el otro servidor
    def askForRemotes(self,remotes, channel_name):
        #asumiendo que ya recibí el OK del servidor, tengo que armar la query de solicitud de archivos
        query_items = []
        current_dir = os.getcwd()
        media_dir = os.path.join(current_dir,MEDIA_FOLDER)
        media_dir = os.path.join(media_dir, channel_name)
        for remote in remotes:
            file_name = remote["file_name"]
            target_dir = os.path.join(media_dir, file_name) #donde debería estar a futuro el archivo (en el servidor desde el cual se está pidiendo el archivo)
            query_items.append(f"{file_name}__{target_dir}")

        #el mensaje empieza con el nombre del canal
        query = channel_name+"::"
        query += "::".join(query_items)
        print("enviando query: ",query)
        #mando la query con los archivos solicitdos
        self.conn.send(query.encode(STR_FORMAT))

        transfered_files = []

        #recibo working (se supone xd)
        serv_msg = self.conn.recv(100).decode(STR_FORMAT)
        if serv_msg == "WORKING":
            #espero a la respuesta
            print("esperando respuesta")
            res_msg = self.conn.recv(4000).decode(STR_FORMAT)
            msg, files_data_str = res_msg.split("::")
            files_data = files_data_str.split("__")
            if len(files_data) > 0: #se lograron transferir algunos archivos
                for file_data in files_data:
                    transfered_files.append(file_data)
            print("archivos transferidos")
            self.conn.close()
            return transfered_files

if __name__ == "__main__":

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
    fileRequester = FileRequester()
    fileRequester.setConnection(socket.gethostbyname(socket.gethostname()),4444)

    