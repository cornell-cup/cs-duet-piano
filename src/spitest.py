import wiringpi

wiringpi.wiringPiSetupGpio()	
channel = 1
speed = 500000
wiringpi.wiringPiSPISetup(channel, speed)
wiringpi.pinMode(7, 1)
wiringpi.pinMode(8, 1)
wiringpi.pinMode(23, 1)
wiringpi.pinMode(24, 1)
buf = "hello"
retlen, retdata = wiringpi.wiringPiSPIDataRW(0, buf)

print retlen, retdata
