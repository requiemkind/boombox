from just_playback import Playback
from pathlib import Path
import shutil
import time
import threading
import queue
import msvcrt
import json
import os
from rich.live import Live
from rich.console import Console
from rich.markup import escape

def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - len(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt


def get_songname(display_name):
    file_name = None
    
    for key, value in custom_titles.items():
        if value == display_name:
            file_name = key
            break
    if file_name is None:
        file_name = f"{display_name}.mp3"

    return file_name


def check_autoplay():
    global song_finished

    current_time = max(0, playback.curr_pos)
    total_time = playback.duration

    if autoplay and current_time >= total_time -1 and not song_finished:
        play_queue.put(("AUTOPLAY", None))
        song_finished = True


def update_player_metrics():
    global time_str, roll_txt, volume, playing_displayed

    # music duration
    current_time = max(0, playback.curr_pos)
    total_time = playback.duration
    time_str = format_time(current_time, total_time)

    roll_txt = title_rolling(playing_displayed)
    volume = volume_bar(current_volume, width=20)


files = Path(__file__).parent / 'songs'
def render_interface():

    if not isplaying:
        return boombox_menu(menu_duration_str)

    update_player_metrics()
    check_autoplay()

    bar_str = progress_bar(playback.curr_pos, playback.duration)

    return boombox_active(time_str, roll_txt, pause, volume, bar_str)


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


def load_menu_song():
    global menu_duration_str

    menu_duration_str = "..."
    file_name = get_songname(listed_songs_keys[selected_index])
    play_queue.put(("LOAD_MENU", file_name))


def skip_song(direction):
    global selected_index

    selected_index = (selected_index + direction) % total_songs

    if isplaying:
        play_current_song()


def boombox_menu(menu_duration):
    song_name = listed_songs_keys[selected_index]
    order = f"{selected_index + 1}."


    design = f"""

{center_alignment(f"Select your track (total: {total_songs}):")}
{center_alignment(f"{order} {song_name.strip()}")}
{center_alignment(menu_duration)}

{center_alignment("[ < ] [Enter] [ > ]")}
{center_alignment("[s] to stop")}
"""

    return escape(design)


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
def play_current_song():
    global scroll_pos, playing_displayed, pause

    scroll_pos = 5
    display_name = listed_songs_keys[selected_index]
    file_name = get_songname(display_name)

    playing_displayed = display_name
    pause = False

    play_queue.put(("PLAY", (file_name, selected_index)))


def boombox_active(time_str, rolling_text, ispaused, volume, bar_str):

    if ispaused:
        play_icon = " ► "
    else:
        play_icon = "❚❚ "

    if autoplay == False:
        autoplaystate = "OFF"
    else:
        autoplaystate = "ON"
     
    active_design = f"""

{center_alignment("Now playing:")}
{rolling_text}

{center_alignment(bar_str)}
{center_alignment(time_str)}

{center_alignment(f"[ < ]  {play_icon} [ > ]")}
{center_alignment("[s] to stop")}
{(center_alignment(center_alignment(center_alignment(f"Autoplay: {autoplaystate}"))))}
{center_alignment(volume)}%
"""

    return escape(active_design)


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


def progress_bar(current, total, width=30):

    if total <= 0:
        return f"[{'─' * width}]"

    progress = max(0, min(current / total, 1))
    pos = round(progress * (width - 1))

    bar = ("━" * pos + "●"+ "─" * (width - pos - 1))

    return f"[{bar}]"


def update_live(live, design, active, cursor):

    if cursor:
        live.console.file.write("\033[u")

    live.update(design, refresh=True)

    vertical = "\033[2A" if active else ""
    horizontal = f"\033[{len(center_alignment('')) + 1}G"

    live.console.file.write(f"\033[s{vertical}{horizontal}")
    live.console.file.flush()

    return True


def change_autoplay(state):
    global autoplay
    autoplay = state


def process_input(user_input):
    global isplaying

    if user_input in [">", ".", "<", ","]:
        if user_input in [">", "."]:
            skip_song(1)
        else:
            skip_song(-1)

        if not isplaying:
            load_menu_song()
                
    elif isplaying:
        if user_input in ["+", "=", "-", "[", "]"]:
            if user_input in ["+", "="]:
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
            play_queue.put(("TOGGLE_PAUSE", None))
    
    elif user_input == "":
        isplaying = True
        play_current_song()
        time.sleep(0.2)


load_songs()
total_songs = len(listed_songs_keys)

if total_songs == 0:
    print("Empty Boombox! ('songs' folder is empty)")
    os._exit(0)

selected_index = 0
playing_displayed = ""
menu_duration_str = "0m 0s"

isplaying = False
pause = False
boombox_shutdown = False
autoplay = False
song_finished = False

playback = Playback()
play_queue = queue.Queue()

def audio_thread():
    global pause, song_finished, selected_index, menu_duration_str

    while True:
        try:
            order, value = play_queue.get(timeout=0.5)

            match order:
                case "PLAY":
                    file_name, _ = value
                    song_path = files / file_name
                    playback.load_file(str(song_path))
                    playback.play()
                    playback.set_volume(current_volume)
                    pause = False

                case "TOGGLE_PAUSE":
                    if pause:
                        playback.resume()
                        pause = False
                    else:
                        playback.pause()
                        pause = True

                case "VOLUME":
                    playback.set_volume(value)

                case "AUTOPLAY":
                    time.sleep(1.5) # autoplay interval
                    global selected_index
                    selected_index = (selected_index + 1) % total_songs
                    song_finished = False
                    play_current_song()

                case "LOAD_MENU":
                    global menu_duration_str
                    song_path = files / value
                    playback.load_file(str(song_path))
                      
                    try:
                        dur = playback.duration
                        menu_duration_str = format_time(dur)
                    
                    except Exception:
                        menu_duration_str = "0m 0s"

                case "STOP":
                    playback.stop()
                    break

        except queue.Empty:
            pass


def input_thread():
    global boombox_shutdown
    
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

        if user_input == "s":
            boombox_shutdown = True
            break

        if user_input is None:
            continue

        process_input(user_input)


t_input = threading.Thread(target=input_thread, daemon=True)
t_audio = threading.Thread(target=audio_thread, daemon=True)
t_input.start()
t_audio.start()

load_menu_song()

def main_loop():
    global boombox_shutdown

    cursor_saved = False

    try:
        with Live(console=Console(highlight=False), refresh_per_second=10, auto_refresh=False) as live:
            live.console.show_cursor(True)

            while not boombox_shutdown:
                
                design = render_interface()

                cursor_saved = update_live(live, design, isplaying, cursor_saved)

                time.sleep(0.1 if not isplaying else 0.5)

            if cursor_saved:
                live.console.file.write("\033[u")
                live.console.file.flush()

    except KeyboardInterrupt:
        boombox_shutdown = True


os.system("cls")
main_loop()

play_queue.put(("STOP", None))

t_input.join()
t_audio.join()

print("\nThanks for using Boombox Project. Hope you enjoyed it.\n") # :)
