from dejavu import Dejavu
from dejavu.recognize import MicrophoneRecognizer

config = {
  "database": {
    "host": "127.0.0.1",
    "user" : "root",
    "passwd" : "Operation2x",
    "db" : "dejavu"
  }
}

djv = Dejavu(config)

djv.fingerprint_directory("mp3", [".mp3"], 3)

print djv.db.get_num_fingerprints()

song = djv.recognize(MicrophoneRecognizer, seconds = 10)

print song
