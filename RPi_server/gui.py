#!/usr/bin/python
# -*- coding: utf-8 -*-

import ttk 
import Tkinter as tk
import tkMessageBox
import threading

from functools import partial
from time import sleep

class Gui(threading.Thread):
    
    quitting = False
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
            
        ubtn = tk.Button(self.root, text=u"\u25b2", 
                         command=lambda : self.commandsQueue.append('u'))
        ubtn.grid(row=1, column=2)
        
        dbtn = tk.Button(self.root, text=u"\u25bc",
                         command=lambda : self.commandsQueue.append('d'))
        dbtn.grid(row=3, column=2)

        lbtn = tk.Button(self.root, text=u"\u25c0",
                         command=lambda : self.commandsQueue.append('l'))
        lbtn.grid(row=2, column=1, padx=5)

        rbtn = tk.Button(self.root, text=u"\u25b6",
                         command=lambda : self.commandsQueue.append('r'))
        rbtn.grid(row=2, column=3, padx=5)
        
        sbtn = tk.Button(self.root, text=u"\u25a0",
                         command=lambda : self.commandsQueue.append('s'))
        sbtn.grid(row=4, column=1)

        pbtn = tk.Button(self.root, height=1, width=6,
                               text=u"\u25b6\u25ae\u25ae",
                         command=lambda : self.commandsQueue.append('p'))
        pbtn.grid(row=4, column=2, columnspan=2)

        self.var = tk.StringVar()
        self.label = tk.Label(self.root, text=0, textvariable=self.var)  
        self.label.grid(row=6, column=0, columnspan=2, rowspan=1, 
            padx=1, pady=1, sticky=(tk.S+tk.W))
            
        fbtn = tk.Button(self.root, text="flush", height=1, width=2,
                         command=self.flush)
        fbtn.grid(row=6, column=2)
        cbtn = tk.Button(self.root, text="Close", height=1, width=2,
                         command=partial(self.onExit, self.root))
        cbtn.grid(row=6, column=3)
        
#        self.root.pack(fill=tk.BOTH, expand=1)


    def flush(self):
        
        while self.commandsQueue != []:
            self.lb.insert(tk.END, self.commandsQueue.pop(0))

    def onSelect(self, val):
      
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)   

        self.var.set(value)
        
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
#        self.root.attributes("-fullscreen", True)

        self.initUI()
        
        print 'Hello'
        
        self.root.mainloop()



def main():
    
    gui = Gui()
    
    i = 0

    while True:
        if gui.quitting:
            print 'quitting...'
            break
        else:
            while gui.commandsQueue != []:
                print gui.commandsQueue.pop(0)
                
            sleep(0.1)




if __name__ == '__main__':
    main()  
