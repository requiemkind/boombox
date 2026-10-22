# ============================================
# BOOMBOX PROJECT
# Music player made for learning purposes.
# Still in creating phase, this is the "test" branch after all. It will be modulized and passed into the "main" branch when the time comes.
# Currently, play songs (Enter), switch the displayed song with "<" + Enter and vice versa. And can pause (if the music is playing) by simply pressing Enter.
# ============================================

# bibliotecas
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

i= 0
def title_rolling(title): # 'Mobius strip' ahh

    global i
    title_rolling = ("     " + title + "     " + title)[i : i+14]
    i = (i + 1) % (len(title) + 5)
    return f"{center_alignment(title_rolling)}"


def boombox_active(time_str, rolling_text):
     
    active_design = f"""
{menu_spacing()}
{center_alignment("Now playing:")}
{rolling_text}
{center_alignment(time_str)}

{center_alignment("[ < ] ❚❚ [ > ]")}
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
parar = False

playback = Playback()
playback.set_volume(0.1) # 10% = optimal, just trust me but feel free to change


def input_thread():
    global parar, pause, isplaying, csi, current_song_key, currently_displayed, song_enumeration, i
    
    while not parar:
        try:
            comando = input().strip().lower()
        except EOFError:
            parar = True
            break

        if comando == "s":
            parar = True
            break
            
        if not isplaying:
            if comando == ">":
                csi = (csi + 1) % total_songs
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."
            elif comando == "<":
                csi = (csi - 1) % total_songs
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."
            elif comando == "":
                song_path = files / current_song_key
                playback.load_file(str(song_path))
                playback.play()
                playback.set_volume(0.1)
                i = 0
                isplaying = True
                time.sleep(0.2) # do NOT remove
        else:
            if comando == ">":
                playback.stop()
                csi = (csi + 1) % total_songs
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."
                song_path = files / current_song_key
                playback.load_file(str(song_path))
                playback.play()
                playback.set_volume(0.1)
                i = 0
                pause = False
            elif comando == "<":
                playback.stop()
                csi = (csi - 1) % total_songs
                current_song_key = listed_songs_keys[csi]
                currently_displayed = song_list[current_song_key]
                song_enumeration = f"{csi+1}."
                song_path = files / current_song_key
                playback.load_file(str(song_path))
                playback.play()
                playback.set_volume(0.1)
                i = 0
                pause = False
            elif comando == "":
                if pause:
                    playback.resume()
                    pause = False
                else:
                    playback.pause()
                    pause = True

threading.Thread(target=input_thread, daemon=True).start()

try:
    while not parar:
        print("\033[H\033[J", end='')

        if not isplaying:
            song_path = files / current_song_key
            playback.load_file(str(song_path))
            dur = playback.duration
            menu_dur_time = f"{int(dur // 60)}m {int(dur % 60)}s" 
            
            print(boombox_menu(menu_dur_time), end='') 
        else:
            atual = playback.curr_pos
            total = playback.duration
            time_str = f"{atual:.0f}s / {total:.0f}s"
            
            if not pause:
                # now title rolling keeps goings no matter what!
                roll_txt = title_rolling(currently_displayed)
            else:
                roll_txt = title_rolling(currently_displayed)
                
            print(boombox_active(time_str, roll_txt), end='')
            print(center_alignment("") + "\033[s", end="", flush=True)
            
            time.sleep(0.5)

except KeyboardInterrupt:
    parar = True


playback.stop()
print("\n\nAudio Encerrado\n")
