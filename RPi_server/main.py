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

letsDo = False

def usr1_signal_handler(ssignal, stack):
    """ Update flag that the signal is the one that we need """
    global letsDo
    letsDo = True

def main():

    gui = Gui()
    player = Player()

    global currentMode
    global currentChoice
    global maxChoice
    global chosenArtist
    global chosenAlbum
    global letsDo

    oldArtistChoice = 0


    def setMode(mode):
        global currentMode
        currentMode = mode
        gui.setMode(currentMode)


    def getMode():
        return currentMode

    def nextsong():
        player.MPDnext()

    def pause():
        player.MPDpause()

    def play():
        player.MPDplay()

    def prevsong():
        player.MPDprev()

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


    def status():
        return player.MPDstatus()


    def volumeUp():
        player.VolUp()


    def volumeDn():
        player.VolDn()


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
        gui.setStatus('Updating music database...')
        player.MPDupdateDatabase()
        gui.setStatus('Scanning artists...')
        player.MPDscanArtists()

        curr_status = status()

        print(curr_status)

        if curr_status['state'] == 'stop':
            gui.setStatus('Stopped')
            showArtists('curr')
            setMode('select_artists')
        elif curr_status['state'] == 'play':
            gui.setStatus('Playing')
            showArtists('curr')
            setMode('playing')
        elif curr_status['state'] == 'pause':
            gui.setStatus('Paused')
            showArtists('curr')
            setMode('ready_to_play')

        signal.signal(signal.SIGUSR1, usr1_signal_handler)

        while True:
            if gui.quitting:
                print 'quitting...'
                break
            else:
                letsDo = False
                while not letsDo:
                    signal.pause()     # wait for interrupt (command?)

                while True:
                    try:
                        command = gui.commandsQueue.popleft()
                    except IndexError:
#                        print 'Empty'
                        break

                    if command=='r':
                        if currentMode in ['select_artists',
                                           'add_albums',
                                           'ready_to_play']:
                            showArtists('next')
                        elif currentMode=='playing':
                            nextsong()
                    elif command=='l':
                        if currentMode in ['select_artists',
                                           'add_albums',
                                           'ready_to_play']:
                            showArtists('prev')
                        elif currentMode=='playing':
                            prevsong()
                    elif command=='d':
                        if currentMode in ['select_artists',
                                           'add_albums',
                                           'ready_to_play']:
                            if currentChoice+1<maxChoice:
                                currentChoice += 1
                                if currentMode=='ready_to_play':
                                    setMode('add_albums')
                            gui.selectListBoxLine(currentChoice)
                        elif currentMode=='playing':
                            volumeDn()
                    elif command=='u':
                        if currentMode in ['select_artists',
                                           'add_albums',
                                           'ready_to_play']:
                            if currentChoice-1>=0:
                                currentChoice -= 1
                                if currentMode=='ready_to_play':
                                    setMode('add_albums')
                            gui.selectListBoxLine(currentChoice)
                        elif currentMode=='playing':
                            volumeUp()
                    elif command=='p':
                        if currentMode=='select_artists':
                            oldArtistChoice = currentChoice
                            setMode('add_albums')
                            showAlbums()
                        elif currentMode=='add_albums':
                            setMode('ready_to_play')
                            addChosenAlbum()
                        elif currentMode=='ready_to_play':
                            setMode('playing')
                            play()
                        elif currentMode=='playing':
                            setMode('ready_to_play')
                            pause()
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

