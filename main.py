from just_playback import Playback
from pathlib import Path
import shutil, time, threading, queue, msvcrt, json, os

files = Path(__file__).parent / 'songs'
playback = Playback()
play_queue = queue.Queue()

isplaying = False
pause = False
boombox_shutdown = False
autoplay = False
song_finished = False

selected_index = 0
current_volume = 0.1 # optimal (10%)
scroll_pos = 5
autoplay_interval = 1.5 # autoplay interval

playing_displayed = ""
menu_duration_str = "0m 0s"

# ASCII
def clean_ascii():
    return [line.rstrip() for line in boombox().strip("\n").splitlines()]


def inject_status(art_lines):

    autoplay_char = "●" if autoplay else "○"
    volume_str = f"{int(current_volume * 100)}%".ljust(3)
    art_lines[9] = art_lines[9].replace("○", autoplay_char)
    art_lines[9] = art_lines[9].replace("10%", volume_str)
    return art_lines


def move_cursor():
    center_col = (shutil.get_terminal_size().columns // 2) + 2
    print(f"\033[10;{center_col}H", end="", flush=True)


selected_option = 0

# utilities functions
def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - len(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt


def ascii_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    lines = txt.splitlines()
    max_width = max(map(len, lines), default=0)
    alignment = max(0, (fullsize_x - max_width) // 2)
    return "\n".join(" " * alignment + line for line in lines)


def vertical_alignment(txt):
    fullsize_y = shutil.get_terminal_size().lines
    lines = txt.splitlines()
    txt_alignment = max(0, (fullsize_y - len(lines)) // 2)
    return "\n" * txt_alignment + txt


def get_songname(index):
    return listed_songs_files[index]


def format_time(seconds, total_seconds=None):
    # boombox_menu()
    if total_seconds is None:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    # boombox_active()
    else:
        return f"{int(seconds)}s / {int(total_seconds)}s"


def progress_bar(current, total, width=20):  
    if total == 0:
        return f"[{'─' * width}]"

    pos = int((current / total) * (width - 1))
    song_length = "━" * pos + "●" + "─" * (width - 1 - pos)

    return f"[{song_length}]"   


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

# interface functions
def choice_menu():
    global selected_option
    print("\033[H\033[J\033[2J", end='')
    
    art_lines = clean_ascii()
    selection_ui = [""] * len(art_lines)

    selection_ui[4] = "  Please select your Boombox UI:  "
    selection_ui[5] = "          ASCII                  "
    selection_ui[6] = "          Legacy Version         "

    if selected_option == 0:
        selection_ui[5] = "      >>  ASCII"
    else:
        selection_ui[6] = "      >>  Legacy Version"

    screen = "\n".join(art_lines[i] + "    " + selection_ui[i] for i in range(len(art_lines)))
    
    print(ascii_alignment(screen), end='')
    time.sleep(0.05)


def get_choice():
    global selected_option
    
    previous_choice = -1
    while True:
        if selected_option != previous_choice:
            choice_menu()
            previous_choice = selected_option
            
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                arrow = msvcrt.getch()
                if arrow == b'P': selected_option = (selected_option + 1) % 2
                elif arrow == b'H': selected_option = (selected_option - 1) % 2
            else:
                char = key.decode('utf-8', errors='ignore').lower()
                if char in ["s", ".", ">"]: selected_option = (selected_option + 1) % 2
                elif char in ["w", ",", "<"]: selected_option = (selected_option - 1) % 2
                elif char == "\r":
                    return "ascii" if selected_option == 0 else "legacy"


def title_rolling(title): # 'Mobius strip' logic
    global scroll_pos
    title_rolling = ("     " + title + "     " + title)[scroll_pos : scroll_pos+14]
    scroll_pos = (scroll_pos + 1) % (len(title) + 5)
    return title_rolling


def boombox_menu(menu_duration):
    song_name = listed_songs_keys[selected_index]
    order = f"{selected_index + 1}."

    design = f"""

{center_alignment(f"Select your track (total: {total_songs}):")}\033[K
{center_alignment(f"{order} {song_name.strip()}")}\033[K
{center_alignment(menu_duration)}\033[K

{center_alignment("[ < ] [Enter] [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
"""

    return design


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

{center_alignment("Now playing:")}\033[K
{center_alignment(rolling_text)}\033[K

{center_alignment(progress)}\033[K
{center_alignment(time_str)}\033[K

{center_alignment(f"[ < ]  {play_icon} [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
{(center_alignment(center_alignment(center_alignment(f"Autoplay: {autoplaystate}"))))}\033[K
{center_alignment(volume)}%\033[K
"""

    return active_design


def render_interface():
    if not isplaying:

        print(boombox_menu(menu_duration_str), end='')
        print(center_alignment("") + "\033[s", end='', flush=True)

    else:
        update_player_metrics()
        check_autoplay()

        print(boombox_active(time_str, roll_txt, pause, volume, progress), end='')
        print("\033[2A\033[G" + center_alignment("") + "\033[s", end='', flush=True)


def ascii_menu(menu_duration):
    global selected_index, autoplay, current_volume

    art_lines = [line.rstrip() for line in boombox().strip("\n").splitlines()]

    song_title = listed_songs_keys[selected_index]
    number = f"{selected_index + 1}."
    if len(song_title) > 14:
        song_title = song_title[:11] + "..."
        
    song_text = f"{number} {song_title}  [{menu_duration}]"
    select_text = f"Select your track ({total_songs}):"

    prefix = "  | | "
    suffix = " | |"
    content_width = len(art_lines[3]) - len(prefix) - len(suffix)

    art_lines[3] = prefix + select_text[:content_width].center(content_width) + suffix
    art_lines[4] = prefix + song_text[:content_width].center(content_width) + suffix

    autoplay_char = "●" if autoplay else "○"
    volume_str = f"{int(current_volume * 100)}%"
    art_lines[9] = art_lines[9].replace("○", autoplay_char)
    art_lines[9] = art_lines[9].replace("10%", volume_str)

    screen = "\n".join(art_lines)
    print("\033[H\033[J\033[3J", end='')
    print(ascii_alignment(screen), end='')

    center_col = (shutil.get_terminal_size().columns // 2) + 2
    print(f"\033[10;{center_col}H", end="", flush=True)


def ascii_active(time_str, rolling_text):
    art_lines = clean_ascii()

    prefix = "  | | "
    suffix = " | |"
    content_width = len(art_lines[3]) - len(prefix) - len(suffix)

    art_lines[3] = prefix + "Now playing:".center(content_width) + suffix
    art_lines[4] = prefix + rolling_text[:content_width].center(content_width) + suffix
    art_lines[5] = prefix + time_str[:content_width].center(content_width) + suffix
    art_lines[6] = "  | |_________________________________________| |"

    art_lines = inject_status(art_lines)
    screen = "\n".join(art_lines)

    print("\033[H\033[J\033[3J", end='')
    print(ascii_alignment(screen), end='')
    move_cursor()


def boombox():
    return r"""    ___________________________________________
   /                                           \
  |  _________________________________________  |
  | |  | | | | | | | | | | | | | | | | | | |  | |
  | |  |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|  | |
  | |_________________________________________| |
  |                                             |
  |  [ - ]      [ < ] [Enter] [ > ]      [ + ]  |
  |                                             |
  |    ○                                  10%   |
  |                                             |
  |                   [POWER]                   |
  |_____________________________________________|
        |                               |
        |_______________________________|"""

# player logic functions
def play_current_song():
    global scroll_pos, playing_displayed, pause, song_finished

    scroll_pos = 5
    display_name = listed_songs_keys[selected_index]
    file_name = get_songname(selected_index)

    playing_displayed = display_name
    pause = False
    song_finished = False

    play_queue.put(("PLAY", (file_name, selected_index)))


def skip_song(direction):
    play_queue.put(("SKIP", direction))


def load_songs():
    global listed_songs_keys, listed_songs_files, custom_titles, total_songs

    json_file = Path(__file__).parent / 'songs.json'

    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            custom_titles = json.load(file)
    else:
        custom_titles = {}

    song_files = sorted(files.glob('*.mp3'))


    listed_songs_keys = []
    listed_songs_files = []

    for file in song_files:
        display_name = custom_titles.get(file.name, file.stem)
        listed_songs_keys.append(display_name)
        listed_songs_files.append(file.name)


def load_menu_song():
    global menu_duration_str

    menu_duration_str = "..."
    file_name = get_songname(selected_index)
    play_queue.put(("LOAD_MENU", file_name))


def adjust_volume(direction, step):
    global current_volume

    current_volume = max(0.0, min(1.0, current_volume + (direction * step)))
    play_queue.put(("VOLUME", current_volume))


def change_autoplay(state):
    global autoplay
    autoplay = state


def process_input(user_input):
    global isplaying

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

    elif user_input in [">", "<", ",", "."]:
        if user_input in [">", "."]:
            skip_song(1)
        else:
            skip_song(-1)

    elif isplaying:
        if user_input == "":
            play_queue.put(("TOGGLE_PAUSE", None))
    
    elif user_input == "":
        isplaying = True
        play_current_song()
        time.sleep(0.2)


def check_autoplay():
    global song_finished

    current_time = max(0, playback.curr_pos)
    total_time = playback.duration

    if autoplay and not pause and current_time >= total_time -1 and not song_finished:
        play_queue.put(("AUTOPLAY", None))
        song_finished = True


def update_player_metrics():
    global time_str, progress, roll_txt, volume

    current_time = max(0, playback.curr_pos)
    total_time = playback.duration
    time_str = format_time(current_time, total_time)

    progress = progress_bar(current_time, total_time, width=30)
    roll_txt = title_rolling(playing_displayed)
    volume = volume_bar(current_volume, width=20)

    return time_str, progress, roll_txt, volume

# threads
def audio_thread():
    global pause, song_finished, selected_index, menu_duration_str
    autoplay_deadline = None

    while True:
        if autoplay_deadline is not None and time.monotonic() >= autoplay_deadline:
            autoplay_deadline = None
            selected_index = (selected_index + 1) % total_songs
            song_finished = False
            play_current_song()

        try:
            timeout = 0.5
            if autoplay_deadline is not None:
                remaining = autoplay_deadline - time.monotonic()
                timeout = min(timeout, max(0, remaining))

            order, value = play_queue.get(timeout=timeout)

            match order:
                case "PLAY":
                    file_name, _ = value
                    song_path = files / file_name
                    playback.load_file(str(song_path))
                    playback.play()
                    playback.set_volume(current_volume)
                    pause = False
                    autoplay_deadline = None

                case "TOGGLE_PAUSE":
                    if pause:
                        playback.resume()
                        pause = False
                    else:
                        playback.pause()
                        pause = True

                case "SKIP":
                    selected_index = (selected_index + value) % total_songs

                    if isplaying:
                        play_current_song()
                    else:
                        load_menu_song()

                case "VOLUME":
                    playback.set_volume(value)

                case "AUTOPLAY":
                    autoplay_deadline = time.monotonic() + autoplay_interval

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
            keyboard = msvcrt.getch()

            if keyboard in [b'\xe0', b'\x00']:
                arrow = msvcrt.getch()
                if arrow == b'M': user_input = ">"
                elif arrow == b'K': user_input = "<"

                else:
                    user_input = None
            else:
                try:
                    user_input = keyboard.decode('utf-8', errors='ignore').lower()

                    if user_input == "\r":
                        user_input = ""
                except:
                    user_input = None
            
        else:
            user_input = None

        time.sleep(0.05)

        if user_input == "s":
            boombox_shutdown = True
            break

        if user_input is None:
            continue

        process_input(user_input)

# main
def legacy_loop():
    global boombox_shutdown

    try:
        while not boombox_shutdown:
            print("\033[H\033[J", end='')
            render_interface()
            print("\033[u", end='', flush=True)

            if not isplaying:
                time.sleep(0.1)

            else:       
                time.sleep(0.5) # title rolling speed

    except KeyboardInterrupt:
        boombox_shutdown = True


def ascii_loop():
    global boombox_shutdown, selected_index, menu_duration_str, isplaying

    try:
        while not boombox_shutdown:
            if not isplaying:
                ascii_menu(menu_duration_str)
            else:
                time_str, _, roll_txt, _ = update_player_metrics()
                check_autoplay()
                ascii_active(time_str, roll_txt)
                
            time.sleep(0.5) # title rolling speed (ascii)

    except KeyboardInterrupt:
        boombox_shutdown = True


def main_loop():
    mode = get_choice()

    t_input = threading.Thread(target=input_thread, daemon=True)
    t_input.start()
    
    if mode == "ascii":
        ascii_loop()
    else:
        legacy_loop()

# program execution part
load_songs()

total_songs = len(listed_songs_keys)
if total_songs == 0:
    print("Empty Boombox! ('songs' folder is empty)")
    os._exit(0)

t_input = threading.Thread(target=input_thread, daemon=True)
t_audio = threading.Thread(target=audio_thread, daemon=True)
t_audio.start()

load_menu_song()
main_loop()

play_queue.put(("STOP", None))
t_audio.join()

print("\033[H\033[J", end='') 
if total_songs > 0:
    print("\nThank you for using Boombox Project. Hope you enjoyed it.") # :)
