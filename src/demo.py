#define  C     1
#define  D     2
#define  E     3
#define  f     4    // Does not seem to like capital F
#define  G     5
#define  R     0
import serial
import time

connected = False
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
MAX_COUNT = len(melody) / 2

def playTone(pin2play):
    duration = 0.3
    pause = 0.1
    if pin2play == 0:
        while time.time() - now < duration:
            ser.write(pin2play)
    else:
        while time.time() - now < pause:
            ser.write(pin2play)
            #digitalWrite(pin2play, HIGH)
            #digitalWrite(pin2play, LOW)

def loop():
    pin=0
    for i in range(MAX_COUNT):
        tone = melody[i]
        switch (tone):
            case 1: pin = 2
                break
            case 2: pin = 3
                break
            case 3: pin = 4
                break
            case 4: pin = 5
                break
            case 5: pin = 6
                break
            default: pin = 0
                break

        playTone(pin)

if __name__ == "__main__":

    ser = serial.Serial("COM11", 9600)

    while not connected:
        serin = ser.read()
        connected = True
    loop()
    ser.close()
