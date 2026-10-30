from just_playback import Playback
from pathlib import Path
import shutil
import time
import threading
import queue
import msvcrt
import json
import os
# import rich # W.I.P.

def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - len(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt


def menu_spacing():
    return f"\n"


def get_songname(display_name):
    file_name = None
    
    for key, value in custom_titles.items():
        if value == display_name:
            file_name = key
            break
    if file_name is None:
        file_name = f"{display_name}.mp3"

    return file_name


def load_duration():
    global menu_duration_str, last_loaded_song

    display_name = listed_songs_keys[song_index]
    file_name = get_songname(display_name)

    if last_loaded_song != file_name:
        song_path = files / file_name
        playback.load_file(str(song_path))
        last_loaded_song = file_name

        try:
            dur = playback.duration
            menu_duration_str = format_time(dur)
        
        except:
            menu_duration_str = "0m 0s"


def check_autoplay():
    global next_song_requested, song_finished

    current_time = max(0, playback.curr_pos)
    total_time = playback.duration

    if autoplay and current_time >= total_time -1 and not song_finished:
        next_song_requested = True
        song_finished = True


def update_player_metrics():
    global time_str, progress, roll_txt, volume

    # music duration
    current_time = max(0, playback.curr_pos)
    total_time = playback.duration
    time_str = format_time(current_time, total_time)

    progress = progress_bar(current_time, total_time, width=30)
    roll_txt = title_rolling(currently_displayed)
    volume = volume_bar(current_volume, width=20)


files = Path(__file__).parent / 'songs'
def render_interface():
    global next_song_requested

    if not isplaying:
        load_duration()

        print(boombox_menu(menu_duration_str), end='')
        print(center_alignment("") + "\033[s", end='', flush=True)

    else:
        update_player_metrics()
        check_autoplay()

        print(boombox_active(time_str, roll_txt, pause, volume, progress), end='')
        print("\033[2A\033[G" + center_alignment("") + "\033[s", end='', flush=True)


def adjust_volume(direction, step):
    global current_volume

    current_volume = max(0.0, min(1.0, current_volume + (direction * step)))
    play_queue.put(("VOLUME", current_volume))


def load_songs():
    global listed_songs_keys, custom_titles, total_songs

    json_file = Path(__file__).parent / 'songs.json'

    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            custom_titles = json.load(file)
    else:
        custom_titles = {}

    song_files = sorted(files.glob('*.mp3'))


    listed_songs_keys = []
    for file in song_files:
        display_name = custom_titles.get(file.name, file.stem)
        listed_songs_keys.append(display_name)


def skip_song(direction):
    global song_index, currently_displayed, song_enumeration

    song_index = (song_index + direction) % total_songs
    currently_displayed = listed_songs_keys[song_index]
    song_enumeration = f"{song_index+1}."

    if isplaying:
        play_current_song()


def boombox_menu(menu_duration):


    design = f"""
{menu_spacing()}\033[K
{center_alignment(f"Select your track (total: {total_songs}):")}\033[K
{center_alignment(f"{song_enumeration} {currently_displayed.strip()}")}\033[K
{center_alignment(menu_duration)}\033[K

{center_alignment("[ < ] [Enter] [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
"""

    return design


def format_time(seconds, total_seconds=None):

    # boombox_menu() (full length of the song)
    if total_seconds is None:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    # boombox_active() (dynamic display)
    else:
        return f"{int(seconds)}s / {int(total_seconds)}s"


scroll_pos = 5
def title_rolling(title): # 'Mobius strip' ahh

    global scroll_pos
    title_rolling = ("     " + title + "     " + title)[scroll_pos : scroll_pos+14]
    scroll_pos = (scroll_pos + 1) % (len(title) + 5)
    return f"{center_alignment(title_rolling)}"


current_volume = 0.1 # 10% = optimal, but feel free to change the default volume
def play_current_song(): # if you wanna change default song volume change 'playback.set_volume()' here
    global scroll_pos

    scroll_pos = 5
    display_name = listed_songs_keys[song_index]
    file_name = get_songname(display_name)
    play_queue.put(("PLAY", file_name))


def boombox_active(time_str, rolling_text, ispaused, volume, progress):

    if ispaused:
        play_icon = " ► "
    else:
        play_icon = "❚❚ "

    if autoplay == False:
        autoplaystate = "OFF"
    else:
        autoplaystate = "ON"
     
    active_design = f"""
{menu_spacing()}\033[K
{center_alignment("Now playing:")}\033[K
{rolling_text}\033[K

{center_alignment(progress)}\033[K
{center_alignment(time_str)}\033[K

{center_alignment(f"[ < ]  {play_icon} [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
{(center_alignment(center_alignment(center_alignment(f"Autoplay: {autoplaystate}"))))}\033[K
{center_alignment(volume)}%\033[K
"""

    return active_design


def volume_bar(vol, width=20):

    total_subblocks = int(vol * width * 8)
    full_blocks = total_subblocks // 8
    partial_blocks = total_subblocks % 8

    sub_chars = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]
    bar = "█" * full_blocks

    if partial_blocks > 0 and full_blocks < width:
        bar += sub_chars[partial_blocks]

    empty_blocks = width - len(bar)
    bar += "░" * empty_blocks

    return f"[{bar}] {int(vol * 100)}"


