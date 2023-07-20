from tkinter import *
from tkinter import messagebox
import os
import ctypes
import pathlib


ctypes.windll.shcore.SetProcessDpiAwareness(True)



root = Tk()
root.title('AKS Dosya Gezgini')
root.overrideredirect(True)
root.overrideredirect(False)
root.attributes('-fullscreen',True)



root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)


def pathChange(*event):
    directory = os.listdir(currentPath.get())
    list.delete(0, END)
    for file in directory:
        list.insert(0, file)

def changePathByClick(event=None):
    picked = list.get(list.curselection()[0])
    path = os.path.join(currentPath.get(), picked)
    if os.path.isfile(path):
        print('Açıldı: '+path)
        os.startfile(path)
    else:
        currentPath.set(path)

def goBack(event=None):
    newPath = pathlib.Path(currentPath.get()).parent
    currentPath.set(newPath)



def AKS():
    try:
        os.startfile("main.py")
        quit()
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "Dosya Bulunamıyor")


def Calculator():
    try:
        os.startfile("Programs\\calculator.py")
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "Dosya Bulunamıyor")

def Clock():
    try:
        os.startfile("Programs\\clock.py")
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "Dosya Bulunamıyor")

def Notepad():
    try:
        os.startfile("Programs\\notepad.py")
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "Dosya Bulunamıyor")

def Webbrowser():
    try:
        os.startfile("Programs\\webbrowser.py")
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "Dosya Bulunamıyor")

def open_popup():
    global top
    top = Toplevel(root)
    top.geometry("250x150")
    top.resizable(False, False)
    top.title("Pencere")
    top.columnconfigure(0, weight=1)
    Label(top, text='Dosya İsmi veya Klasör İsmi').grid()
    Label(top, text='Not:Klasör Oluşturmak İçin Uzantı Koymayınız').grid()
    Entry(top, textvariable=newFileName).grid(column=0, pady=10, sticky='NSEW')
    Button(top, text="Oluştur", command=newFileOrFolder).grid(pady=10, sticky='NSEW')


def newFileOrFolder():
    if len(newFileName.get().split('.')) != 1:
        open(os.path.join(currentPath.get(), newFileName.get()), 'w').close()
    else:
        os.mkdir(os.path.join(currentPath.get(), newFileName.get()))
    top.destroy()
    pathChange()

top = ''

newFileName = StringVar(root, "File.dot", 'new_name')
currentPath = StringVar(
    root,
    name='currentPath',
    value=pathlib.Path.cwd()
)
currentPath.trace('w', pathChange)


Button(root, text='Üst Klasör', command=goBack).grid(
    sticky='NSEW', column=0, row=0
)
root.bind("<Alt-Up>", goBack)
Entry(root, textvariable=currentPath).grid(
    sticky='NSEW', column=1, row=0, ipady=10, ipadx=10
)

list = Listbox(root)
list.grid(sticky='NSEW', column=1, row=1, ipady=10, ipadx=10)
list.bind('<Double-1>', changePathByClick)
list.bind('<Return>', changePathByClick)




menubar = Menu(root)
menubar.add_command(label="Dosya Veya Klaör Ekle", command=open_popup)


programs =Menu(root)
programs.add_command(label="Hesap Makinesi", command=Calculator)
programs.add_command(label="Saat",command=Clock)
programs.add_command(label="Not Defteri",command=Notepad)
programs.add_command(label="İnternet Tarayıcısı",command=Webbrowser)

menubar.add_cascade(label="Programlar", menu=programs)



menubar.add_command(label="AKS",command=AKS)
menubar.add_command(label="Kapat", command=root.quit)

root.config(menu=menubar)


pathChange('')
root.mainloop()