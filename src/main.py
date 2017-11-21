import midi as Midi
import audioRec as Rec
import time
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



	def continue_match(self):
		return "hi"

if __name__ == "__main__" :
	process = Main()

	process.intial_match()
