# general imports
import os.path
import time
import speech_recognition as sr
import whisper

# spotipy setup
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# pyttsx3 setup
import pyttsx3

# initialization
source = sr.Microphone()
recognizer = sr.Recognizer()


# IMPORTANT:
# To make this work, create a Spotify app (https://developer.spotify.com/dashboard/create).
# For Redirect URI, enter "http://localhost:1234/", you can choose the rest yourself.
# After the app is created, enter its settings and copy-paste the credentials below.
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    #client_id="[YOUR_CLIENT_ID]",
    #client_secret="[YOUR_CLIENT_SECRET]",
    redirect_uri="http://localhost:1234/",
    scope="user-read-currently-playing,"
          "user-modify-playback-state,"
          "user-read-playback-state"))

base_model_path = os.path.expanduser('~/.cache/whisper/base.pt')
# Available Models:
# 'tiny.en', 'tiny', 'base.en', 'base',
# 'small.en', 'small', 'medium.en', 'medium',
# 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'
base_model = whisper.load_model("medium")


engine = pyttsx3.init()


def spotipy_test():
    current_playing_data = sp.current_playback()
    #print(json.dumps(current_playing_data, indent=4))
    print(current_playing_data['device']['volume_percent'])


def listen_to_command():

    with source as s:
        #prepare to listen
        print("Preparing...")
        recognizer.pause_threshold = 2
        recognizer.adjust_for_ambient_noise(s)

        #fade out spotify
        prev_vol = sp.current_playback()['device']['volume_percent']
        spotipy_fade_volume(prev_vol, 30, 5, 1.5)
        time.sleep(1)

        #listen
        print("Listening...")
        audio = recognizer.listen(s)

        #fade in spotify
        time.sleep(1)
        spotipy_fade_volume(30, prev_vol, 5, 1.5)

    try:
        print("Thinking...")
        with open("command.wav", "wb") as f:
            f.write(audio.get_wav_data())

        command = base_model.transcribe("command.wav")
        if command and command['text']:
            msg = command['text'].replace(". ", ".\n")
            print("\nMESSAGE:\n" + msg.strip())
            return command['text'].lower().strip()
        return None
    except sr.UnknownValueError:
        print("Could not understand audio :/")
        return None
    except sr.RequestError:
        print("Could not request results :/ But why though, this should run offline! >:c")
        return None


def respond(msg):
    engine.say(msg)
    engine.runAndWait()


def spotipy_fade_volume(vol_from, vol_to, steps, fade_time):
    if vol_from < 0 or vol_from > 100 or vol_to < 0 or vol_to > 100 or steps < 0 or steps > 100:
        print("Invalid args!")
        return None

    if vol_from == vol_to:
        print("Nothing to do here :)")
        return None

    vol_per_step = ((vol_to - vol_from) / steps)
    # print("Stepping from", vol_from, "to", vol_to, "in", steps, "steps, thats", vol_per_step, "per step!")

    for i in range(steps):
        vol_current = vol_from + (i*vol_per_step)
        vol_next = int(vol_from + ((i+1)*vol_per_step))
        # print("Step", (i+1), "of", steps, "total!", vol_current, "->", vol_next)
        sp.volume(vol_next)
        if steps > 1:
            time.sleep(fade_time/steps)


if __name__ == '__main__':
    #spotipy_test()
    msg = listen_to_command()
    #respond(msg)
