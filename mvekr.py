from cProfile import label
import tkinter as tk
from tkinter import font
root = tk.Tk()

root.overrideredirect(True)
root.overrideredirect(False)
root.attributes('-fullscreen',True)
root.title("FullScreen")
root.configure(bg="darkblue")



screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()




label1 = tk.Label(root,text=":(", font=("Arial",int(screen_width/8.6)), bg="darkblue")
label1.place(x=70,y=((screen_width/32)*2.5)) 

f=open("hatakyt.txt","r")
hata=f.read()

label2 = tk.Label(root,text=("Hata Sebebi:"+hata), font=("Arial",int(screen_width/72)), bg="darkblue")
label2.place(x=45,y=(screen_width/32)*10)

label3 = tk.Label(root,text="Program bir hata ile karşılaştığından dolayı kapatılması gerekiyor.",font=("Arial",int(screen_width/70)),bg="darkblue")
label3.place(x=45,y=(screen_width/32)*12)

label4 = tk.Label(root,text="Programdan çıkmak için Alt+F4 tuşlarına aynı anda basınız",font=("Arial",int(screen_width/80)),bg="darkblue")
label4.place(x=45,y=(screen_width/32)*14)



root.mainloop()