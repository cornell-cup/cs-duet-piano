from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

config = {
	"database": {
		"host": "127.0.0.1",
		"user": "root",
		"passwd": "duetpiano",
		"db": "dejavu",
	},
	"database_type": "mysql",
	"fingerprint_limit": 15
}

djv = Dejavu(config)

djv.fingerprint_directory("songs", [".mp3"], 3)

song = djv.recognize(FileRecognizer, "songs/saints.mp3")
song2 = djv.recognize(MicrophoneRecognizer, seconds=15)

print song
print song2
