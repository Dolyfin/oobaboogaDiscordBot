import asyncio
import json

import dotenv
import os
from os import getenv
import requests

dotenv.load_dotenv()
SPEECH_API_ADDRESS = getenv('SPEECH_GEN_IP') + ":" + getenv('SPEECH_GEN_PORT')

speech_enabled = True
if getenv('SPEECH_GEN_IP') == "" or getenv('SPEECH_GEN_PORT') == "":
    print("<!> 'SPEECH_GEN_IP' or 'SPEECH_GEN_PORT' is missing in .env file.")
    speech_enabled = False
if not os.path.isfile("ffmpeg.exe"):
    print(
        "<!> ffmpeg.exe is not found in the root folder. Please download manually and place .exe in root folder for voice.")
    speech_enabled = False


async def initialize():
    if not speech_enabled:
        print(f"<!> Speech not available.")
        return
    directory_path = "temp/"
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(directory_path, file_name)
            os.remove(file_path)

    if await is_speech_enabled():
        print(f"<?> Speech Ready!")


async def is_speech_enabled():
    response = requests.get(f"http://{SPEECH_API_ADDRESS}/ready")
    if response.status_code == 200:
        return True
    else:
        return False


voice_counter = 0


async def gen_speech(channel_id, text_message, persona_data):
    global voice_counter
    voice_counter += 1

    output_file = f"{channel_id}_{voice_counter}"

    narrator_enabled = False
    if persona_data["narrator"] != "":
        narrator_enabled = True

    text_message = " " + text_message
    text_message = text_message.replace(' *', f" *{persona_data['name']} ").replace('* ', '*. ')

    payload = {
        "text_input": text_message,
        "text_filtering": "standard",
        "character_voice_gen": persona_data["voice"],
        "narrator_enabled": narrator_enabled,
        "narrator_voice_gen": persona_data["narrator"],
        "text_not_inside": "character",
        "language": "en",
        "output_file_name": output_file,
        "output_file_timestamp": False,
        "autoplay": False,
        "autoplay_volume": "0.8",
    }

    response = requests.post(f"http://{SPEECH_API_ADDRESS}/api/tts-generate", data=payload)
    response = response.json()
    print(json.dumps(response))

    return response['output_file_url']

