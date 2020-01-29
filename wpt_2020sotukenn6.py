import time
import statistics
import math
import serial
import collections
import csv
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.font as tkFont
import tkinter.ttk as ttk

x=0
L=[] #dataを保存
L1=[]
L2=[]
Lmsave=[]
Lmsend=[]
Lmreceive=[]
fre=0 #測定範囲の最小値
laf=0 #1目盛りの周波数
data=0 #測定範囲の最大値
ser1=0 #送電側のシリアル通信
ser2=0 #受電側のシリアル通信
t=1
tm=0



def maindef():
    global x
    global L
    global ser
    global fre
    global data
    global laf
    global ser1 
    global ser2
    global t
    global tm
    global L1
    global L2
    global Lmsave
    global Lmsend
    global Lmreceive
   
    if x==0:
        t=1#一応
    elif x==1:
        #次の周波数を入力
        if float(fre) > float(laf):
            x=3
        else:
            
            ser1.write('a'.encode('ascii')) # arduinoへ開始の合図を送る。
            ser2.write('a'.encode('ascii'))
            ser1.write(fre.encode('ascii'))
            ser2.write(fre.encode('ascii'))
            ser1.flush() # バッファ内の待ちデータを送りきる。
            ser2.flush()
            print("send:"+fre+"kHz")
            L.append(fre+"kHz")
            x=2
        t=1
    elif x==2:
        #データ受け取りスイープ
        line1 = ser1.readline().decode('ascii').rstrip()
        line2 = ser2.readline().decode('ascii').rstrip()
        L1.append(line1)
        L2.append(line2)
        print(fre+" "+line1+" "+line2+" ")
        L.append(fre+" "+line1+" "+line2+" ")
        if t>=int(tm):
            math1=collections.Counter(L1).most_common()[0][0]
            math2=collections.Counter(L2).most_common()[0][0]
            Lmsave.append(fre+" "+math1+" "+math2)
            Lmsend.append(fre+" "+math1)
            Lmreceive.append(fre+" "+math2)
            if float(fre)+float(data)*0.001 > float(laf) and float(laf) > float(fre):
                fre=laf
            else:
                fre=str(round(float(fre) + float(data)*0.001,3))
            x=1
            L1=[]
            L2=[]
        else:
            t=t+1
            
    elif x==3:
        #データを送らない、後始末
        stop_data()
        x=0
    elif x==4:
        #データ受け取り通常
        line1 = ser1.readline().decode('ascii').rstrip()
        line2 = ser2.readline().decode('ascii').rstrip()
        print(fre+" "+line1+" "+line2+" ")
        L.append(fre+" "+line1+" "+line2+" ")
    
    root.after(10,maindef)

class Ser:
    def __init__(self):
        self.ser=None
        
    def start_connect(self):
        global ser1
        global ser2
        comport1='COM4' # arduino ideで調べてから。送電側
        comport2='COM3' #受電側必ずcomportは送電側受電側異なるものを使用
        tushinsokudo=57600 # arduinoのプログラムと一致させる。
        timeout=5# エラーになったときのために。とりあえず5秒で戻ってくる。
        ser1=self.ser
        ser2=self.ser
        ser1 = serial.Serial(comport1,tushinsokudo,timeout=timeout)
        ser2 = serial.Serial(comport2,tushinsokudo,timeout=timeout)
        time.sleep(2) # 1にするとダメ！短いほうがよい。各自試す。
        
    def send_com(self):
        global x
        global data
        global fre
        global laf
        global ser1
        global ser2
        global L
        global tm
        global L1
        global L2
        global Lmsave
        global Lmsend
        global Lmreceive
        # v,u,sの文字列は、
        #ぞれぞれv.get(),u.get(),s.get()で取り出す。
        #下部send_entry内のTextvariableでデータ入力
        data=v.get()
        fre=u.get() 
        laf=s.get()
        tm=v1.get() 
        if data.isdecimal()==True and fre.isdecimal()==True and laf.isdecimal()==True and tm.isdecimal()==True:
                ser1.write('a'.encode('ascii')) # arduinoへ開始の合図を送る。
                ser2.write('a'.encode('ascii'))
                ser1.write(fre.encode('ascii'))
                ser2.write(fre.encode('ascii'))#送電側と受電側の送るデータの量を合わせるため，
                #あえて周波数を送る.送らなかった場合，送電側と受電側の出力にずれが生じるから．
                ser1.flush() # バッファ内の待ちデータを送りきる。
                ser2.flush()
                print("send incease_fre:"+data+" first_fre:"+fre+" last_fre:"+laf)
                print("frequency transmission_ep receiving_ep")
                L.append("increase_frequency:"+data+" first_frequency:"+fre+" last_frequency:"+laf)
                L.append("frequency transmission_ep receiving_ep")
                print("send:"+fre+"kHz")
                L.append(fre+"kHz")
                L1=[]
                L2=[]
                Lmsave=[]
                Lmsend=[]
                Lmreceive=[]
                
                
                if int(data)==0:
                    x=4
                else:
                    x=2
                t=1
        else:
                print("error")
                v.set("")
                u.set("")
                s.set("")
                v1.set("")
    def stop_com(self):
        global x
        x=3
        

    def connect(self):
        self.start_connect()
        send_button.configure(state=tk.NORMAL)
        stop_button.configure(state=tk.NORMAL)
        send_entry.configure(state=tk.NORMAL)
        defalt_entry.configure(state=tk.NORMAL)
        saveas_button.configure(state=tk.NORMAL)
        max_entry.configure(state=tk.NORMAL)
        time_entry.configure(state=tk.NORMAL)
        connect_button.configure(state=tk.DISABLED)
        saveas_combo.configure(state=tk.NORMAL)

