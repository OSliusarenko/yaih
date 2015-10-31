#!/usr/bin/python
# -*- coding: utf-8 -*-

import ttk
import Tkinter as tk
import tkMessageBox
import threading

import random # temporarily, remove after
import string

from functools import partial
from time import sleep

def randomString(length):
    return ''.join(random.choice(string.lowercase+string.digits+
                   string.uppercase) for i in range(length))

class Gui(threading.Thread):

    quitting = False
    UIinitialized = False
    commandsQueue = list()  # storage for all commands


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

        self.ubtn = tk.Button(self.root, text=u"\u25b2",
                         command=lambda : self.commandsQueue.append('u'))
        self.ubtn.grid(row=1, column=2)

        self.dbtn = tk.Button(self.root, text=u"\u25bc",
                         command=lambda : self.commandsQueue.append('d'))
        self.dbtn.grid(row=3, column=2)

        self.lbtn = tk.Button(self.root, text=u"\u25c0",
                         command=lambda : self.commandsQueue.append('l'))
        self.lbtn.grid(row=2, column=1, padx=5)

        self.rbtn = tk.Button(self.root, text=u"\u25b6",
                         command=lambda : self.commandsQueue.append('r'))
        self.rbtn.grid(row=2, column=3, padx=5)

        self.sbtn = tk.Button(self.root, text=u"\u25a0",
                         command=lambda : self.commandsQueue.append('s'))
        self.sbtn.grid(row=4, column=1)

        self.pbtn = tk.Button(self.root, height=1, width=6,
                               text=u"\u25b6\u25ae\u25ae",
                         command=lambda : self.commandsQueue.append('p'))
        self.pbtn.grid(row=4, column=2, columnspan=2)

        self.var = tk.StringVar()
        self.label = tk.Label(self.root, text=0, textvariable=self.var)
        self.label.grid(row=6, column=0, columnspan=2, rowspan=1,
            padx=1, pady=1, sticky=(tk.S+tk.W))

        self.fbtn = tk.Button(self.root, text="flush", height=1, width=2,
                         command=self.flush)
        self.fbtn.grid(row=6, column=2)
        self.cbtn = tk.Button(self.root, text="Close", height=1, width=2,
                         command=partial(self.onExit, self.root))
        self.cbtn.grid(row=6, column=3)


    def flush(self):
        """ Temporary, delete afterwards """
        while self.commandsQueue != []:
            self.lb.insert(tk.END, self.commandsQueue.pop(0))


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
        value = self.lb.get(idx)
        return idx, value


    def setStatus(self, value):
        self.var.set(value)


    def onSelect(self, val):
        self.commandsQueue.append('set_selection')


    def setMode(self, mode):
        if mode=='select_artists':
            self.lbtn.config(state=tk.NORMAL, text='A<')
            self.rbtn.config(state=tk.NORMAL, text='>Z')
            self.pbtn.config(text='Choose')
            self.sbtn.config(state=tk.DISABLED)
        elif mode=='add_albums':
            self.lbtn.config(state=tk.DISABLED)
            self.rbtn.config(state=tk.DISABLED)
            self.pbtn.config(text=u'+/ \u25b6')
            self.sbtn.config(state=tk.NORMAL, text='<-')


    def onExit(self, frame):
        """ Correctly destroys the window and says to main thread that
            we need to exit.
            Of course, since it is a member function of a class with
            just one window, we could use this function without 'frame'
            argument, and just do 'self.root.quit()'. But it's fun to
            use 'partial' :) """
        if tkMessageBox.askokcancel("Quit", "Stop playing?"):
            self.quitting = True
            frame.quit()


    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW",
                                partial(self.onExit, self.root))

        self.root.geometry("320x240+0+0")

# To use this on Adafruit's LCD for RPi
#    uncomment  the following line
#        self.root.attributes("-fullscreen", True)

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
                command = gui.commandsQueue.pop(0)
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

