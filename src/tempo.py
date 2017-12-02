import pretty_midi

def get_tempo_bpm(midiFilePath):
	midi_data = pretty_midi.PrettyMIDI(midiFilePath)
	return midi_data.estimate_tempo()
