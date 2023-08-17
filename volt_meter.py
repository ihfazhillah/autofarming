from machine import ADC
import time

vmeter = ADC(27)

"""Rumus:
V_out = V_in * R2 / R1 + R2

r2 = 2.2
r1 = 10

2.3 = x * 2.2 / 10 + 2.2
2.3 * (10 + 2.2) = x * 2.2
x = 2.3 * (10 + 2.2) / 2.2
"""

while True:
    # 65535 max integer of 16 bit
    # 3.3 is voltage of each pinout
    # 10 (first resistor)
    # 2.2 (second resistor)
    adc_read = vmeter.read_u16() / 65535 * 3.3
    print(round(adc_read * (10 + 2.2) / 2.2, 2))
    time.sleep(1)