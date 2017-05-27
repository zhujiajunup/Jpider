from tkinter import filedialog
from tkinter import *
from traceback import *
from win32com.client import Dispatch
import time, eyed3,threading
name = []

def openfile(index = [1]):
    global total,name
    filenames = filedialog.askopenfilenames(title = "音乐播放器",filetypes =[("mp3文件","*.mp3"),("WMA文件","*.wma"),("WAV文件","*.wav")])
    if filenames:
        for i in range(len(filenames)):
            media = wmp.newMedia(filenames[i])
            wmp.currentPlaylist.appendItem(media)

            print(filenames[i])
            coco = eyed3.load(filenames[i])  #eyed3模块读取mp3信息
            total = int(coco.info.time_secs)
            minute = int(coco.info.time_secs)//60
            sec = int(coco.info.time_secs)%60
            length = int(coco.info.time_secs)

            name = filenames[i].split("/")

            i =index[-1]
            list_name.insert(END,str(i)+"."+name[-1])
            list_name.insert(END," "*6)
            if sec >=10:
                list_name.insert(END,"0%d:%d" %(minute,sec)+ "\n")
            else:
                list_name.insert(END,"0%s:0%d" %(minute,sec)+ "\n")
            i = i +1
            index.append(i)
def play(event = None):
    #root.title("%s" % name[-1]),使用wmp.currentMedia.name更好,在per函数中
    per_thread = threading.Thread(target = per)
    per_thread.daemnon = True
    wmp.controls.play()
    per_thread.start()
    #print(wmp.currentMedia.duration)#放到暂停那里居然可以用,而这里不行

def per():
    global total
    while wmp.playState !=1:
        progress_scal.set(int(wmp.controls.currentPosition))
        progress_scal.config(label = wmp.controls.currentPositionString)
        progress_scal.config(to = total,tickinterval = 50)
        time.sleep(1)
        root.title("%s" % wmp.currentMedia.name)

def stop():
    wmp.controls.stop()
def pause(event = None):
    wmp.controls.pause()
def uselist():
    pass
def fullscr():
    pass
def exitit():
    root.destroy()
def Previous_it():
    wmp.controls.previous()
def Next_it():
    wmp.controls.next()
def Volume_ctr(none):
    wmp.settings.Volume = vio_scale.get()
def Volume_add(i=[0]):
    wmp.settings.Volume =wmp.settings.Volume+5
    i.append(wmp.settings.Volume)
    vio_scale.set(wmp.settings.Volume)
def Volume_minus(i=[0]):
    wmp.settings.Volume = wmp.settings.Volume -5
    i.append(wmp.settings.Volume)
    vio_scale.set(wmp.settings.Volume)
def Scale_ctr(none):
    wmp.controls.currentPosition = var_scale.get()
    print(wmp.currentMedia.duration)
def Clear_list():
    wmp.currentPlaylist.clear()
    list_name.delete(1.0,END)
    name = []
    index = []
def List_random():
    wmp.settings.setMode("shuffle",True)
    play()
def List_loop():
    wmp.settings.setMode("loop",True)
    play()
