import wiringpi
import subprocess
PIN_TO_SENSE = 6        #numer pinu zgodnie z moją rozpiską

def gpioCallback():
    print ("GPIO CALLBACK - called by buttonclick!")
    subprocess.call('sudo python3 /home/odroid/MainOdroid.py >> /home/odroid/testConnectionv1.txt', shell=True)

wiringpi.wiringPiSetup()
wiringpi.pinMode(PIN_TO_SENSE, 0)
wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.PUD_UP) #podciaganie rezystorem do 3.3V

#wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_FALLING, gpioCallback) #wersja na przerwaniu

while True:
    if wiringpi.digitalRead(PIN_TO_SENSE) == 0:
        gpioCallback()
        break
    wiringpi.delay(100) #ms
