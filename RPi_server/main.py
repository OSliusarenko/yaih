#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
from time import sleep

from player2 import Player
from gui import Gui


currentMode = ''
chosenArtist = ''
chosenAlbum = ''

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
    global chosenArtist
    global chosenAlbum


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
        global chosenArtist
        idx, chosenArtist = gui.getListBoxSelectedLine()
        msg = player.MPDscanArtistsAlbums(chosenArtist)
        currentChoice = 0
        maxChoice = len(msg)
        gui.clearListBox()
        gui.feedToListbox(msg)
        gui.selectListBoxLine(currentChoice)
        
        
    def addChosenAlbum():
        global currentChoice
        global maxChoice
        global chosenArtist
        global chosenAlbum
        idx, chosenAlbum = gui.getListBoxSelectedLine()
        player.MPDaddArtistAlbumToPlaylist(chosenArtist, chosenAlbum)
        gui.setStatus(u'Album \' {:s}\' added!'.format(chosenAlbum))

        



    while not gui.UIinitialized:
        sleep(0.1)

    if player.connected_to_mpd:
        #gui.setStatus('Updating music database...')
        #player.MPDupdateDatabase()
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
                            if currentMode=='ready_to_play':
                                setMode('add_albums')
                        gui.selectListBoxLine(currentChoice)
                    elif command=='u':
                        if currentChoice-1>=0:
                            currentChoice -= 1
                            if currentMode=='ready_to_play':
                                setMode('add_albums')
                        gui.selectListBoxLine(currentChoice)
                    elif command=='p':
                        if currentMode=='select_artists':
                            oldArtistChoice = currentChoice
                            setMode('add_albums')
                            showAlbums()
                        elif currentMode=='add_albums':
                            setMode('ready_to_play')
                            addChosenAlbum()
                    elif command=='s':
                        if currentMode=='ready_to_play':
                                setMode('add_albums')
                        if currentMode=='add_albums':
                            setMode('select_artists')
                            showArtists('curr')
                            currentChoice = oldArtistChoice
                            gui.selectListBoxLine(currentChoice)
                    elif command=='set_selection':
                        if currentMode=='ready_to_play':
                                setMode('add_albums')
                        idx, value = gui.getListBoxSelectedLine()
                        currentChoice = idx[0]
                    elif command=='c':
                        player.MPDclearPlayList()
                        if currentMode=='ready_to_play':
                                setMode('add_albums')
                        gui.setStatus('Current playlist is empty')
                    else:
                        print command

        player.MPDserverDisconnect()

    else:
        print 'Connection problems'




    return 0


if __name__ == '__main__':
    main()

