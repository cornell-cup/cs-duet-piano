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
	hex = hexcode.encode("hex")
	pressed = []
	for i in range(len(hex) / 4 + 1):
		sub = hex[i * 4:(i + 1) * 4]  # 3333
		print sub
		bin_sub = bin(int(sub, 16))[2:]
		for key in bin_sub:
			if key == "1":
				pressed.append(True)
			else:
				pressed.append(False)
	return pressed


def getUniqueNotes(lastTime, lastData, dataNotes):
	nowTime = time.time()
	pressDown = []
	letGo = []
	dataNotes = [[0, note] for note in dataNotes]
	if dataNotes != lastData and math.floor(nowTime) != math.floor(lastTime):
		for i in range(len(dataNotes)):
			if dataNotes[i] == True and lastData[i] == False:
				left, right = Midi.splitLR(dataNotes[i])
				pressDown[0] += left
				pressDown[1] += right
				lastData = dataNotes
				lastTime = nowTime

			elif dataNotes[i] == False and lastData[i] == True:
				left, right = Midi.splitLR(dataNotes[i])
				letGo[0] += left
				letGo[1] += right
				lastData = dataNotes
				lastTime = nowTime
		
	return lastData, lastTime, pressDown, letGo


'''
Params: MIDI integer representation of the key that the pinkie should be on for either hand
Returns: Hex string representation of the key
'''
def getPinkie(key):
	return hex(key)


class Main:
	def __init__(self):
		self.time_current = time.time() * 1000
		self.time_start = time.time() * 1000

		self.notesUpdate = {0: [], 1: [], 2: [], 3: []}

		self.left_played = []
		self.left_index = 0
		self.left_queue = []

		self.right_played = []
		self.right_index = 0
		self.right_queue = []

		self.transcript = []
		self.robot_transcript = []
		self.human_transcript = []

		self.human_side = ""
		self.human_played = [[], []]
		self.human_letGo = [[], []]
		self.human_tempo = 0
		self.tempo_scale = 1

	def setSong(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

	def initial_match(self, spi):
		set = Thread(target=self.setSong)
		set.start()
		print "running simultaneously"
		while self.transcript == []:
			now = time.time()
			lastData = []  # last note value, last timestamp
			lastTime = 0
			while time.time() - now < 5:
				data = wiringpi.digitalRead(23) #pin 23
				dataNotes = hexToNote(data)
				lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
				if pressDown != []:
					self.human_played.append(pressDown)
				if letGo != []:
					self.human_letGo.append(letGo)

		print(self.transcript)

		human_average = sum(self.human_played[0] + self.human_played[1]) / len(
			self.human_played[0] + self.human_played[1])
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

	def play_note(self):
		self.time_current = time.time()*1000
		while self.time_current!= self.nextTime:
			self.time_current = time.time()*1000
		# TODO WRITE MSG TO RASPBERYY PI


	'''
		Params: [i] represents which part of the transcript, [latest_time] represents time of the last action done so far
		Returns: Parses through transcripts and tries to find the time of the next action
				returns a list of notes for a particular 'next time'
	'''
	def parse_transcript(self, latest_time):
		update = {0: [], 1: [], 2: [], 3: []}
		for i in range(len(self.robot_transcript), 0, -1):
			next = self.find_next(i, latest_time)
			if next[0] > self.nextTime:
				next = []
			if i == 0 or i == 1:
				prevNotes = list(set(self.notesUpdate[i+2])^set(self.notesUpdate[i]))
				self.notesUpdate[i] = list(set(prevNotes + next)).sort()  #not sure if sort is necessary
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
		next = []
		self.nextTime = -1
		for t in range(transcript):
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
	Params: self.queue represented as [five oldest notes, current note, five next notes]
	Returns: Updates queue. Pops off the oldest note and adds in a new note
	'''
	def update_queue(self):
		print "Unimplemented"

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
			for chord in l:
				delta = chord[0] - start
				chord[0] = delta/float(self.tempo_scale)


	def continue_match(self, pressDown, letGo):
		print "Unimplemented"


if __name__ == "__main__":
	process = Main()
	process.intial_match()
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
	retlen, retdata = wiringpi.wiringPiSPIDataRW(0, buf)
	# receiving 84 bits / 8 = 11 bytes
	# convert hex to mido keys
	# append to list that would store 5 seconds -> tempo matching () -> bpm -> 
	# update tempo_scale = new bpm/old bpm
	# continue match()

	while not end:
		tempoSample = mido.MidiFile()
		tempoSamplePath = 'tempo.mid'
		track = mido.MidiTrack()
		now = time.time()
		lastData = []  # last note value, last timestamp
		lastTime = 0
		while time.time() - now < 5:
			data = wiringpi.digitalRead(24) #pin 24
			dataNotes = hexToNote(data)
			lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
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
					elif dataNotes[i] == False and lastData[i] == True:
						messageType = 'note_off'
						msg = mido.Message(messageType, note=(noteOffset + i), velocity=64, time = math.floor(time.time()))
						track.append(msg)
				process.continue_match(msg)
				tempoSample.save(tempoSamplePath)
				bpm = Tempo.get_tempo_bpm(tempoSamplePath)
				process.human_tempo = bpm
		process.continue_match()
