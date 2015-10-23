from mpd import MPDClient
from time import sleep
client = MPDClient()               # create client object
client.timeout = 10                # network timeout in seconds (floats allowed), default: None
client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None

try:
	client.connect("localhost", 6600)  # connect to localhost:6600
	print 'MPD version',
	print(client.mpd_version)          # print the MPD version
	connected_to_mpd = True
except:
	connected_to_mpd = False

if connected_to_mpd:
	client.update()
	print('Updating music database...')
	while 'updating_db' in client.status():
		sleep(1)
	print('Done!')
	
	print('Building structure...')
	artists = sorted(client.list('artist'))
	artistsFirstLettersU = []
	for i, artist in enumerate(artists):
		if len(artist)>0:
			cU = artist.decode('utf-8')[0]
			if cU not in artistsFirstLettersU:
				artistsFirstLettersU.append(cU)
	print('Done!')
	
	for cU in artistsFirstLettersU:
		print cU,
	chosenLetterNumber = int(input('\n Letter number '))
	if chosenLetterNumber<len(artistsFirstLettersU):
		chosenLetterU = artistsFirstLettersU[chosenLetterNumber]
	else:
		print 'Out of range'
		chosenLetterU = artistsFirstLettersU[0]

	for i, artist in enumerate(artists):
		if len(artist)>0:
			cU = artist.decode('utf-8')[0]
			if cU==chosenLetterU:
				print i, artist

	myartistid = int(input('Artist '))

	if 0<=myartistid<len(artists):
		myartist = artists[myartistid]
		myalbums = sorted(client.list('album', 'artist', myartist))
		print 'Artist\'s', myartist, 'albums:'
		for i, c in enumerate(myalbums):
			print i, c.decode('utf-8')
			
	
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

	client.close()                     # send the close command
	client.disconnect()                # disconnect from the server
else:
	print 'Connection problems'
