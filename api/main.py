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
    def get_matrix(self):
        pass

    def __init__(self) -> None:
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
        )
        self.new_data = 0
        self.create_matrix()

    def create_matrix(self) -> None:
        matrix: list = []
        for x in range(MX):
            for y in range(MY):
                self.client.set(str(x) + "-" + str(y), "#ABABAB")
        for x in range(MX):
            matrix.append([])
            for y in range(MY):
                matrix[x].append(self.client.get(str(x) + "-" + str(y)).decode("ascii"))

    def get_data(self) -> list:
        flat_matrix: list = []
        matrix: list = []
        for x in range(MX):
            for y in range(MY):
                flat_matrix.append(str(x) + "-" + str(y))
        redis_data = self.client.mget(flat_matrix)
        for x in range(MX):
            matrix.append([])
            for y in range(MY):
                matrix[x].append(redis_data[x * MX + y].decode("ascii"))

        return matrix

    @staticmethod
    def validate_pixel(data):
        if data["cord"][1] < 0 or data["cord"][0] < 0:
            return False

        if data["cord"][0] < MX and data["cord"][1] < MY:
            if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", data["color"]):
                return True

    def write_pixel(self, data):
        if self.validate_pixel(data):
            self.client.set(
                str(data["cord"][0]) + "-" + str(data["cord"][1]), data["color"]
            )
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
    storage.new_data = 1
    status = storage.write_pixel(request.json)
    return jsonify({"status": status})


@sock.route("/sock")
def echo(sock):
    while True:
        if storage.new_data == 1:
            matrix = storage.get_data()
            sock.send(json.dumps(matrix))
            storage.new_data = 0


if __name__ == "__main__":
    app.run(host="0.0.0.0")
