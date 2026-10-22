# if youre seeing a boombox project with this file, its because im still working on the code rework

# from pathlib import Path

# files = Path(__file__).parent / 'songs'
# song_list = sorted(files.glob('*.mp3'))

import shutil
import time

def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - len(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt

def menu_spacing():
    return f"\n" * 3


# current way to add songs to YOUR boombox
song_list = {
    "musga1": "say wallahi bro",
    "musga2": "wut da HEEEEEL"
}

listed_songs_keys = sorted(list(song_list))
total_songs = len(song_list)
csi = 0 # current song/title index
current_song_key = listed_songs_keys[csi]
currently_displayed = song_list[current_song_key]
song_enumeration = f"{csi+1}."

def boombox_menu():

    # terminal design needs this space, not even joking
    design = f"""
{menu_spacing()}
{center_alignment(f"Select your track (total: {total_songs}):")}
{center_alignment(f"{song_enumeration} {currently_displayed.strip()}")}
{center_alignment("[duration]")}

{center_alignment("[ < ] [Enter] [ > ]")}
{center_alignment("[s] to stop")}
"""

    return design


i = 0 # don't worry this and the title rolling function took my brain way too long to understand too

def title_rolling(title): # Mobius strip logic

    global i
    title_rolling = ("     " + title + "     " + title)[i : i+14]
    i = (i + 1) % (len(title) + 5)
    return f"\r{center_alignment(title_rolling)}\033[K"


def boombox_active():
     
    active_design = f"""
{menu_spacing()}
{center_alignment(f"Now playing:")}\033[K

{center_alignment("[duration]")}\033[K

{center_alignment("[ < ] ❚❚ [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
"""

    return active_design


isplaying = False

while True:

    print("\033[H", end='')
    if not isplaying:
        print(boombox_menu(), end='')
        
        input_fix = center_alignment("")
        print(f"{input_fix}\033[s\033[K", end="", flush=True) # input cursor location + K so it doesn't "leave a mark" (unless program execution end)

        user_input = input().strip().lower()

        if user_input == "s":
            break

        elif user_input in [">", "<"]:
            if user_input == ">":
                csi = (csi + 1) % total_songs
            else:
                csi = (csi - 1) % total_songs

            current_song_key = listed_songs_keys[csi]
            currently_displayed = song_list[current_song_key]
            song_enumeration = f"{csi+1}."

        elif user_input == "":
            isplaying = True
        
        
    else:
        print("\033[H", end='')
        print(boombox_active(), end='')

        print("\033[F" * 4, end='', flush=True)
        print("\033[s", end='', flush=True)

        try:
            while isplaying:
                print("\033[u", end='', flush=True)
                print(title_rolling(currently_displayed), end='', flush=True)
                time.sleep(0.2)

        except KeyboardInterrupt:
            isplaying = False


print("fim")
