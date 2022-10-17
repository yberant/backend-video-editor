import os
import socket
import time
import tqdm
import sys


#TODO: VER TEMA DE PUERTO. QUIZÁS CON ENTORNOS?
SERVER_PORT=7555
#TODO: VER ESTO TAMBIÉN
SERVER_IP_1 = "192.9.201.76"
SERVER_IP_2 = "192.168.1.10"
STR_FORMAT = "utf-8"


CHANNEL = "40Principales.air.cl"#sys.argv[1]
TIMESTAMP_START = "2022-10-17 03-40-00"#sys.argv[2]
TIMESTAMP_END= "2022-10-17 05-10-00"#sys.argv[3]
EXTENTION = "mp3"#sys.argv[4]

SERVER_ADRESS_1 = (SERVER_IP_1, SERVER_PORT)
SERVER_ADRESS_2 = (SERVER_IP_2, SERVER_PORT)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    client.connect(SERVER_ADRESS_1)
    print("socket conectado")

except:
    print("conexión fallida")
    exit(0)

#mensaje de seguridad 1
cli_msg = "CLIENT::HELLO"
client.send(cli_msg.encode(STR_FORMAT))

#recivo OK o DENIED
serv_msg = client.recv(100).decode(STR_FORMAT)
print(f"recibido mensaje de servidor: {serv_msg}")

if serv_msg != "OK":
    print("solicitud no aceptada")
    exit()

if serv_msg:

    #pido segmento
    print("pidiendo segmento")
    cli_msg = f"{CHANNEL}::{TIMESTAMP_START}::{TIMESTAMP_END}::{EXTENTION}"
    client.send(cli_msg.encode())

    #recibo working (si todo sale bien)
    serv_msg = client.recv(100).decode(STR_FORMAT)
    if serv_msg == "WORKING":
        print("esperando")
        final_msg = client.recv(1000).decode(STR_FORMAT)
        print("final msg: ",final_msg)
        client.close()
        #pass#TODO: SEGUIR CON ESTO
    else:
        print("query no aceptada")
        exit()
    '''
    #espero a la respuesta
    res_msg = self.conn.recv(4000).decode(STR_FORMAT)
    msg, files_data_str = res_msg.split("::")
    files_data = files_data_str.split("__")
    if len(files_data) > 0: #se lograron transferir algunos archivos
        #TODO: registar los archivos transferidos
        pass
    print("archivos transferidos: ",res_msg)
    '''
    '''
    cli_msg = f"SEND FILE::{file_name}"
    client.send(cli_msg.encode())

    #petición exitosa?
    serv_msg = client.recv(100).decode(STR_FORMAT)
    print(f"recibido mensaje: {serv_msg}")
    if serv_msg != "OK":
        raise Exception("servidor negó acceso")

    #recibo tamaño de buffer
    buffer_size = int(client.recv(100).decode(STR_FORMAT))
    print(f"tamaño de buffer: {buffer_size}")

    #recibo tamaño de archivo
    file_size = int(client.recv(100).decode(STR_FORMAT))
    print(f"tamaño de archivo: {file_size}")

    #recibo archivo
    progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=buffer_size)
    with open(file_dir, "wb") as f:

        c = 0

        while True:

            bytes_read = client.recv(buffer_size)
            
            c += len(bytes_read)
            print(c)
            
            # write to the file the bytes we just received
            f.write(bytes_read)
            
            if not bytes_read or c>=file_size:    
                # nothing is received
                # file transmitting is done
                break
            # update the progress bar
            progress.update(len(bytes_read))

        print("video recibido")
        print(os.path.getsize(file_dir))


        
        c = 0

        while c <= file_size:
            bytes_read = client.recv(buffer_size)
            c += len(bytes_read)

            #print(len(bytes_read))
            if c>=file_size or not bytes_read:
                # file transmitting is done
                break
            f.write(bytes_read)
            
    '''





else:
    raise Exception("servidor negó acceso")


'''
progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "wb") as f:
    while True:
        # read 1024 bytes from the socket (receive)
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:    
            # nothing is received
            # file transmitting is done
            break
        # write to the file the bytes we just received
        f.write(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
'''


#client.recv(BUFFER_SIZE).