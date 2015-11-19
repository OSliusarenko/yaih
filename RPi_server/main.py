#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
from time import sleep

from player2 import Player
from gui import Gui


currentMode = ''
currentChoice = 0
maxChoice = 0


def usr1_signal_handler(ssignal, stack):
    """ Temporarily nothing """
    pass

def main():

    gui = Gui()
    player = Player()

    global currentMode
    global currentChoice
    global maxChoice


    def setMode(mode):
        global currentMode
        currentMode = mode
        gui.setMode(currentMode)


    def getMode():
        return currentMode


    def showArtists(what):
        global currentChoice
        global maxChoice
        if what=='curr':
            msg = player.currLetter()
        elif what=='next':
            msg = player.nextLetter()
        elif what=='prev':
            msg = player.prevLetter()
        currentChoice = 0
        maxChoice = len(msg)
        gui.clearListBox()
        gui.feedToListbox(msg)
        gui.selectListBoxLine(currentChoice)


    def showAlbums():
        global currentChoice
        global maxChoice
        idx, artist = gui.getListBoxSelectedLine()
        msg = player.MPDscanArtistsAlbums(artist)
        currentChoice = 0
        maxChoice = len(msg)
        gui.clearListBox()
        gui.feedToListbox(msg)
        gui.selectListBoxLine(currentChoice)



    while not gui.UIinitialized:
        sleep(0.1)

    if player.connected_to_mpd:
        gui.setStatus('Updating music database...')
        player.MPDupdateDatabase()
        gui.setStatus('Scanning artists...')
        player.MPDscanArtists()

        gui.setStatus('Stopped')
        showArtists('curr')
        setMode('select_artists')

        signal.signal(signal.SIGUSR1, usr1_signal_handler)

        while True:
            if gui.quitting:
                print 'quitting...'
                break
            else:
                signal.pause()     # wait for interrupt (command?)

                while True:
                    try:
                        command = gui.commandsQueue.popleft()
                    except IndexError:
                        print 'Empty'
                        break

                    if command=='r':
                        showArtists('next')
                    elif command=='l':
                        showArtists('prev')
                    elif command=='d':
                        if currentChoice+1<maxChoice:
                            currentChoice += 1
                        gui.selectListBoxLine(currentChoice)
                    elif command=='u':
                        if currentChoice-1>=0:
                            currentChoice -= 1
                        gui.selectListBoxLine(currentChoice)
                    elif command=='p':
                        oldArtistChoice = currentChoice
                        setMode('add_albums')
                        showAlbums()
                    elif command=='s':
                        if currentMode=='add_albums':
                            setMode('select_artists')
                            showArtists('curr')
                            currentChoice = oldArtistChoice
                            gui.selectListBoxLine(currentChoice)
                    elif command=='set_selection':
                        idx, value = gui.getListBoxSelectedLine()
                        currentChoice = idx[0]
                    else:
                        print command

        player.MPDserverDisconnect()

    else:
        print 'Connection problems'




    return 0


if __name__ == '__main__':
    main()

