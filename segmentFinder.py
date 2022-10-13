import socket
import os
import sys
from datetime import datetime, timedelta
from threading import local

from fileRequester import FileRequester

MEDIA_FOLDER = "media"
DATE_FORMAT = "%Y-%m-%d %H-%M-%S"


#TODO: TENER EN CUENTA ARCHIVOS CORRUPTOS SIN EOF. HAY QUE CHEQUEAR SI CUMPLEN CON EL TIEMPO SUFICIENTE PARA EL SEGMENTO Y BUSCAR EOF
#TODO: EN RADIO, A VECES LOS VIDEOS DURAN UN POCO MAS DE UNA HORA
#TODO: 

class SegmentFinder():

    def __init__(self):
        return
        #self.server_id = server_id
        #self.ip = socket.gethostbyname(socket.gethostname())
        #print("servidor en ip: ",self.ip)

    #retorno un diccionario con la información de un segmento solicitado
    def search_segment_file(self, channel_name, extention, segment_start, segment_end):

        hour_start = segment_start.replace(minute=0, second=0)
        file_name = f"{channel_name} {hour_start.strftime(DATE_FORMAT)}" + "." + extention
        #hour_end = hour_start + timedelta(hours=1)

        file_dir = os.path.join(os.path.join(MEDIA_FOLDER, channel_name), file_name)

        #reviso si está en el servidor
        if os.path.exists(file_dir):
            location = "local"
        else:
            location = "remote"


        time_start = segment_start - hour_start #11:40 - 
        time_end = segment_end - hour_start

        #print(time_start, time_end)

        return {
            "file_name": file_name,
            "time_start": str(time_start),
            "time_end": str(time_end),
            "location": location
        }

    def get_segment_list(self, timestamp_start, timestamp_end):

        start = datetime.strptime(timestamp_start, DATE_FORMAT)
        end = datetime.strptime(timestamp_end, DATE_FORMAT)

        if end <= start:
            raise Exception("invalid time ranges. Start must happen before end.")

        segments = []

        delta = timedelta(hours=1)

        current = start
        
        while current < end :

            next = current.replace(minute=0, second=0) + delta #la hora siguiente al acutal
            #print(next)
            if next > end:
                dest = end
            else:
                dest = next
            segments.append((current, dest))
            current = dest

        return segments

    #TODO: IMPLEMENTAR ESTO!!!!!
    def validateFile(self, file_dir):
        pass


    def get_media(self, channel_name, extention, timestamp_start, timestamp_end):
        
        segment_ranges = self.get_segment_list(timestamp_start, timestamp_end)
        segments_dict_list = []
        print("buscando segmentos:")
        print(segment_ranges)
        for segment_start, segment_end in segment_ranges:
            #busco datos de cada segmento (nombre archivo, desde que minuto parte, hasta que minuto duro y si está local o en el otro servidor)
            segments_dict_list.append(self.search_segment_file(channel_name, extention, segment_start, segment_end))

        #reviso si hay algún remoto
        #TODO: VALIDAR ACÁ LA DURACIÓN, VALIDEZ y EOF!. Si es que es inválido marcar también
        remotes = []
        for sr in segments_dict_list:
            if sr['location'] == 'remote':
                remotes.append(sr)

        if len(remotes) > 0:#debo pedir al otro servidor
            fileRequester = FileRequester()
            print("conectando con otro servidor")
            if fileRequester.setConnection() != None:
                print("solicitando chunks faltantes")
                transferedRemotes = fileRequester.askForRemotes(remotes, channel_name)
                for tr in transferedRemotes:
                    for i in range(len(segments_dict_list)):
                        if segments_dict_list[i]['file_name'] == tr:
                            segments_dict_list[i]['location'] = 'local'
                            break
                

                print("segmentos finales: ", segments_dict_list)
            
            else:
                raise Exception("no se pudo conectar con servidor")


        return segments_dict_list


if __name__ == "__main__":

    concatter = SegmentFinder()

    name = "Adn.air.cl"
    timestamp_start = "2022-09-01 23-40-00"
    timestamp_end = "2022-09-02 03-40-00"
    extention = "mp3"

    M = concatter.get_media(name, extention,timestamp_start,timestamp_end)
