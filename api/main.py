import json
import os
import re
import redis
from flask import Flask, request, jsonify
from flask_sock import Sock
from flask_cors import CORS

app = Flask(__name__)
sock = Sock(app)
CORS(app)


MX = int(os.getenv("MAX_X", 100))
MY = int(os.getenv("MAX_Y", 70))


class Storage:
    def __init__(self) -> None:
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
        )
        self.client.set("new", 0)
        self.flat_matrix = []
        self.create_matrix()

    def _set_click(self, value: int):
        self.client.set("new", value)

    def _get_click_status(self):
        return int(self.client.get("new").decode())

    def create_matrix(self) -> None:
        # matrix: list = []
        for x in range(MX):
            for y in range(MY):
                self.flat_matrix.append(f"{x}-{y}")
                self.client.set(f"{x}-{y}", "#ABABAB")
        # for x in range(MX):
        #     matrix.append([])
        #     for y in range(MY):
        #         matrix[x].append(self.client.get(f"{x}-{y}").decode("ascii"))

    def get_data(self) -> list:
        matrix: list = []
        redis_data = self.client.mget(self.flat_matrix)
        for x in range(MX):
            matrix.append([])
            for y in range(MY):
                matrix[x].append(redis_data[x * MX + y].decode("ascii"))

        return matrix

    @staticmethod
    def validate_pixel(data):
        if data["x"] < 0 or data["y"] < 0:
            return False

        if data["x"] < MX and data["y"] < MY:
            if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", data["color"]):
                return True

    def write_pixel(self, data):
        if self.validate_pixel(data):
            self.client.set(f"{data['x']}-{data['y']}", data["color"])
            return "ok"
        else:
            return "validate error"


storage = Storage()


@app.route("/matrix", methods=["GET"])
def matrix_get():
    matrix = storage.get_data()
    return jsonify(matrix)


@app.route("/pixel", methods=["POST"])
def matrix_edit():
    storage._set_click(1)
    status = storage.write_pixel(request.json)
    return jsonify({"status": status})


@sock.route("/sock")
def echo(sock):
    while True:
        if storage._get_click_status():
            matrix = storage.get_data()
            sock.send(json.dumps(matrix))
            storage._set_click(0)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
