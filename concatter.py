import ffmpeg
import os

from dotenv import load_dotenv

load_dotenv()


#segments = [{'file_name': 'Adn.air.cl 2022-09-01 23-00-00.mp3', 'time_start': '0:40:00', 'time_end': '1:00:00', 'location': 'local'}, {'file_name': 'Adn.air.cl 2022-09-02 00-00-00.mp3', 'time_start': '0:00:00', 'time_end': '1:00:00', 'location': 'local'}, {'file_name': 'Adn.air.cl 2022-09-02 01-00-00.mp3', 'time_start': '0:00:00', 'time_end': '1:00:00', 'location': 'local'}, {'file_name': 'Adn.air.cl 2022-09-02 02-00-00.mp3', 'time_start': '0:00:00', 'time_end': '1:00:00', 'location': 'local'}, {'file_name': 'Adn.air.cl 2022-09-02 03-00-00.mp3', 'time_start': '0:00:00', 'time_end': '0:40:00', 'location': 'local'}]
segments = [{'file_name': 'Adn.air.cl 2022-09-02 02-00-00.mp3', 'time_start': '0:00:00', 'time_end': '1:00:00', 'location': 'local'}, {'file_name': 'Adn.air.cl 2022-09-02 03-00-00.mp3', 'time_start': '0:00:00', 'time_end': '0:40:00', 'location': 'local'}]

class Concatter:


    def __init__(self, input_file_name="input.txt", tmp_folder_name = "tmp", media_dir = os.getenv("MEDIA_DIR")):
        self.input_file_name = input_file_name
        self.tmp_folder_name = tmp_folder_name
        self.media_dir = media_dir

    def deleteInputFileIfExists(self):
        if os.path.exists(os.path.join(self.tmp_folder_name, self.input_file_name)):
            os.remove(os.path.join(self.tmp_folder_name, self.input_file_name))

    def createInputFile(self, channel_name, segments):
        with open(os.path.join(self.tmp_folder_name, self.input_file_name), "w") as f:
            for segment in segments:
                if segment['location'] == 'local':
                    f.write(f"file '{os.path.join(os.path.join(self.media_dir, channel_name), segment['file_name'])}'\n")
                    f.write(f"inpoint {segment['time_start']}\n")
                    f.write(f"outpoint {segment['time_end']}\n")

    def concat(self, input_dir, output_dir):
        ffmpeg.input(input_dir, f='concat', safe=0).output(output_dir, codec='copy').overwrite_output().run()


    def concatSegments(self, channel_name, segments, file_name):
        try:
            self.deleteInputFileIfExists()
            self.createInputFile(channel_name, segments)
            input_dir = os.path.join(self.tmp_folder_name, self.input_file_name)
            output_dir = os.path.os.path.join(self.tmp_folder_name, file_name)
            self.concat(input_dir, output_dir)
            self.deleteInputFileIfExists()
            return output_dir
        except Exception as E:
            return None


if __name__ == "__main__":

    concatter = Concatter()

    input_dir = "tmp/input.txt"

    output_dir = "tmp/result.mp3"

    concatter.concatSegments(segments, "test.mp3")

    #ffmpeg.input(input_dir, f='concat', safe=0).output(output_dir, codec='copy').overwrite_output().run()

    '''
    stream = ffmpeg.input(input_dir)
    stream = ffmpeg.filter(stream, "concat", safe=0)
    stream = ffmpeg.output(stream, output_dir)


    try:
      ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
    except ffmpeg.Error as e:
      print('stdout:', e.stdout.decode('utf8'))
      print('stderr:', e.stderr.decode('utf8'))
      raise e
    '''