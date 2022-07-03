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
        "http://localhost:5000/pixel",
        json={"cord": [point.x, point.y], "color": point.color},
    )
    return r


def test_incorrect_HEX():
    data = make_request(Point(1, 1, "#AAAAAA"))
    assert json.load(data.text)["status"] == "ok"


test_incorrect_HEX()
