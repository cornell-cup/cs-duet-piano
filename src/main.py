import midi as Midi
import audioRec as Rec
import tempo as Tempo
import time
import spidev
import mido
import math
from threading import Thread

noteOffset = 28 # are notes zero indexed?

def hexToNote(hexcode):
	hex = hexcode.encode("hex")
	pressed = []
	for i in range(len(hex)/4+1):
		sub = hex[i*4:(i+1)*4] #3333
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
		##msg = Midi.Message()
		for i in range(len(dataNotes)):
			if dataNotes[i] == True and lastData[i] == False:
				#messageType = 'note_on'
				#msg = Midi.Message(messageType, note=(noteOffset + i), velocity=64, time=math.floor(time.time()))
				left, right = Midi.splitLR(dataNotes[i])
				pressDown[0] += left
				pressDown[1] += right

			elif dataNotes[i] == False and lastData[i] == True:
				#messageType = 'note_off'
				#msg = Midi.Message(messageType, note=(noteOffset + i), velocity=64, time=math.floor(time.time()))
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
		self.time_current = time.time()*1000
		self.time_start = time.time()*1000

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
		self.human_played = [[],[]]
		self.human_letGo = [[],[]]
		self.human_tempo = 0
		self.tempo_scale = 1

	def setSong(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

	def initial_match(self,spi):
		set = Thread(target = self.setSong)
		set.start()
		print "running simultaneously"
		while self.transcript == []:
			now = time.time()
			lastData = [] # last note value, last timestamp
			lastTime = 0
			while time.time() - now < 5:
				data = spi.readbytes(n)
				dataNotes = hexToNote(data)
				lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
				if pressDown != []:
					self.human_played.append(pressDown)
				if letGo != []:
					self.human_letGo.append(letGo)

		self.time_current = time.time()*1000

		print(self.transcript)

		human_average = sum(self.human_played[0] + self.human_played[1])/len(self.human_played[0]+ self.human_played[1])
		if human_average > 64:
			self.human_side = "R"
			self.robot_transcript = self.transcript[0]
		else:
			self.human_side = "L"
			self.human_transcript = self.transcript[1]

		#based on time_current and notes played by human, get robot note
		skipToL, skipToR = len(self.human_played[0]),len(self.human_played[1])
		currNoteL, currNoteR = self.human_transcript[0][skipToL], self.human_transcript[0][skipToR]
		if currNoteL[1] == self.human_played[0][-1] and currNoteR[1] == self.human_played[1][-1]:
			left_time = currNoteL[0]
			right_time = currNoteR[0]
			for entry in self.robot_transcript[0]:
				if entry[0] > left_time:
					nextNoteL = entry
			for entry in self.robot_transcript[1]:
				if entry[0] > right_time:
					nextNoteR = entry


	'''
	Params: self.queue represented as [five oldest notes, current note, five next notes]
	Returns: Updates queue. Pops off the oldest note and adds in a new note
	'''
	def update_queue(self):
		print "Unimplemented"

	'''
	Params: Updates transcript based tempo
	Returns: Tempo adjusted transcript
	'''
	def update_transcript(self):
		print "Unimplemented"

	def continue_match(self, pressDown, letGo):
		print "Unimplemented"


if __name__ == "__main__" :
	process = Main()
	spi = spidev.SpiDev()
	bus = ""
	device = ""
	spi.open(bus, device)
	process.initial_match(spi)
	end = False
	n = 0 # number of bytes
	# get unique data from the spi thing
	# convert hex to mido keys
	# append to list that would store 5 seconds -> tempo matching () -> bpm -> 
	# update tempo_scale = new bpm/old bpm
	# continue match()
	while not end:
		tempoSample = mido.MidiFile()
		tempoSamplePath = 'tempo.mid'
		track = mido.MidiTrack()
		now = time.time()
		lastData = [] # last note value, last timestamp
		lastTime = 0
		while time.time() - now < 5:
			data = spi.readbytes(n)
			dataNotes = hexToNote(data)
			lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
			if pressDown != [[],[]] or letGo != [[],[]]:
				process.continue_match(pressDown, letGo)
		tempoSample.save(tempoSamplePath)
		bpm = Tempo.get_tempo_bpm(tempoSamplePath)
		process.human_tempo = bpm
		#song reaches end and end is true then
		# need end of song check somewhere
	spi.close()
	process.continue_match()
