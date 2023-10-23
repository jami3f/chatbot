from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
from TTS.api import TTS
from playsound import playsound
import os
import re
import threading
import inflect
from pydub import AudioSegment
from flask import Flask, request

app = Flask(__name__)


def setup():
    global tts
    global pipeline
    global tokenizer
    tts = TTS("tts_models/en/jenny/jenny")
    model_name = "tiiuae/falcon-7b-instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name, device_map="auto", pad_token_id=0, load_in_8bit=True
    )

    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        pad_token_id=0,
        trust_remote_code=True,
        device_map="auto",
    )


def generate_response(prompt):
    prefix = "You are a helpful chatbot designed to answer any questions you are given as accurately as possible, using facts when possible. Answer the following question: "

    # run the model to generate a response
    sequences = pipeline(
        text_inputs=prefix + prompt,
        max_length=200,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )

    # retrieve the generated response
    response: str = sequences[0]["generated_text"].split("\n")[1].strip()

    # remove commas between numbers and convert them to words using the inflect library
    response = re.sub(r"(?<=\d),(?=\d)", "", response)
    response = re.sub(r"\d+", lambda x: inflect.engine().number_to_words(x.group()), response)

    response = "A fact about nature is that the Northern Lights, also known as auroral displays, are created when solar winds from outer space enter the earth's magnetic field and collide with the nitrogen and oxygen atoms in the atmosphere, causing them to release energy in the form of light. These mesmerising displays can be seen in the night sky and places with clear skies, usuallly during the winter months."


def generate_audio(text):
    # split response on punctuation
    text_split = re.split(r"!|\.|,|:|;|\?", text)

    # find the next file number to use (e.g. output0036.wav)
    current_files = os.listdir("chatbot-output")
    num = max([int(file.split(".")[0].replace("output", "")) for file in current_files]) + 1
    files_to_play = []

    tts.tts_to_file("hi", file_path="./test-output.wav")

    # define function to be used by threads later
    def create_tts_audio(section, file_path):
        tts.tts_to_file(text=section, file_path=file_path)

    threads = []

    for section in text_split:
        # filter out empty sections
        if section.strip() == "":
            continue

        # create a thread for each section so they can all be processed in parallel
        file_path = f"chatbot-output/output{num:0>4}.wav"
        files_to_play.append(file_path)
        num += 1
        thread = threading.Thread(target=create_tts_audio, args=(section, file_path), daemon=True)
        threads.append(thread)
        thread.start()

    # wait for all threads to finish
    for t in threads:
        t.join()

    segments = []
    for f in files_to_play:
        segments.append(AudioSegment.from_file(f, format="wav"))

    combined = AudioSegment.empty()
    for segment in segments:
        combined += segment
    combined.export(f"chatbot-output/output{num}.wav", format="wav")
    return f"chatbot-output/output{num}.wav"


setup()


@app.route("/chatbot", methods=["POST"])
def chatbot():
    prompt = request.json["prompt"]
    response = generate_response(prompt)
    audio_file = generate_audio(response)
    print(audio_file)
    return audio_file
