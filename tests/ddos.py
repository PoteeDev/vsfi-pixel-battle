import requests
import random
from dataclasses import dataclass
import json
from threading import Thread
import time

COUNT_TREADS = 50


def treading_function(data):
    time.sleep(5)
    print("Thread " + str(data) + " started")
    for x in range(100):
        for y in range(100):
            color = lambda: random.randint(0, 255)
            r = requests.post(
                "http://localhost/api/v1/pixel",
                json={
                    "x": x,
                    "y": y,
                    "color": "#%02X%02X%02X" % (color(), color(), color()),
                },
            )
            # print(r.text, r.status_code, [x, y])


threads = []
for i in range(COUNT_TREADS):
    try:
        t = Thread(target=treading_function, args=(i,))
        threads.append(t)
        t.start()
    except:
        print("Error: unable to start thread")
