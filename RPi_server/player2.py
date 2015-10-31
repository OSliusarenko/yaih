from mpd import MPDClient
from time import sleep

class Player():
    """ Main class. Supports communicating with MPD """

    connected_to_mpd = False
    currentLetterNumber = 0
    maxLetterNumber = 0

    def __init__(self):
        """ Coonects to MPD, prints version """
        self.client = MPDClient()               # create client object
        self.client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None

        try:
            self.client.connect("localhost", 6600)  # connect to localhost:6600
            print 'MPD version',
            print(self.client.mpd_version)          # print the MPD version
            self.connected_to_mpd = True
        except:
            self.connected_to_mpd = False


    def MPDserverDisconnect(self):
        self.client.close()                     # send the close command
        self.client.disconnect()                # disconnect from the server


    def MPDupdateDatabase(self):
        """ Updates MPD's music database """
        self.client.update()
        print('Updating music database...')
        while 'updating_db' in self.client.status():
            sleep(1)
        print('Done!')


    def MPDscanArtists(self):
        """ Scans music database for unique artists names,
            makes the DB of their names first letters """
        print('Building structure...')
        self.artists = sorted(self.client.list('artist'))
        self.artistsFirstLettersU = []
        for i, artist in enumerate(self.artists):
            if len(artist)>0:
                cU = artist.decode('utf-8')[0]
                if cU not in self.artistsFirstLettersU:
                    self.artistsFirstLettersU.append(cU)
        self.maxLetterNumber = len(self.artistsFirstLettersU)
        print('Done!')


    def MPDscanArtistsAlbums(self, myartist):
        """ Scans music database for artist's albums
            returns albums names """
        myalbums = sorted(self.client.list('album', 'artist', myartist))
        return myalbums


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


    def currLetter(self):
        return self.MPDchooseArtistsWithFirstLetter(
                                               self.currentLetterNumber)

"""    def temp(self):
            if i!=0:
                myalbumid = int(input('Disc '))
            else:
                myalbumid = 0
            if 0<=myalbumid<len(myalbums):
                myalbum = myalbums[myalbumid]
                print '\nChosen album', myalbum, '\n'

                # TODO: depend on MPD version
                client.clear()
                myplaylist = client.find('artist', myartist, 'album', myalbum)

                for c in myplaylist:
                    client.add(c['file'])
                ###
                client.play()
            else:
                print 'Album id out of range'
        else:
            print 'Artist id out of range'
"""


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





