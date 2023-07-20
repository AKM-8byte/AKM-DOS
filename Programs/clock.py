
from tkinter import * 
from tkinter.ttk import *
  

from time import strftime
  

root = Tk()
root.title('Saat')
  

def time():
    string = strftime('%H:%M:%S')
    lbl.config(text = string)
    lbl.after(1000, time)
  

lbl = Label(root, font = ('calibri', 100, 'bold'),
            background = 'darkblue',
            foreground = 'white')
  

lbl.pack(anchor = 'center')
time()
  
mainloop()