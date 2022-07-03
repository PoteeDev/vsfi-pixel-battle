from flask import Flask, request, jsonify
from flask_sock import Sock
import json
import os
import re

from flask_cors import CORS
from sqlalchemy import true

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

    @staticmethod
    def validate_pixel(data):
        if data["cord"][1] < 0 or data["cord"][0] < 0:
            return False

        if data["cord"][0] < MX and data["cord"][1] < MY:
            if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", data["color"]):
                return True

    def write_pixel(self, data):
        if self.validate_pixel(data):
            self.matrix[data["cord"][0]][0][data["cord"][1]] = data["color"]
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
    app.run("0.0.0.0")
