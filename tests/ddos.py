import requests
import random
from dataclasses import dataclass
import json


@dataclass
class Point:
    x: int
    y: int
    color: str


def make_request(point):
    r = requests.post(
        "http://192.168.0.157:5000/pixel",
        json={"cord": [point.x, point.y], "color": point.color},
    )
    return r


for x in range(100):
    for y in range(100):
        r = lambda: random.randint(0, 255)
        data = make_request(Point(x, y, "#%02X%02X%02X" % (r(), r(), r())))
        print(data.text, data.status_code, [x, y])

test_incorrect_HEX()
