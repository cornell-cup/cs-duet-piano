import midi as Midi
import audioRec as Rec
import tempo as Tempo
import time
import mido
import wiringpi
import math
from threading import Thread

noteOffset = 28 # zero indexed notes

def hexToNote(hexcode):
	hex = format(hexcode, '076b')
	pressed = []
	print hex
	print()
	for i in hex:
		bin_sub = bin(int(i, 16))[2:]
		print(bin_sub)
		for key in bin_sub:
			if key == "1":
				pressed.append(True)
			else:
				pressed.append(False)
	return pressed

def noteToHex(notesUpdate):
	left = notesUpdate[0]
	right = notesUpdate[2]
	hexcode = ""
	for i in left:
		hexcode += str(hex(i))
	for i in right:
		hexcode += str(hex(i))
	return hexcode

'''
Params: MIDI integer representation of the key that the pinkie should be on for either hand
Returns: Hex string representation of the key
'''
def getPinkie(chord):
	return hex(min(chord))


class Main:
	def __init__(self):
		self.time_current = time.time() * 1000
		self.time_start = time.time() * 1000

		self.notesUpdate = {0: [], 1: [], 2: [], 3: []}

		self.left_played = []
		self.left_index = [[],[]]
		self.left_queue = []

		self.right_played = []
		self.right_index = [[],[]]
		self.right_queue = []

		self.transcript = []
		self.robot_transcript = []
		self.human_transcript = []

		self.human_side = ""
		self.human_played = [[], []]
		self.human_letGo = [[], []]
		self.human_tempo = 0
		self.tempo_scale = 1

		self.letGo = [[],[]]
		self.pressDown = [[],[]]

		self.nextTime = -1

	def setSong(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

	def initial_match(self, spi):
		set = Thread(target=self.setSong)
		set.start()
		print "running simultaneously"
		#TODO MANUAL NOTE CHECK
		while self.transcript == []:
			now = time.time()
			lastData = []  # last note value, last timestamp
			lastTime = 0
			data = wiringpi.digitalRead(23) #pin 23
			dataNotes = hexToNote(data)
			lastData, lastTime, pressDown, letGo = self.getUniqueNotes(lastTime, lastData, dataNotes)
			if pressDown != []:
				self.human_played.append(pressDown)
			if letGo != []:
				self.human_letGo.append(letGo)

		print(self.transcript)

		human_average = sum(self.human_played[0] + self.human_played[1]) / \
						len(self.human_played[0] + self.human_played[1])
		if human_average > 64:
			self.human_side = "R"
			self.robot_transcript = self.transcript[0]
		else:
			self.human_side = "L"
			self.human_transcript = self.transcript[1]

		# based on time_current and notes played by human, get robot note
		skipToL, skipToR, skipToL2, skipToR2 = len(self.human_played[0]), len(self.human_played[1]), \
											   len(self.human_letGo[0]), len(self.human_letGo[1])

		currNoteL, currNoteR, letGoL, letGoR = self.human_transcript[0][skipToL], self.human_transcript[1][skipToR],\
											   self.human_transcript[2][skipToL2], self.human_transcript[3][skipToR2]

		if currNoteL[1] == self.human_played[0][-1]:
			left_time = currNoteL[0]
		if currNoteR[1] == self.human_played[1][-1]:
			right_time = currNoteR[0]
		if letGoL[1] == self.human_letGo[0][-1]:
			left_time2 = letGoL[1]
		if letGoR[1] == self.human_letGo[1][-1]:
			right_time2 = letGoR[1]

		self.parse_transcript(max(left_time, left_time2, right_time, right_time2))

		self.play_note()

	'''
			Params: [latest_time] represents time of the last action done so far
			Returns: Parses through transcripts and tries to find the time of the next action
					returns a list of notes for a particular 'next time'
	'''
	def getUniqueNotes(self, lastTime, lastData, dataNotes):
		nowTime = time.time()*1000
		if dataNotes != lastData and math.floor(nowTime) != math.floor(lastTime):
			played, letGo = [],[]
			for i in range(len(dataNotes)):
				if dataNotes[i] == True and lastData[i] == False:
					played.append([0, i])
				elif dataNotes[i] == False and lastData[i] == True:
					letGo.append([0, i])

		#parsing based on splitting keyboard in half
		if self.human_side == "L": #robot plays notes greater than 64
			played = [note for note in played if note >64]
			letGo = [note for note in letGo if note >64]
		elif self.human_side == "R": #robot plays notes less than 64
			played = [note for note in played if note <64]
			letGo = [note for note in letGo if note <64]

		#else: initial match -> do not know yet. its all human

		left, right = Midi.splitLR(played)
		self.pressDown[0] += left
		self.pressDown[1] += right

		left, right = Midi.splitLR(letGo)
		self.letGo[0] += left
		self.letGo[1] += right
		lastData = dataNotes
		lastTime = nowTime
		return lastData, lastTime

	def play_note(self):
		self.time_current = time.time()*1000
		while self.time_current!= self.nextTime:
			self.time_current = time.time()*1000
		msg = noteToHex(self.notesUpdate)
		# TODO WRITE MSG TO RASPBERRY PI
		# TODO MSG: (left and right pinkie position, left and right finger positions)
		# play self.notesUpdate after analyzing it


	'''
		Params: [latest_time] represents time of the last action done so far
		Returns: Parses through transcripts and tries to find the time of the next action
				returns a list of notes for a particular 'next time'
	'''
	def parse_transcript(self, latest_time):
		#update = {0: [], 1: [], 2: [], 3: []}
		for i in range(len(self.robot_transcript), 0, -1):
			next = self.find_next(i, latest_time)
			if next[0] > self.nextTime: #tonext[0]do check validity
				next = []
			if i == 0 or i == 1:
				prevNotes = list(set(self.notesUpdate[i+2])^set(self.notesUpdate[i]))
				self.notesUpdate[i] = list(set(prevNotes + next)).sort()  #not sure if sorting is necessary
			else:
				self.notesUpdate[i] = next

	'''
	Params: [i] represents which part of the transcript, [latest_time] represents time of the last action done so far
	Returns: Parses through transcripts and tries to find the time of the next action
			sets the index of last played in transcript
			returns a list of notes for a particular 'next time'
	'''
	def find_next(self, i , latest_time):
		transcript = self.robot_transcript[i]
		if i == 0:
			transcript = transcript[self.left_index[0]:]
		if i == 2:
			transcript = transcript[self.left_index[1]:]
		if i == 1:
			transcript = transcript[self.right_index[0]:]
		if i == 3:
			transcript = transcript[self.right_index[1]:]
		next = []
		for t in range(len(transcript)):
			if  transcript[t][0] > latest_time and (self.nextTime == -1 or self.nextTime >  transcript[t][0]):
				self.nextTime =  transcript[t][0]
				next.append( transcript[t][1])
			elif  transcript[t][0] > self.nextTime:
				if i == 0:
					self.left_index[0] = t
				if i == 2:
					self.left_index[1] = t
				if i == 1:
					self.right_index[0] = t
				if i == 3:
					self.right_index[1] = t
				break
		next = [self.nextTime, next]
		return next

	'''
	Params: Updates future transcript based tempo
	Returns: Tempo adjusted transcript
	'''
	def update_transcript(self):
		#partitions of not-played notes
		l_press = self.robot_transcript[0][self.left_index[0]:]
		l_letgo = self.robot_transcript[2][self.left_index[1]:]
		r_press = self.robot_transcript[1][self.right_index[0]:]
		r_letgo = self.robot_transcript[3][self.right_index[1]:]
		lst = [l_press, l_letgo, r_press, r_letgo]

		for l in lst:
			start = l[0]
			rest = l[1:]
			for chord in rest:
				delta = chord[0] - start
				chord[0] = delta/float(self.tempo_scale)

	#TODO THIS ENTIRE FUNCTION NEEDS HELP. S O S
	def checkPlaying(self):
		print ("Unimplemented")


	def continue_match(self, pressDown, letGo):
		#TODO check if note played was the correct note
		self.left_played[0] += pressDown[0]
		self.left_played[1] += letGo[0]
		self.right_played[0] += pressDown[1]
		self.right_played[1] += letGo[1]
		self.parse_transcript(time.time())


if __name__ == "__main__":
	process = Main()
	process.initial_match()
	#pins: 7 hand f,8 hand f,24 sensors,23 step
	wiringpi.wiringPiSetupGpio()	
	channel = 1
	speed = 500000
	wiringpi.wiringPiSPISetup(channel, speed)
	wiringpi.pinMode(7, 1)
	wiringpi.pinMode(8, 1)
	wiringpi.pinMode(23, 1)
	wiringpi.pinMode(24, 1)
	buf = "hello"
	end = False
	retlen, retdata = wiringpi.wiringPiSPIDataRW(channel, buf)
	# receiving 84 bits / 8 = 11 bytes
	# convert hex to mido keys
	# append to list that would store 5 seconds -> tempo matching () -> bpm -> 
	# update tempo_scale = new bpm/old bpm
	# continue match()

	while not end:
		tempoSample = mido.MidiFile()
		tempoSamplePath = 'tempo.mid'
		track = mido.MidiTrack()
		tempoSample.tracks.append(track)

		now = time.time()*1000
		lastData = []  # last note value, last timestamp
		lastTime = 0
		pressDown = []
		letGo = []
		while time.time()*1000 - now < 5:
			data = wiringpi.digitalRead(24) #pin 24
			dataNotes = hexToNote(data)

			if pressDown != [[], []] or letGo != [[], []]:
				process.continue_match(pressDown, letGo)
			# song reaches end and end is true then
			# need end of song check somewhere
			nowTime = time.time()
		
			if dataNotes != lastData and math.floor(nowTime) != math.floor(lastTime):
				msg = mido.Message()
				for i in range (0, len(dataNotes)):
					if dataNotes[i] == True and lastData[i] == False:
						messageType = 'note_on'
						msg = mido.Message(messageType, note=(noteOffset + i), velocity=64, time = math.floor(time.time()))
						track.append(msg)
						#TODO split between human and robot
						left, right = Midi.splitLR(dataNotes[i])
						process.pressDown[0] += left
						process.pressDown[1] += right

					elif dataNotes[i] == False and lastData[i] == True:
						messageType = 'note_off'
						msg = mido.Message(messageType, note=(noteOffset + i), velocity=64, time = math.floor(time.time()))
						track.append(msg)
						#TODO split between human and robot
						left, right = Midi.splitLR(dataNotes[i])
						process.letGo[0] += left
						process.letGo[1] += right

				tempoSample.save(tempoSamplePath)
				bpm = Tempo.get_tempo_bpm(tempoSamplePath)

				process.tempo_scale = bpm/process.human_tempo
				process.human_tempo = bpm
				process.update_transcript()
				process.continue_match()
		process.continue_match()
