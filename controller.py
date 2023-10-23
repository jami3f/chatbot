import requests

base_url = "http://localhost:8011/A2F/Player"
a2f_player = "/World/audio2face/Player"

response = requests.post("http://localhost:5000/chatbot", json={"prompt": "hi"})

file_name = response.text

print(f"File name: {file_name}")

set_track_response = requests.post(
    f"{base_url}/SetTrack",
    json={"a2f_player": a2f_player, "file_name": file_name},
)
print("API Response: " + set_track_response.json()["message"])

if not set_track_response.ok:
    print(set_track_response.text)
    exit()

play_response = requests.post(
    f"{base_url}/Play",
    json={"a2f_player": a2f_player},
)

print("API Response: " + play_response.json()["message"])
