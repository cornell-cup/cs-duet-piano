from dejavu import Dejavu
from dejavu.recognize import MicrophoneRecognizer

config = {
	"database": {
		"host": "127.0.0.1",
		"user": "root",
		"passwd": "root",
		"db": "dejavu",
	},
	"database_type": "mysql",
	"fingerprint_limit": 15
}

def recognizeAudio():
	djv = Dejavu(config)

	djv.fingerprint_directory("songs", [".mp3"], 3)

	song = djv.recognize(MicrophoneRecognizer, seconds=5)

	print(song)
	return song['song_name']
