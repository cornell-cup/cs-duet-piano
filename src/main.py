import midi as Midi
import audioRec as Rec

song = Rec.recognizeAudio()

transcript = Midi.setSong(song)

