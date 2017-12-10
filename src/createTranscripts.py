import midi

songs = ['when_the_saints_pnoduet', 'hot_cross_buns_pnoduet']

for s in songs:
	f = open('transcripts/' + s + '.txt', 'w')
	f.write(str(midi.transcribe(s)))
	f.close()
