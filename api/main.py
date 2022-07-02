from ipaddress import ip_address
from flask import Flask, request, jsonify
from flask_sock import Sock
import json
import os

from flask_cors import CORS

app = Flask(__name__)
sock = Sock(app)
CORS(app)

MX = os.getenv("MAX_X", 100)
MY = os.getenv("MAX_Y", 100)


class Storage:
    matrix: list = []

    def __init__(self) -> None:
        self.new_data = 0
        self.create_matrix()

    def create_matrix(self):
        for _ in range(MX):
            self.matrix.append([["#ABABAB"] * MY])

    def get_data(self):
        return self.matrix

    def write_pixel(self, data):
        self.matrix[data["cord"][0]][0][data["cord"][1]] = data["color"]


storage = Storage()


@app.route("/matrix", methods=["GET"])
def matrix_get():
    matrix = storage.get_data()
    return jsonify(matrix)


@app.route("/pixel", methods=["POST"])
def matrix_edit():
    storage.new_data = 1
    status = storage.write_pixel(request.json)
    return jsonify(status)


@sock.route("/sock")
def echo(sock):
    while True:
        if storage.new_data == 1:
            matrix = storage.get_data()
            sock.send(json.dumps(matrix))
            storage.new_data = 0


if __name__ == "__main__":
    app.run("0.0.0.0")
