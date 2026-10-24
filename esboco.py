from just_playback import Playback # the protagonist
from pathlib import Path
import shutil
import time
import threading # first time using this
import msvcrt # for a dynamic autoplay
import rich # W.I.P. not the current main focus

# low tier importance fuctions
def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - len(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt

def menu_spacing():
    return f"\n" * 3

# major importance functions

def boombox_menu(menu_duration):

    # terminal design needs this space, not even joking
    design = f"""
{menu_spacing()}
{center_alignment(f"Select your track (total: {total_songs}):")}
{center_alignment(f"{song_enumeration} {currently_displayed.strip()}")}
{center_alignment(menu_duration)}

{center_alignment("[ < ] [Enter] [ > ]")}
{center_alignment("[s] to stop")}
"""

    return design


def format_time(seconds, total_seconds=None):

    # boombox_menu() (full length of the song)
    if total_seconds is None:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    # boombox_active() (dynamic display)
    else:
        return f"{int(seconds)}s / {int(total_seconds)}s"

scroll_pos = 0
def title_rolling(title): # 'Mobius strip' ahh

    global scroll_pos
    title_rolling = ("     " + title + "     " + title)[scroll_pos : scroll_pos+14]
    scroll_pos = (scroll_pos + 1) % (len(title) + 5)
    return f"{center_alignment(title_rolling)}"


current_volume = 0.1 # 10% = optimal, but feel free to change the default volume
def play_current_song(): # if you wanna change default song volume change 'playback.set_volume()' here
    
    global pause, scroll_pos, current_volume
    song_path = files / current_song_key
    playback.load_file(str(song_path))
    playback.play()
    playback.set_volume(current_volume)
    scroll_pos = 5 # 5 = skips the first 5 setback spaces
    pause = False


def boombox_active(time_str, rolling_text, ispaused, volume):

    if ispaused:
        play_icon = "►"
    else:
        play_icon = "❚❚"

    if autoplay == False:
        autoplaystate = "OFF"
    else:
        autoplaystate = "ON"
     
    active_design = f"""
{menu_spacing()}
{center_alignment("Now playing:")}
{rolling_text}
{center_alignment(time_str)}

{center_alignment(f"[ < ] {play_icon} [ > ]")}
{center_alignment("[s] to stop")}
{(center_alignment(center_alignment(center_alignment(f"Autoplay: {autoplaystate}"))))}
{center_alignment(volume)}%
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



# alright here we go (dont mind me im organizing for the final update)

# localize songs folder and all the current downloaded songs (on folder at least)
files = Path(__file__).parent / 'songs'
# funfact: 'Waiting for you' and 'The 89's Momentum' were friend requests ;)
song_list = {
    "vampira.mp3": "Willyrodriguezwastaken - Vampira",
    "lupinlovinit.mp3": "Tommy Snyder - Lovin' You",
    "luvsic2acoustica.mp3": "Nujabes - Luv(sic) Part 2 feat.Shing02 Acoustica",
    "onceinalullaby.mp3": "Chris Christodolou - Once in a Lullaby",
    "pentatonixattention.mp3": "Charlie Puth - Attention (Pentatonix Cover)",
    "escalofrios.mp3": "Cataratas en Siberia - Escalofríos",
    "luvsic5.mp3": "Nujabes - Luv(sic) Part 5 feat.Shing02",
    "waitingforyou.mp3": "Akira Yamaoka - Waiting for you",
    "lastdinosaur.mp3": "the pillows - LAST DINOSAUR",
    "the89smomentum.mp3": "MYUKKE. - The 89's Momentum"
}


listed_songs_keys = sorted(list(song_list))
total_songs = len(song_list)
csi = 0 # current song/title index
current_song_key = listed_songs_keys[csi]
currently_displayed = song_list[current_song_key]
song_enumeration = f"{csi+1}."

isplaying = False
pause = False
boombox_shutdown = False
last_loaded_song = None
autoplay = False # Feel free to enable this to True
next_song_requested = False # do NOT change this one though, will figure something better in the future if possible

playback = Playback()

# still under review for better coding if possible (75% done)
def input_thread():
    global boombox_shutdown, pause, isplaying, csi, current_song_key, currently_displayed, song_enumeration, scroll_pos, current_volume, autoplay, next_song_requested
    
    while not boombox_shutdown:
        try:
            user_input = input().strip().lower()
        except EOFError:
            boombox_shutdown = True
            break

        if next_song_requested:
            csi = (csi + 1) % total_songs
            current_song_key = listed_songs_keys[csi]
            currently_displayed = song_list[current_song_key]
            song_enumeration = f"{csi+1}."
            play_current_song()
            next_song_requested = False
            continue

        if user_input == "s":
            boombox_shutdown = True
            break
            
        if not isplaying:
            if user_input in [">", "<"]:
                if user_input == ">":
                    csi = (csi + 1) % total_songs
                else:
                    csi = (csi - 1) % total_songs
            
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."

            elif user_input == "":
                isplaying = True
                play_current_song()
                time.sleep(0.2) # do NOT remove
        else:
            if user_input in [">", "<"]:
                if user_input == ">":
                    csi = (csi + 1) % total_songs
                else:
                    csi = (csi - 1) % total_songs
            
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."

                playback.stop()
                play_current_song()

            elif user_input in ["+", "-", "++", "--"]:
                if user_input == "+":
                    current_volume = min(1.0, current_volume + 0.1)
                    playback.set_volume(current_volume)
                elif user_input == "++":
                    current_volume = min(1.0, current_volume + 0.01)
                    playback.set_volume(current_volume)
                elif user_input == "-":
                    current_volume = max(0.0, current_volume - 0.1)
                    playback.set_volume(current_volume)
                elif user_input == "--":
                    current_volume = max(0.0, current_volume - 0.01)
                    playback.set_volume(current_volume)

                playback.set_volume(current_volume)

            elif user_input in ["y", "n"]:
                if user_input == "y":
                    autoplay = True
                elif user_input == "n":
                    autoplay = False
                
            elif user_input == "":
                if pause:
                    playback.resume()
                    pause = False
                else:
                    playback.pause()
                    pause = True

threading.Thread(target=input_thread, daemon=True).start()

# will stay here for now, but later will obviously be put as the final function in the "major importance functions".
def main_loop():
    global last_loaded_song, boombox_shutdown, next_song_requested

    try:
        while not boombox_shutdown:
            print("\033[H\033[J", end='')

            if not isplaying:
                if last_loaded_song != current_song_key:
                    song_path = files / current_song_key
                    playback.load_file(str(song_path))
                    last_loaded_song = current_song_key

                try:
                    dur = playback.duration
                    menu_dur_str = format_time(dur)
                except:
                    menu_dur_str = "0m 0s"
                
                print(boombox_menu(menu_dur_str), end='')
                print(center_alignment("") + "\033[s", end="", flush=True)
                time.sleep(0.1)
            else:
                current_time = max(0, playback.curr_pos)
                total_time = playback.duration
                time_str = format_time(current_time, total_time)

                if autoplay and current_time >= total_time - 1:
                    next_song_requested = True
                
                if not pause:
                    # now title rolling keeps goings no matter what!
                    roll_txt = title_rolling(currently_displayed)
                else:
                    roll_txt = title_rolling(currently_displayed)

                volume = volume_bar(current_volume, width = 20)
                
                print(boombox_active(time_str, roll_txt, pause, volume), end='')
                print("\033[A\033[A" + center_alignment("") + "\033[s", end="", flush=True)
                
                time.sleep(0.5)

    except KeyboardInterrupt:
        boombox_shutdown = True

main_loop()

playback.stop()
print("\n\nThanks for using Boombox Project. Hope you enjoyed it.\n") # :)
