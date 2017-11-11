from mido import MidiFile

mid = MidiFile('midi/when_the_saints_pnoduet.mid')

def to_absolute_time(track):
    messages = []
    now = 0
    for msg in track:
        messages.append(msg.copy(time=now+msg.time))
        now += msg.time
    return messages

chordsOn, chordsOff=[],[]
for i, track in enumerate(mid.tracks):
  if i != 0:
    print('Track {}: {}'.format(i, track.name))
    track_on, track_off = {}, {}
    for msg in to_absolute_time(track):
      if not msg.is_meta and msg.type == 'note_on':
        if msg.time not in track_on:
          track_on[msg.time] = [msg.note]
        else:
          track_on[msg.time].append(msg.note)
      if not msg.is_meta and msg.type == 'note_off':
        if msg.time not in track_off:
          track_off[msg.time] = [msg.note]
        else:
          track_off[msg.time].append(msg.note)
    chordsOn.append(track_on)
    chordsOff.append(track_off)
#print(chordsOn)
#print(chordsOff)

leftHand, rightHand = [],[]

l,r = [],[]
d= chordsOn[1]
left = []
right = []
for key in d.keys():
  keys = sorted(d[key])
  key_max = keys[-1]
  key_min = keys[0]
  split = key_min + 12
  if key_max != key_min:
    left2, right2 = [],[]
    for k in keys:
      if k <= split:
        left2.append(k)
      else:
        right2.append(k)
    if len(left2) == 0:
      left2 = right2.pop(0)
    elif len(right2) == 0:
      right2 = left2.pop()
    left.append((key, left2))
    right.append((key, right2))
  else:
    right.append((key, key_max))
l.append(left)
r.append(right)

print(sorted(left))
print(sorted(right))