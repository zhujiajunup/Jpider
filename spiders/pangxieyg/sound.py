# from win32com.client import Dispatch
#
#
# while True:
#     wmp = Dispatch("WMPlayer.OCX")
#     media = wmp.newMedia("D:/CloudMusic/双笙 - 小幸运.mp3")
#     wmp.currentPlaylist.appendItem(media)
#     wmp.controls.play()
import pyaudio
import wave


chunk = 1024
wf = wave.open(r'C:\Windows\Media\notify.wav', 'rb')
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# 写声音输出流进行播放
while True:
    data = wf.readframes(chunk)
    if data == b'':
        break
    stream.write(data)
stream.close()
p.terminate()
