from mpd import MPDClient
from mpd import ConnectionError
from time import sleep
import alsaaudio

class Player():
    """ Main class. Supports communicating with MPD """

    connected_to_mpd = False
    currentLetterNumber = 0
    maxLetterNumber = 0

    def __init__(self):
        """ Coonects to MPD, prints version """
        self.client = MPDClient()               # create client object
#        self.client.timeout = 10                # network timeout in seconds (floats allowed), default: None
#        self.client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None

        self.MPDserverconnect()
        self.mixer = alsaaudio.Mixer(control='PCM', id=0, cardindex=1)

    def MPDnext(self):
        for i in xrange(5):
            try:
                self.client.next()
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDprev(self):
        for i in xrange(5):
            try:
                self.client.previous()
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDserverconnect(self):
        try:
            self.client.connect("localhost", 6600)  # connect to piplay:6600
            print 'MPD version',
            print(self.client.mpd_version)          # print the MPD version
            self.connected_to_mpd = True
        except:
            self.connected_to_mpd = False


    def MPDserverDisconnect(self):
        for i in xrange(5):
            try:
                self.client.close()                     # send the close command
                self.client.disconnect()                # disconnect from the server
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDstatus(self):
        for i in xrange(5):
            try:
                return self.client.status()
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDupdateDatabase(self):
        """ Updates MPD's music database """
        for i in xrange(5):
            try:
                self.client.update()
                print('Updating music database...')
                while 'updating_db' in self.client.status():
                    sleep(1)
                print('Done!')
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDclearPlayList(self):
        for i in xrange(5):
            try:
                self.client.clear()
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDplay(self):
        for i in xrange(5):
            try:
                self.client.play()
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDscanArtists(self):
        """ Scans music database for unique artists names,
            makes the DB of their names first letters """
        print('Building structure...')
        for i in xrange(5):
            try:
                self.artists = sorted(self.client.list('artist'))
                self.artistsFirstLettersU = []
                for i, artist in enumerate(self.artists):
                    if len(artist)>0:
                        cU = artist.decode('utf-8')[0]
                        if cU not in self.artistsFirstLettersU:
                            self.artistsFirstLettersU.append(cU)
                self.maxLetterNumber = len(self.artistsFirstLettersU)
                print('Done!')
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDscanArtistsAlbums(self, myartist):
        """ Scans music database for artist's albums
            returns albums names """
        for i in xrange(5):
            try:
                myalbums = sorted(self.client.list('album',
                                                   'artist', myartist))
                return myalbums
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDpause(self):
        for i in xrange(5):
            try:
                self.client.pause()
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')


    def MPDchooseArtistsWithFirstLetter(self, chosenLetterNumber):
        """ Selects artists whose names start with
            self.artistsFirstLettersU[chosenLetterNumber] """
        if chosenLetterNumber<self.maxLetterNumber:
            chosenLetterU = self.artistsFirstLettersU[chosenLetterNumber]
        else:
            print 'Out of range'
            chosenLetterU = self.artistsFirstLettersU[0]
        msg = []
        for i, artist in enumerate(self.artists):
            if len(artist)>0:
                cU = artist.decode('utf-8')[0]
                if cU==chosenLetterU:
                    msg.append(artist)
        return msg


    def MPDwhat_song_playing(self):
        for i in xrange(5):
            try:
                return self.client.currentsong()
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')



    def MPDaddArtistAlbumToPlaylist(self, myartist, myalbum):
        for i in xrange(5):
            try:
                myplaylist = self.client.find('artist', myartist, 'album', myalbum)
                for c in myplaylist:
                    self.client.add(c['file'])
                break
            except:
                self.connected_to_mpd = False
                self.MPDserverconnect()
        else:
            print('Maximum attempts exceeded')



    def nextLetter(self):
        if self.currentLetterNumber+1<self.maxLetterNumber:
            self.currentLetterNumber += 1
        return self.MPDchooseArtistsWithFirstLetter(
                                               self.currentLetterNumber)


    def prevLetter(self):
        if self.currentLetterNumber-1>=0:
            self.currentLetterNumber -= 1
        return self.MPDchooseArtistsWithFirstLetter(
                                               self.currentLetterNumber)


    def VolDn(self):
        vol = int(self.mixer.getvolume()[0])
        vol -= 10
        if vol < 0:
            vol = 0
        self.mixer.setvolume(vol)


    def VolUp(self):
        vol = int(self.mixer.getvolume()[0])
        vol += 10
        if vol > 100:
            vol = 100
        self.mixer.setvolume(vol)


    def currLetter(self):
        return self.MPDchooseArtistsWithFirstLetter(
                                               self.currentLetterNumber)



def main():

    player = Player()

    if player.connected_to_mpd:
        player.MPDupdateDatabase()
        player.MPDscanArtists()

        for artist in player.artists:
            print artist

        print ' '

        for i, artist in player.MPDchooseArtistsWithFirstLetter(2):
            print i, artist

        player.MPDserverDisconnect()

    else:
        print 'Connection problems'

    return 0



if __name__ == '__main__':
    main()





