# voice process modules
# detect voice
from speech_recognition import Recognizer, Microphone, WavFile
from pyaudio import PyAudio, paInt16
import wave
# generate voice
from pygame import mixer
from tempfile import NamedTemporaryFile
from gtts import gTTS

# time
from datetime import datetime
from time import sleep

# setting
from setting import menu_xlsx_path

# order process modules
# process order
from process_order import load_xlsx, process_data_to_menu, process_price_with_order

class Order_Bot:
    def __init__(self, mode = 'voice1'):
        # speaker init
        mixer.init()
        # mode: voice1, voice2, text
        self.mode = mode
        # recognizer init    
        self.recognizer = Recognizer()
        # user name
        self.master = None

    def line_speaker(self, texts,lang='zh-tw'):
        with NamedTemporaryFile(delete=True) as fp:
            tts = gTTS(text=texts,lang=lang)
            tts.save("{}.mp3".format(fp.name))
            mixer.music.load('{}.mp3'.format(fp.name))
            mixer.music.play()
        print(texts)

    def listener(self):
        if self.mode == 'text':
            result = input()
            return result
        elif self.mode == 'voice1':
            result = None
            while(result == None):
                with Microphone() as source:
                    # recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)
                try:
                    result = self.recognizer.recognize_google(audio,language = 'zh-tw')
                except:
                    continue
            print(result)
            return result
        elif self.mode == 'voice2':
            result = None
            while(result == None):
                # sample chunk size
                chunk = 1024
                # sample format: paFloat32, paInt32, paInt24, paInt16, paInt8, paUInt8, paCustomFormat
                sample_format = paInt16
                # sound channel
                channels = 2
                # sample frequency rate: 44100 ( CD ), 48000 ( DVD ), 22050, 24000, 12000 and 11025
                fs = 44100
                # recording seconds
                seconds = 5
                # init pyaudio object
                p = PyAudio()

                print("starting recording...")

                # active voice stream
                stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
                frames = []
                # voice list
                for _ in range(0, int(fs / chunk * seconds)):
                    # record voice into list
                    data = stream.read(chunk)
                    frames.append(data)
                # stop recording
                stream.stop_stream()
                # close stream
                stream.close()
                p.terminate()
                print('stop recording...')
                
                with NamedTemporaryFile(delete=True) as fp:
                    # open voice file
                    wf = wave.open("{}.wav".format(fp.name), 'wb')
                    # set channel
                    wf.setnchannels(channels)
                    # set format
                    wf.setsampwidth(p.get_sample_size(sample_format))
                    # set sampling frequency rate
                    wf.setframerate(fs)
                    # save
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    with WavFile('{}.wav'.format(fp.name)) as source:
                        audio = self.recognizer.listen(source)
                        try:
                            result = self.recognizer.recognize_google(audio,language = 'zh-tw')
                        except:
                            continue
            print(result)
            return result

    def order_manage(self):
        data_dict = load_xlsx(file_name=menu_xlsx_path)
        menu_dict = process_data_to_menu(data_dict)
        self.line_speaker('?????????????????????????????????????????????????????????')
        while(1):
            order_line = self.listener()
            
            # ??????
            if '??????' in order_line:
                self.line_speaker('?????????')
                if self.master!=None:
                    self.line_speaker('??????'+self.master)
            
            # ???????????????
            elif '???????????????' in order_line or '??????' in order_line:
                self.master=order_line.split('???')[-1]
                self.line_speaker('???????????????Master??????'+self.master)

            # ??????????????????
            elif '??????' in order_line:
                eat_count = 0
                self.line_speaker('?????????????????????')
                while(eat_count<2):
                    order_line = self.listener()
                    if '???' in order_line:
                        self.line_speaker('???????????????')
                        eat_count+=1
                    elif '???' in order_line:
                        self.line_speaker('???????????????')
                        eat_count+=1
                    else:
                        self.line_speaker('??????????????????')
                self.line_speaker('???????????????')
                continue

            # ?????????
            elif '??????' in order_line:
                self.line_speaker('?????????????????????????????????????????????????????????????????????')
                while(not '???' in order_line):
                    order_line = self.listener()
                self.line_speaker('??????????????????????????????????????????????????????')
                order_line = self.listener()
                while(not '???' in order_line):
                    order_line = self.listener()
                if '??????' in order_line:
                    self.line_speaker('????????????')
                else:
                    self.line_speaker('????????????')

            # ??????
            elif '???' in order_line:
                total_order = ''
                self.line_speaker('???????????????????????????')
                while(1):
                    order_menu_line = self.listener()
                    if '???' in order_menu_line or '???' in order_menu_line:
                        total_order+=order_menu_line+'???'
                    elif '???' in order_menu_line or '??????' in order_menu_line:
                        # ?????????
                        break
                    else:
                        self.line_speaker('?????????????????????????????????')
                self.line_speaker(process_price_with_order(menu_dict, total_order))

            # ?????????????????????
            elif ('??????' in order_line) or ('??????' in order_line):
                now = datetime.now()
                res_text = '??????????????? %d ??? %d ??? %d ???' % (now.hour, now.minute, now.second)
                self.line_speaker(res_text)

            # ??????
            elif '??????' in order_line or '??????' in order_line:
                self.line_speaker('???????????????????????????????????????????????????')
                sleep(6)
                break
            
            # not any option upper
            else:
                self.line_speaker('?????????????????????????????????')
            
    def __call__(self):
        self.order_manage()

if __name__ == '__main__':
    order_bot = Order_Bot('text')
    order_bot.mode = 'voice2'
    order_bot()