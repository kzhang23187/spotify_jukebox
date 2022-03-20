#!/usr/bin/python
from contextlib import redirect_stderr
from multiprocessing.connection import wait
import time
import webbrowser
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import sys
import os

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal

continue_reading = True

#Capture SIGINT for cleanup when script is aborted
def end_read(signal, frame):
    global continue_reading
    print("\nCtrl+c captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
    
signal.signal(signal.SIGINT, end_read)

    
def create_spotify():
    auth_manager = SpotifyOAuth(
        client_id = os.environ['SPOTIFY_CLIENT_ID'],
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET'],
        redirect_uri = 'http://127.0.0.1:8887',
        scope = 'user-read-playback-state user-library-read playlist-modify-public playlist-modify-private user-modify-playback-state'
    )

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return auth_manager, spotify

def refresh_spotify(auth_manager, spotify):
    token_info = auth_manager.cache_handler.get_cached_token()
    if auth_manager.is_token_expired(token_info):
        auth_manager, spotify = create_spotify()
    return auth_manager, spotify

def play_album(sp, album_uri, device_id):
    sp.start_playback(device_id=device_id, context_uri=album_uri, offset={"position": 0},  position_ms=0)
    try:
        sp.shuffle(False, device_id=device_id)
    except:
        return

def play_song(sp, song_uri):
    sp.add_to_queue(song_uri)
    sp.next_track()

def play_recommendation_by_genres(sp, seed_genres, device_id):
    recommendations = sp.recommendations(seed_genres=seed_genres, limit=50, country='US')
    q = []
    names = []
    for song in recommendations['tracks']:
        q.append(song['uri'])
        names.append(song['name'])
    sp.start_playback(device_id=device_id, uris=q, offset={"position": 0}, position_ms=0)

def play_recommendation_by_artists(sp, seed_artists, device_id):
    recommendations = sp.recommendations(seed_artists=seed_artists, limit=50, offset=50, country='US', max_instrumentalness=0.35)
    q = []
    names = []
    for song in recommendations['tracks']:
        q.append(song['uri'])
        names.append(song['name'])
    sp.start_playback(device_id=device_id, uris=q, offset={"position": 0}, position_ms=0)
    
def like_song(sp, device_id):
    current_song = sp.currently_playing()
    print(current_song)

    #sp.playlist_add_items("spotify:playlist:1l70hdljjU66G05HsU8cmV", 

def get_device(sp, target_device):
    data = sp.devices()
    devices = data['devices']
    for d in devices:
        if target_device.lower() in d['name'].lower():
            return d['id']
    return None

def handle_data(sp, device_id, text):
    if text == "Stop":
        "Stopping jukebox"
        end_read()
    elif text == "like":
        like_song(sp, device_id)
        return

    uri = text.strip()
    tokens = text.split(':')
    uriType = tokens[1]
    try:
        if (uriType == "album"):
            play_album(sp, uri, device_id)
        elif (uriType == "artist"):
            play_recommendation_by_artists(sp, [uri], device_id)
    except:
        print("API failed")
    

def main():
    #reader = MFRC522()
    scopes = 'user-read-playback-state user-library-read playlist-modify-public user-modify-playback-state'
    auth, sp = create_spotify()

    dean_album_uri = "spotify:album:1MW3txTS49ZGvyLi0fziLU"
    circles_album_uri = "spotify:album:5sY6UIQ32GqwMLAfSNEaXb"
    ye_album_uri = "spotify:album:2Ek1q2haOnxVqhvVKqMvJe"
    ciki_album_uri = "spotify:album:04MdUslmkxO6q1SHeqBYx2"
    day6_album_uri = "spotify:album:4B2Ijqpz9hRDqWraaDxLSS"


    #good seeds
    kanye_artist_uri = "spotify:artist:5K4W6rqBFWDnAN6FQUkS6x"
    gray_artist_uri = "spotify:artist:3kPEBSt7qgVoRZSbIXMr7W"
    glenn_gould_artist_uri = "spotify:artist:2aAHdB5HweT3mFcRzm0swc"
    iu_artist_uri = "spotify:artist:3HqSLMAZ3g3d5poNaI7GOU"
    dean_artist_uri = "spotify:artist:3eCd0TZrBPm2n9cDG6yWfF"
    frank_ocean_artist_uri = "spotify:artist:2h93pZq0e7k5yf4dywlkpM"
    mac_miller_artist_uri = "spotify:artist:4LLpKhyESsyAXpc4laK94U"
    
    target_device = "Echo Dot"
    device_id = get_device(sp, target_device)
    print(device_id)
    return
    print("Starting jukebox")
    reader = MFRC522()

    while (continue_reading):
        #Scan for cards
        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)

        # Get the UID of the card
        (status, uid) = reader.MFRC522_Anticoll()

        if status == reader.MI_OK:

            reader.MFRC522_SelectTag(uid)

            #Check authenticated
            if status == reader.MI_OK:
                data = []
                text_read = ''
                #[6,7,8,9,10,11,12]
                for block_num in [6,10,14]:
                    block = reader.MFRC522_Read(block_num) 
                    if block:
                        data += block
                if data:
                    text_read = ''
                    for i in data:
                        if chr(i) == 'þ':
                            break
                        text_read = text_read + chr(i)
                        #text_read = ''.join(chr(i) for i in data)
                     
                text = text_read[1:]
                
                reader.MFRC522_StopCrypto1()

                handle_data(sp, device_id, text)

            else:
                print("Scan error")
        time.sleep(3)

 

if __name__ == '__main__':
    main()

#create systemd service: https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/
    #Add the spotify client id and secret as Environment= in the .service file
    #set WorkingDirectory=/path/to/pythonscript
#Add export SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to /env/profile so that spotify env variables are there after boot




