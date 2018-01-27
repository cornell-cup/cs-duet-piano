#define  C     1
#define  D     2
#define  E     3
#define  f     4    // Does not seem to like capital F
#define  G     5
#define  R     0
#define rest   11
import time
import wiringpi


C = 1
D = 2
E = 3
f = 4
G = 5
R = 0

melody = [E, E, E, R,
               E, E, E, R,
               E, G, C, D, E, R,
               f, f, f, f, f, E, E, E, E, D , D, E, D, R, G , R,
               E, E, E, R,
               E, E, E, R,
               E, G, C, D, E, R,
               f, f, f, f, f, E, E, E,  G, G, f, D, C, R
              ]
MAX_COUNT = len(melody)

def playTone(pin2play, dur):
    print(pin2play)
    buf = str(pin2play) + "\n"
    stuff = wiringpi.wiringPiSPIDataRW(channel, buf)
    time.sleep(dur)

def loop():
    prev = 0
    for i in range(MAX_COUNT):
        tone = melody[i]
        print(prev, tone)
        if prev == tone:
            playTone(11, 0.02)
            playTone(tone, 0.3)
            prev = tone
        elif tone == 0:
            playTone(prev, 0.3)
        else:
            playTone(tone, 0.3)
            prev = tone
    playTone(0, 0.3)

if __name__ == "__main__":

    wiringpi.wiringPiSetupGpio()
    channel = 1
    speed = 500
    wiringpi.wiringPiSPISetup(channel, speed)

    loop()