root =Tk()
wmp = Dispatch("WMPlayer.OCX")
canvas = Canvas(root,width =150,height = 100,bg = "blue")
# filename = PhotoImage(file = "girl.gif")
# image =canvas.create_image((0,0),image = filename)
canvas.place(x=0,y=0)
#canvas.coords(image,79,50)
canvas.grid(row =0,column = 0,sticky = "nw",rowspan =2)
progress_lab = LabelFrame(root,text = "播放进度")
progress_lab.grid(row =2,column =0,sticky = "we",rowspan = 2)
var_scale = DoubleVar()
progress_scal = Scale(progress_lab,orient = HORIZONTAL,showvalue = 0,length =180,variable = var_scale)
#progress_scal.bind("<Button-1>",pause)
#progress_scal.bind("")
#progress_scal.bind("<ButtonRelease-1>",play)
progress_scal.grid(row =3,column =0)
modee_lab = LabelFrame(root,text = "播放模式")
modee_lab.grid(row =4,column =0,rowspan =4,sticky = "ws")
var_mode = IntVar()
randomradio = Radiobutton(modee_lab,variable = var_mode,value = 1,text ="随机播放",command =List_random )
randomradio.grid(row =4,column =2)
inturnradio = Radiobutton(modee_lab,variable = var_mode,value =2,text= "顺序播放",command = play)
inturnradio.grid(row=4,column =3)
alloop = Radiobutton(modee_lab,variable = var_mode,value =2,text = "全部循环播放",command = List_loop)
alloop.grid(row =5,column = 2)
sinloop = Radiobutton(modee_lab,variable = var_mode,value =3,text = "单曲循环播放")
sinloop.grid(row =5,column =3)
previous_play = Button(modee_lab,text = "上一曲",height =1,command = Previous_it)
previous_play.grid(row =6,column =2,rowspan =2,pady =5)
next_play = Button(modee_lab,text = "下一曲",height =1,command = Next_it)
next_play.grid(row =6,column =3,rowspan =2,pady =5)
var_volume = IntVar()
vioce_lab = LabelFrame(root,text = "音量控制")
vioce_lab.grid(row =8,column =0,sticky = "wes")
vio_scale = Scale(vioce_lab,orient = HORIZONTAL,length =170,variable = var_volume,command =Volume_ctr)
vio_scale.set(30)
vio_scale.grid(row =8,column =0)
vio_plus = Button(vioce_lab,width =8,text = "增加音量+",command =Volume_add)
vio_plus.grid(row =9,column =0,sticky = "w")
vio_minus = Button(vioce_lab,width =8,text ="减少音量-",command = Volume_minus)
vio_minus.grid(row =9,column =0,sticky ="e")
ctr_lab = LabelFrame(root,text = "播放控制",height =130)
ctr_lab.grid(row =0,column =1,rowspan =12,sticky = "ns")
btn_open = Button(ctr_lab,text ="打开音乐文件",width =10,command = openfile)
btn_open.grid(row=0,column =1)
btn_play = Button(ctr_lab,text ="播放",width =10,command = play)
btn_play.grid(row =1,column =1,pady =5)
btn_stop = Button(ctr_lab,text ="停止",width =10,command = stop)
btn_stop.grid(row =2,column =1,pady =5)
btn_pause = Button(ctr_lab,text ="暂停",width =10,command = pause)
btn_pause.grid(row =3,column =1,pady =5)
btn_playlist = Button(ctr_lab,text ="新建播放列表",width =10,command = uselist)
btn_playlist.grid(row =4,column =1,pady =5)
listimport = Button(ctr_lab,width =10,text = "导入列表")
listimport.grid(row =6,column =1,sticky ="nw",pady =5)
listexport = Button(ctr_lab,width =10,text = "导出列表")
listexport.grid(row =7,column =1,sticky = "nw",pady =5)
listdel_all = Button(ctr_lab,width =10,text = "清空列表",command = Clear_list)
listdel_all.grid(row =8,column =1,sticky ="nw",pady =5)
listdel_sel= Button(ctr_lab,width =10,text = "删除歌曲")
listdel_sel.grid(row =12,column =1,sticky = "nw",pady =5)
savelist_btn = Button(ctr_lab,text = "保存为列表")
savelist_btn.grid(row=9,column =1)
min_btn = Button(ctr_lab,text = "最小化窗口",command = root.iconify)
min_btn.grid(row =13,column =1)
time_lab= Label(root,width =20,height =2,text ="现在时间为:")
time_lab.grid(row =12,column =0,sticky = "nw",pady =5)
time_text= Text(root,width =30,height =3,foreground ="green")
time_text.grid(row =10,column =0,sticky = "nw",pady =5)
list_name = Text(root,height =18,width =110)
list_name.grid(row =0,column =2,sticky = "n",rowspan =6)
root.mainloop()