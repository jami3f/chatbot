from time import time
from TTS.api import TTS

model_file = open("models.txt", "r")
english_models = list(filter(lambda f: "/en/" in f, model_file.read().splitlines()))

times = {}

for model in english_models:
    try:
        start = time()
        tts = TTS(model)
        text = "Hi, this is your Computacenter chatbot speaking, how may I help?"
        speaker = tts.speakers[0] if tts.is_multi_speaker else None
        tts.tts_to_file(text=text, file_path=f"tts-output/{tts.model_name.replace('/', '_')}.wav")
        end = time()
        times[tts.model_name] = end - start
        print("TTS model: " + tts.model_name + " generated in " + str(end - start) + " seconds")
    except:
        continue
print(times)
