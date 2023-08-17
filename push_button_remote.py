from machine import Pin
import time

btn = Pin(15, Pin.IN, Pin.PULL_DOWN)

# kabel
# biru negatif
# coklat positif
# kuning positif / data
# coklat ke power
# biru ke gnd (kalau tidak, lampu di push button yang tidak menyala, tapi event tekan sampai)
# kuning pin 15

while True:
    print(btn.value())
    time.sleep(0.5)