def saveas():
    global L
    global data
    global Lmreceive
    global Lmsave
    global Lmsend
    secomb=vc.get()
    if secomb=='all':
        save(L)
    else:
        if data=='0':
            print("error!!")
        else:
            if secomb=='sweep:fre-send-receive':
                save(Lmsave)
            elif secomb=='sweep:fre-send':
                save(Lmsend)
            elif secomb=='sweep:fre-receive':
                save(Lmreceive)

def save(a):
    filename=tkFileDialog.asksaveasfilename(defaultextension=".csv",filetypes=[("csv","*.csv*")])
    with open(filename,'w') as fout:
        fout.write("\n".join(a))
        
    
#周波数をclock_genelaterに送る
#ストップするときの関数
def stop_data():
    global ser1
    global ser2
    global fre
    ser1.write('b'.encode('ascii')) # arduinoへ終了の合図を送る。
    ser2.write('b'.encode('ascii'))
    ser1.flush() # バッファ内の待ちデータを送りきる。
    ser2.flush()
    ser1
    print("--stop--")
    L.append("stop")
    fre='0'
    time.sleep(1)
    
root=tk.Tk()
font=tkFont.Font(size=24)
ser=Ser() 
v=tk.StringVar() # tk.TK()の後に書く。
u=tk.StringVar()
s=tk.StringVar()
v1=tk.StringVar()
vc=tk.StringVar()

#ボタン入力
connect_button=tk.Button(root,text='connect',font=font,height=2,padx=20,command=ser.connect)
connect_button.grid(row=0,column=0)
send_button=tk.Button(root,text='send',font=font,height=2,padx=20,command=ser.send_com)
send_button.grid(row=0,column=1)
send_button.configure(state=tk.DISABLED)
stop_button=tk.Button(root,text='stop',font=font,height=2,padx=20,command=ser.stop_com)
stop_button.grid(row=0,column=2)
stop_button.configure(state=tk.DISABLED)
#entry
send_entry=tk.Entry(root,font=font,textvariable=v)
send_entry.grid(row=1,column=1,columnspan=2)
send_entry.configure(state=tk.DISABLED)
defalt_entry=tk.Entry(root,font=font,textvariable=u)
defalt_entry.grid(row=2,column=1,columnspan=2)
defalt_entry.configure(state=tk.DISABLED)
max_entry=tk.Entry(root,font=font,textvariable=s)
max_entry.grid(row=3,column=1,columnspan=2)
max_entry.configure(state=tk.DISABLED)
time_entry=tk.Entry(root,font=font,textvariable=v1)
time_entry.grid(row=4,column=1,columnspan=2)
time_entry.configure(state=tk.DISABLED)

#label
label1=tk.Label(root,font=font,text='increase_frequency')
label1.grid(row=1,column=0)
label1_Hz=tk.Label(root,font=font,text='Hz')
label1_Hz.grid(row=1,column=3)
label2=tk.Label(root,font=font,text='first_frequency')
label2.grid(row=2,column=0)
label2_Hz=tk.Label(root,font=font,text='kHz')
label2_Hz.grid(row=2,column=3)
label3=tk.Label(root,font=font,text='last_frequency')
label3.grid(row=3,column=0)
label3_Hz=tk.Label(root,font=font,text='kHz')
label3_Hz.grid(row=3,column=3)
label4_time=tk.Label(root,font=font,text='Measurement_Time')
label4_second=tk.Label(root,font=font,text='ds')
label4_time.grid(row=4,column=0)
label4_second.grid(row=4,column=3)

#セーブボタン
saveas_button=tk.Button(root,text='save',font=font,height=2,padx=20,command=saveas)
saveas_button.grid(row=0,column=3)
saveas_button.configure(state=tk.DISABLED)

#COMBOBOX
Comb=['all','sweep:fre-send-receive','sweep:fre-send','sweep:fre-receive']
saveas_combo=ttk.Combobox(root,values=Comb,textvariable=vc)
vc.set(Comb[0])
saveas_combo.grid(row=0,column=4)
saveas_combo.configure(state=tk.DISABLED)

root.after(100,maindef)
root.mainloop()   
