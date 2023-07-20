import os
from turtle import *
import turtle
import os
import time

try:
    import playsound
except ModuleNotFoundError:
    print("Playsound Modülü Yok")


#change the pen speed
speed(1)
#change the screen color
bgcolor("black")
penup()
#change the pen position

playsound.playsound("win95.mp3")

goto(-50,60)
pendown()
color('#00adef')
begin_fill()
#change the position
goto(100,100)
goto(100,-100)
goto(-50,-60)
 
goto(-50,60)
end_fill()
 
color("black")
goto(15,100)
color("black")
width(10)
goto(15,-100)
penup()
 
goto(100,0)
pendown()
 
goto(-100,0)

goto(-80,-250)
penup()
color("white")
turtle.write("AKA", font=("Verdana",70))
goto(-90,-300)
turtle.write("AKM Corporation", font=("Verdana",20))
pendown()


time.sleep(3)


os.startfile("main.py")
quit()