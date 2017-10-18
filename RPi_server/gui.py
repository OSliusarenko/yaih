#!/usr/bin/python
# -*- coding: utf-8 -*-

import ttk
import Tkinter as tk
import tkMessageBox
import threading
import signal
import os

import random # temporarily, remove after
import string

from functools import partial
from time import sleep
from collections import deque

def randomString(length):
    return ''.join(random.choice(string.lowercase+string.digits+
                   string.uppercase) for i in range(length))

BTN_GO_UP = u'\u23f6'
BTN_GO_DN = u'\u23f7'
BTN_PAUSE = u'\u23f8'
BTN_STOP = u'\u23f9'
BTN_PREV = u'\u23ee'
BTN_NEXT = u'\u23ed'
BTN_PPAUSE = u'\u23ef'
BTN_EJECT = u'\u23cf'
BTN_BACK = u'\u2b8c'
BTN_CLOSE = u'\u2bbd'
BTN_VDN = u'\u2796'
BTN_VUP = u'\u2795'
BTN_CHOOSE = u'\ue531'
BTN_A = u'\ue525'
BTN_Z = u'\ue526'


class Gui(threading.Thread):

    quitting = False
    UIinitialized = False
    commandsQueue = deque()  # storage for all commands


    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def initUI(self):

        self.root.title("player")
        self.style = ttk.Style()
        self.style.theme_use("default")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(4, pad=30)
        self.root.rowconfigure(5, weight=1)

        self.lb = tk.Listbox(self.root)
        self.lb.grid(row=0, column=0, columnspan=1, rowspan=6,
            padx=3, pady=3, sticky=tk.E+tk.W+tk.S+tk.N)

        self.lb.bind("<<ListboxSelect>>", self.onSelect)

        self.ubtn = tk.Button(self.root, text=BTN_GO_UP,
                    command=partial(self.appendToCommandsQueue, 'u'))
        self.ubtn.grid(row=1, column=2, columnspan=1)

        self.dbtn = tk.Button(self.root, text=BTN_GO_DN,
                    command=partial(self.appendToCommandsQueue, 'd'))
        self.dbtn.grid(row=3, column=2, columnspan=1)

        self.lbtn = tk.Button(self.root, text=u"\u25c0",
                    command=partial(self.appendToCommandsQueue, 'l'))
        self.lbtn.grid(row=2, column=1, padx=5)

        self.rbtn = tk.Button(self.root, text=u"\u25b6",
                    command=partial(self.appendToCommandsQueue, 'r'))
        self.rbtn.grid(row=2, column=3, padx=5)

        self.sbtn = tk.Button(self.root, text=BTN_STOP,
                    command=partial(self.appendToCommandsQueue, 's'))
        self.sbtn.grid(row=4, column=1)

        self.pbtn = tk.Button(self.root, height=1, width=6,
                               text=BTN_PPAUSE,
                    command=partial(self.appendToCommandsQueue, 'p'))
        self.pbtn.grid(row=4, column=2, columnspan=2)

        self.var = tk.StringVar()
        self.label = tk.Label(self.root, text=0, textvariable=self.var)
        self.label.grid(row=6, column=0, columnspan=2, rowspan=1,
            padx=1, pady=1, sticky=(tk.S+tk.W))

        self.fbtn = tk.Button(self.root, text=BTN_EJECT, height=1, width=2,
                    command=partial(self.appendToCommandsQueue, 'c'))
        self.fbtn.grid(row=6, column=2)
        self.cbtn = tk.Button(self.root, text=BTN_CLOSE, height=1, width=2,
                         command=self.onExit)
        self.cbtn.grid(row=6, column=3)





    def feedToListbox(self, lines):
        """ Displays specified list of strings on form's listbox """
        for line in lines:
            self.lb.insert(tk.END, line)


    def clearListBox(self):
        """ Just clears form's listbox """
        self.lb.delete(0, tk.END)


    def selectListBoxLine(self, linenum):
        self.lb.selection_clear(0, tk.END)
        self.lb.selection_set(linenum)
        self.lb.see(linenum)


    def getListBoxSelectedLine(self):
        idx = self.lb.curselection()
        try:
            value = self.lb.get(idx)
            return idx, value
        except:
            idx = (0,)
            value = self.lb.get(idx)
            print value
            return idx, value


    def setStatus(self, value):
        print(value)
        self.var.set(value)


    def onSelect(self, val):
        self.appendToCommandsQueue('set_selection')


    def setMode(self, mode):
        if mode=='select_artists':
            self.ubtn.config(state=tk.NORMAL, text=BTN_GO_UP)
            self.dbtn.config(state=tk.NORMAL, text=BTN_GO_DN)
            self.lbtn.config(state=tk.NORMAL, text=BTN_A)
            self.rbtn.config(state=tk.NORMAL, text=BTN_Z)
            self.pbtn.config(state=tk.NORMAL, text=BTN_CHOOSE)
            self.sbtn.config(state=tk.DISABLED)
        elif mode=='add_albums':
            self.ubtn.config(state=tk.NORMAL, text=BTN_GO_UP)
            self.dbtn.config(state=tk.NORMAL, text=BTN_GO_DN)
            self.lbtn.config(state=tk.NORMAL, text=BTN_A)
            self.rbtn.config(state=tk.NORMAL, text=BTN_Z)
            self.pbtn.config(text=u'Add')#/ \u25b6
            self.sbtn.config(state=tk.NORMAL, text=BTN_BACK)
        elif mode=='ready_to_play':
            self.ubtn.config(state=tk.NORMAL, text=BTN_GO_UP)
            self.dbtn.config(state=tk.NORMAL, text=BTN_GO_DN)
            self.lbtn.config(state=tk.NORMAL, text=BTN_A)
            self.rbtn.config(state=tk.NORMAL, text=BTN_Z)
            self.pbtn.config(state=tk.NORMAL, text=BTN_PPAUSE)
            self.sbtn.config(state=tk.NORMAL, text=BTN_BACK)
        elif mode=='playing':
            self.pbtn.config(text=BTN_PAUSE)
            self.ubtn.config(text=BTN_VUP)
            self.dbtn.config(text=BTN_VDN)
            self.lbtn.config(state=tk.NORMAL, text=BTN_PREV)
            self.rbtn.config(state=tk.NORMAL, text=BTN_NEXT)
            self.sbtn.config(state=tk.NORMAL, text=BTN_STOP)

    def appendToCommandsQueue(self, command):
        """ Appends a command to the end of the queue, raises USR1 """
        self.commandsQueue.append(command)
        os.kill(os.getpid(), signal.SIGUSR1)


    def onExit(self):
        """ Correctly destroys the window and says to main thread that
            we need to exit. """
#        if tkMessageBox.askokcancel("Quit", "Stop playing?"):
        self.root.quit()
        self.quitting = True
        os.kill(os.getpid(), signal.SIGUSR1)


    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.onExit)
        self.root.tk.call('encoding', 'system', 'utf-8')

        self.root.geometry("320x240+0+0")
        #tkMessageBox.showinfo("UTF-8 example", u'\ud83d\udd08')

# To use this on Adafruit's LCD for RPi
#    uncomment  the following line
        #self.root.attributes("-fullscreen", True)

        self.initUI()

        print 'GUI initialized.'

        self.UIinitialized = True

        self.root.mainloop()



def main():

    gui = Gui()

    while True:
        if gui.quitting:
            print 'quitting...'
            break
        else:
            while gui.commandsQueue != []:
                command = gui.commandsQueue.popleft()
                if command=='p':
                    gui.clearListBox()
                    msg = []
                    for i in xrange(10):
                        msg.append(randomString(15))
                    gui.feedToListbox(msg)
                else:
                    print command

            sleep(0.1)

    return 0



if __name__ == '__main__':
    main()

