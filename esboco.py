from just_playback import Playback # the protagonist
from pathlib import Path
import shutil
import time
import threading # first time using this
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

scroll_pos = 0
def title_rolling(title): # 'Mobius strip' ahh

    global scroll_pos
    title_rolling = ("     " + title + "     " + title)[scroll_pos : scroll_pos+14]
    scroll_pos = (scroll_pos + 1) % (len(title) + 5)
    return f"{center_alignment(title_rolling)}"


def play_current_song(): # if you wanna change default song volume change 'playback.set_volume()' here
    
    global pause, scroll_pos
    song_path = files / current_song_key
    playback.load_file(str(song_path))
    playback.play()
    playback.set_volume(0.1) # 10% = optimal, just trust me but feel free to change
    scroll_pos = 0 # or else you might start the switched song somewhere thats not the beginning of the song
    pause = False


def boombox_active(time_str, rolling_text, ispaused):

    if ispaused:
        play_icon = "►"
    else:
        play_icon = "❚❚"
     
    active_design = f"""
{menu_spacing()}
{center_alignment("Now playing:")}
{rolling_text}
{center_alignment(time_str)}

{center_alignment(f"[ < ] {play_icon} [ > ]")}
{center_alignment("[s] to stop")}
"""

    return active_design


# alright here we go (dont mind me im organizing for the final update)

# localize songs folder and all the current downloaded songs (on folder at least)
files = Path(__file__).parent / 'songs'
song_list = {
    "vampira.mp3": "Willyrodriguezwastaken - Vampira",
    "lupinlovinit.mp3": "Tommy Snyder - Lovin' You",
    "luvsic2acoustica.mp3": "Nujabes - Luv(sic) Part 2 feat.Shing02 Acoustica",
    "onceinalullaby.mp3": "Chris Christodolou - Once in a Lullaby",
    "pentatonixattention.mp3": "Charlie Puth - Attention (Pentatonix Cover)",
    "escalofrios.mp3": "Cataratas en Siberia - Escalofríos",
    "luvsic5.mp3": "Nujabes - Luv(sic) Part 5 feat.Shing02",
    "waitingforyou.mp3": "Akira Yamaoka - Waiting for you",
    "lastdinosaur.mp3": "the pillows - LAST DINOSAUR"
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

playback = Playback()

# still under review for better coding if possible (75% done)
def input_thread():
    global boombox_shutdown, pause, isplaying, csi, current_song_key, currently_displayed, song_enumeration, scroll_pos 
    
    while not boombox_shutdown:
        try:
            user_input = input().strip().lower()
        except EOFError:
            boombox_shutdown = True
            break

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
    global last_loaded_song, boombox_shutdown

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
                    menu_dur_str = f"{int(dur // 60)}m {int(dur % 60)}s" 
                except:
                    menu_dur_str = "0m 0s"
                
                print(boombox_menu(menu_dur_str), end='')
                print(center_alignment("") + "\033[s", end="", flush=True)
                time.sleep(0.1)
            else:
                atual = playback.curr_pos
                total = playback.duration
                time_str = f"{atual:.0f}s / {total:.0f}s"
                
                if not pause:
                    # now title rolling keeps goings no matter what!
                    roll_txt = title_rolling(currently_displayed)
                else:
                    roll_txt = title_rolling(currently_displayed)
                    
                print(boombox_active(time_str, roll_txt, pause), end='')
                print(center_alignment("") + "\033[s", end="", flush=True)
                
                time.sleep(0.5)

    except KeyboardInterrupt:
        boombox_shutdown = True

main_loop()

playback.stop()
print("\n\nThanks for using Boombox Project. Hope you enjoyed it.\n") # :)

