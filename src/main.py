import midi as Midi
import audioRec as Rec
import tempo as Tempo
import time
import spidev
import math
from threading import Thread

noteOffset = 3 #are notes zero indexed?

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
	if dataNotes != lastData and math.floor(nowTime) != math.floor(lastTime):
		msg = Midi.Message()
		for i in range(len(dataNotes)):
			if dataNotes[i] == True and lastData[i] == False:
				messageType = 'note_on'
				msg = Midi.Message(messageType, note=(noteOffset + i), velocity=64, time=math.floor(time.time()))
				track.append(msg)
				pressDown.append(dataNotes[i])
			elif dataNotes[i] == False and lastData[i] == True:
				messageType = 'note_off'
				msg = Midi.Message(messageType, note=(noteOffset + i), velocity=64, time=math.floor(time.time()))
				track.append(msg)
				letGo.append(dataNotes[i])
		lastData = dataNotes
		lastTime = nowTime
	return lastData, lastTime, pressDown, letGo

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
		self.initial_match()
		self.human_played = []
		self.human_letGo = []
		self.human_tempo = 0
		self.tempo_scale = 1

	def setSong(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

	def initial_match(self,spi):
		set = Thread(target = self.setSong)
		set.start()
		print "running simultaneously"
		count = 0
		while self.transcript == []:
			data = spi.readbytes(n)
			dataNotes = hexToNote(data) #true/false array
			now = time.time()
			lastData = list() # last note value, last timestamp
			lastTime = 0
			while time.time() - now < 5:
				data = spi.readbytes(n)
				dataNotes = hexToNote(data)
				lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
				if pressDown != []:
					self.human_played.append(pressDown)
				if letGo != []:
					self.human.letGo.append(letGo)

		print(self.transcript)
		self.time_current = time.time()*1000

	def update_transcript(self):
		return "hi"

	def continue_match(self, pressDown, letGo):
		return "hi"


if __name__ == "__main__" :
	process = Main()
	spi = spidev.SpiDev()
	bus = ""
	device = ""
	spi.open(bus, device)
	process.intial_match(spi)
	n = 0 # number of bytes
	# get unique data from the spi thing
	# convert hex to mido keys
	# append to list that would store 5 seconds -> tempo matching () -> bpm -> 
	# update tempo_scale = new bpm/old bpm
	# continue match()
	while True:
		tempoSample = Midi.MidiFile()
		tempoSamplePath = 'tempo.mid'
		track = Midi.MidiTrack()
		now = time.time()
		lastData = list() # last note value, last timestamp
		lastTime = 0
		while time.time() - now < 5:
			data = spi.readbytes(n)
			dataNotes = hexToNote(data)
			lastData, lastTime, pressDown, letGo = getUniqueNotes(lastTime, lastData, dataNotes)
			if pressDown != [] or letGo != []:
				process.continue_match(pressDown, letGo)
		tempoSample.save(tempoSamplePath)
		bpm = Tempo.get_tempo_bpm(tempoSamplePath)
		process.human_tempo = bpm
	spi.close()
	process.continue_match()
