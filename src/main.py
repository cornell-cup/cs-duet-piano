import midi as Midi
import audioRec as Rec
import time
import spidev
import math
from threading import Thread

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
		self.human_tempo = 0
		self.tempo_scale = 1

	def setSong(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

	def initial_match(self):
		set = Thread(target = self.setSong)
		set.start()
		print "running simultaneously"
		count = 0
		while self.transcript == []:
			self.human_played.append()

		print(self.transcript)
		self.time_current = time.time()*1000

	def update_transcript(self):


	def continue_match(self):
		return "hi"


if __name__ == "__main__" :
	process = Main()
	process.intial_match()
	spi = spidev.SpiDev()
	bus = ""
	device = ""
	spi.open(bus, device)
	n = 0 # number of bytes
	# get unique data from the spi thing
	# convert hex to mido keys
	# append to list that would store 5 seconds -> tempo matching () -> bpm -> 
	# update tempo_scale = new bpm/old bpm
	# continue match()
	noteOffset = 3
	while True:
		tempoSample = mido.MidiFile()
		tempoSamplePath = 'tempo.mid'
		track = mido.MidiTrack()
		now = time.time()
		lastData = list() # last note value, last timestamp
		lastTime = 0
		while time.time() - now < 5:
			data = spi.readbytes(n)
			dataNotes = hexToNote(data)
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
				lastData = dataNotes
				lastTime = nowTime
				process.continue_match(msg)
		tempoSample.save(tempoSamplePath)
		bpm = Tempo.get_tempo_bpm(tempoSamplePath)
		process.human_tempo = bpm
	spi.close()
	process.continue_match()
