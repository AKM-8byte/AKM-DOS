import os
from random import *
import string

try:
    import pyautogui
    pyautogui.press("f11")
except ModuleNotFoundError:
    print("Uyarı pyautogui bilgiseyarda bulunmadığından dolayı tam ekran modunu elle aktif edebilirsiniz")


try:
    kullanıcı_adı = open("Kullanıcı\\kullanıcı_ad.txt","r",encoding="utf-8")
except FileNotFoundError:
    print("Buralarda Yeni Gibi Gözüküyorsun Sana Ne İle Hitap Etmeliyim")
    ad = input()
    kullanıcı_adı = open("Kullanıcı\\kullanıcı_ad.txt","w",encoding="utf-8")
    kullanıcı_adı.write(ad)
    os.system("cls")



print("AKM Komut Sistemi 0.5 Alpha Versiyonuna Hoş geldiniz "+str(*kullanıcı_adı))

def fonkisyon():
    try:
        cvp = input(">>>")
        if cvp =="sürüm":
            print("AKS Versiyon 0.5 Alpha")
            fonkisyon()
        elif cvp =="yardım":
            print("sürüm")
            print("aygıtlar")
            print("hesap")
            print("cmd")
            print("calistir")
            print("yazıdft")
            print("web")
            print("aka")
            print("kapat")
            print("renk")
            print("temizle")
            fonkisyon()
        elif cvp == "hesap":
            print("İşleminizi Yazın")
            print("1-Toplama")
            print("2-Çıkarma")
            print("3-Bölme")
            print("4-Çarpma")
            print("5-Çıkış")
            i = input()
            if i == "1":
                deger1=int(input())
                deger2=int(input())
                print(deger1+deger2)
                fonkisyon()
            elif i == "2":
                deger1=int(input())
                deger2=int(input())
                print(deger1-deger2)
                fonkisyon()
            elif i == "3":
                deger1=int(input())
                deger2=int(input())
                print(deger1/deger2)
                fonkisyon()
            elif i == "4":
                deger1=int(input())
                deger2=int(input())
                print(deger1*deger2)
                fonkisyon()
            elif i == "5":
                fonkisyon()
            else:
                print("Yanlış Yazdınız")
                fonkisyon()
        elif cvp == "aygıtlar":
            os.system("devmgmt.msc")
            fonkisyon()
        elif cvp == "cmd":
            cmd=input()
            os.system(cmd)
            fonkisyon()
        elif cvp == "calistir":
            calisacak = input()
            os.startfile(calisacak)
            fonkisyon()
        elif cvp == "notepad":
            os.startfile("Programs\\notepad.py")
            fonkisyon()
        elif cvp == "web":
            os.startfile("Programs\\webbrowser.py")
            fonkisyon()
        elif cvp == "aka":
            os.startfile("aka.py")
        elif cvp == ("çıkış" and "kapat"):
            quit()
        elif cvp == "renk":
            renk = input("Sayı Giriniz:")
            os.system("color "+renk)
            fonkisyon()
        elif cvp == "temizle":
            os.system("cls")
        else:
            print("Böyle bir komut yok(Yardım için yardım komudunu yazın)")
            fonkisyon()


    except ValueError:
        f=open("hatakyt.txt","w")
        f.write("Value Error")
        os.startfile("mvekr.py")
        quit()
    except FileNotFoundError:
        f=open("hatakyt.txt","w")
        f.write("File Not Found Error")
        os.startfile("mvekr.py")
        quit()







fonkisyon()
