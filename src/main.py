import midi as Midi
import audioRec as Rec
import time

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

	def initial_match(self):
		song = Rec.recognizeAudio()
		self.transcript = Midi.transcribe(song)

		print(self.transcript)
		self.time_current = time.time()*1000


	def continue_match(self):
		return "hi"

if __name__ == "__main__" :
	process = Main()
	process.continue_match()