import time

import network

def connect(username, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(username, password)

    count = 0
    while not wlan.isconnected():
        if count == 30:
            return False
        print("waiting for connection....")
        time.sleep(1)
        count += 1

    print("connected")
    return True
