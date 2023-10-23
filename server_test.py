from flask import Flask, request
import os

app = Flask(__name__)


@app.route("/chatbot", methods=["POST"])
def generate_audio():
    prompt = request.json["prompt"]
    print(prompt)
    current_files = os.listdir("chatbot-output")
    file = max(current_files, key=lambda x: int(x.split(".")[0].replace("output", "")))
    return file