def progress_bar(current, total, width=20):
    
    if total == 0:
        return f"[{'─' * width}]"

    pos = int((current / total) * (width - 1))
    song_length = "━" * pos + "●" + "─" * (width - 1 - pos)

    return f"[{song_length}]"


def change_autoplay(state):
    global autoplay
    autoplay = state


load_songs()
total_songs = len(listed_songs_keys)
song_index = 0
currently_displayed = listed_songs_keys[song_index]
song_enumeration = f"{song_index+1}."

isplaying = False
pause = False
boombox_shutdown = False
last_loaded_song = None
autoplay = False # Feel free to enable this to True
song_finished = False
next_song_requested = False # do NOT change this one though, will figure something better in the future if possible

playback = Playback()
play_queue = queue.Queue()

def audio_thread():
    global boombox_shutdown, scroll_pos, current_volume, last_loaded_song, pause

    while not boombox_shutdown:
        try:
            order, value = play_queue.get(timeout=0.5)

            match order:
                case "PLAY":
                    song_path = files / value
                    playback.load_file(str(song_path))
                    playback.play()
                    playback.set_volume(current_volume)
                    pause = False
                    scroll_pos = 5
                    last_loaded_song = value

                case "PAUSE":
                    playback.pause()
                    pause = True

                case "RESUME":
                    playback.resume()
                    pause = False

                case "VOLUME":
                    current_volume = value
                    playback.set_volume(current_volume)

                case "STOP":
                    playback.stop()

        except queue.Empty:
            pass


# still under review for better coding if possible
def input_thread():
    global boombox_shutdown, pause, isplaying, song_index, currently_displayed, song_enumeration, autoplay, next_song_requested
    
    while not boombox_shutdown:

        if msvcrt.kbhit():
            keyboard = msvcrt.getch().decode('utf-8', errors='ignore').lower()

            if keyboard == "\r":
                user_input = ""
            else:
                user_input = keyboard
        
        else:
            user_input = None

        time.sleep(0.05)

        if next_song_requested:
            next_song_requested = False
            time.sleep(1.5) # changes the interval duration before the next song in autoplay
            skip_song(1)
            continue

        if user_input == "s":
            boombox_shutdown = True
            play_queue.put(("STOP", None))
            break

        if user_input is None:
            continue
            
        if user_input in [">", "<"]:
            if user_input == ">":
                skip_song(1)
            else:
                skip_song(-1)
            
        elif isplaying:
            if user_input in ["+", "-", "[", "]"]:
                if user_input == "+":
                    adjust_volume(1, 0.1)
                elif user_input == "-":
                    adjust_volume(-1, 0.1)
                elif user_input == "[":
                    adjust_volume(1, 0.01)
                elif user_input == "]":
                    adjust_volume(-1, 0.01)

            elif user_input in ["y", "n"]:
                change_autoplay(user_input == "y")
                    
            elif user_input == "":
                if pause:
                    play_queue.put(("RESUME", None))
                else:
                    play_queue.put(("PAUSE", None))

        elif user_input == "":
            isplaying = True
            play_current_song()
            time.sleep(0.2)


threading.Thread(target=input_thread, daemon=True).start()
threading.Thread(target=audio_thread, daemon=True).start()

def main_loop():
    global boombox_shutdown

    try:
        while not boombox_shutdown:
            print("\033[H\033[J", end='')
            render_interface()
            print("\033[u", end='', flush=True)

            if not isplaying:
                time.sleep(0.1)

            else:       
                time.sleep(0.5)

    except KeyboardInterrupt:
        boombox_shutdown = True


main_loop()

playback.stop()
print("\n")
print("\n\nThanks for using Boombox Project. Hope you enjoyed it.\n") # :)
