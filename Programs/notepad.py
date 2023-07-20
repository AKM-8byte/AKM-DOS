from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
import ctypes
import sys





appName = 'Yazı Defteri'
nofileOpenedString = 'Yeni Dosya'

currentFilePath = nofileOpenedString

# Viable File Types, when opening and saving files.
fileTypes = [("Text Files","*.txt"), ("Markdown","*.md")]


# Tkinter Setup
window = Tk()

window.title(appName + " - " + currentFilePath)

# Window Dimensions in Pixel
window.geometry('500x400')

# Set the first column to occupy 100% of the width
window.grid_columnconfigure(0, weight=1)


# Handler Functions
def fileDropDownHandeler(action):
    global currentFilePath
    # Opening a File
    if action == "open":
        file = filedialog.askopenfilename(filetypes = fileTypes)
        window.title(appName + " - " + file)
        currentFilePath = file
        with open(file, 'r') as f:
            txt.delete(1.0,END)
            txt.insert(INSERT,f.read())


    elif action == "new":
        currentFilePath = nofileOpenedString
        txt.delete(1.0,END)
        window.title(appName + " - " + currentFilePath)


    elif action == "save" or action == "saveAs":
        if currentFilePath == nofileOpenedString or action=='saveAs':
            currentFilePath = filedialog.asksaveasfilename(filetypes = fileTypes)
        with open(currentFilePath, 'w') as f:
            f.write(txt.get('1.0','end'))
        window.title(appName + " - " + currentFilePath)



def textchange(event):
    window.title(appName + " - *" + currentFilePath)


# Text Area
txt = scrolledtext.ScrolledText(window, height=999)
txt.grid(row=1,sticky=N+S+E+W)

# Bind event in the widget to a function
txt.bind('<KeyPress>', textchange)




menu = Menu(window)
# set tearoff to 0
fileDropdown = Menu(menu, tearoff=False)
# Add Commands and and their callbacks
fileDropdown.add_command(label='Yeni', command=lambda: fileDropDownHandeler("new"))
fileDropdown.add_command(label='Aç', command=lambda: fileDropDownHandeler("open"))
# Adding a seperator between button types.
fileDropdown.add_separator()
fileDropdown.add_command(label='Kaydet', command=lambda: fileDropDownHandeler("save"))
fileDropdown.add_command(label='Farklı Kaydet', command=lambda: fileDropDownHandeler("saveAs"))
menu.add_cascade(label='Dosya', menu=fileDropdown)
# Set Menu to be Main Menu
window.config(menu=menu)




# Enabling "open with" by looking if the second argument was passed.
if len(sys.argv) == 2:
    currentFilePath = sys.argv[1]
    window.title(appName + " - " + currentFilePath)
    with open(currentFilePath, 'r') as f:
        txt.delete(1.0,END)
        txt.insert(INSERT,f.read())


window.mainloop()
