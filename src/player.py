import src.config as config
from src.utils import format_time
import queue, time, json, os, msvcrt

play_queue = queue.Queue()

def get_songname(index):
    return config.listed_songs_files[index]


def load_songs():
    json_file = config.base_path / 'songs.json'

    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                loaded_titles = json.load(file)
                config.custom_titles = loaded_titles if isinstance(loaded_titles, dict) else {} # ensures json is a dictionary
        except (json.JSONDecodeError, OSError):
            config.custom_titles = {}
    else:
        config.custom_titles = {}

    song_files = sorted(config.files.glob('*.mp3'))

    config.listed_songs_keys = []
    config.listed_songs_files = []

    for file in song_files:
        display_name = config.custom_titles.get(file.name, file.stem)
        config.listed_songs_keys.append(display_name)
        config.listed_songs_files.append(file.name)

    config.total_songs = len(config.listed_songs_keys)


def load_menu_song():
    config.menu_duration_str = "..."
    file_name = get_songname(config.selected_index)
    play_queue.put(("LOAD_MENU", file_name))


def play_current_song():
    config.scroll_pos = 5
    config.playing_displayed = config.listed_songs_keys[config.selected_index]
    file_name = get_songname(config.selected_index)

    config.pause = False
    config.song_finished = False

    play_queue.put(("PLAY", (file_name, config.selected_index)))


def skip_song(direction):
    play_queue.put(("SKIP", direction))


def adjust_volume(direction, step):
    config.current_volume = max(0.0, min(1.0, config.current_volume + (direction * step)))
    play_queue.put(("VOLUME", config.current_volume))


def process_input(user_input):
    if user_input in ["+", "=", "-", "[", "]", "up", "down"]:
        if user_input in ["+", "=", "up"]:
            adjust_volume(1, 0.1)
        elif user_input in ["-", "down"]:
            adjust_volume(-1, 0.1)
        elif user_input == "]":
            adjust_volume(1, 0.01)
        elif user_input == "[":
            adjust_volume(-1, 0.01)
    
    elif user_input in ["y", "n"]:
        config.autoplay = (user_input == "y")

    elif user_input in [">", "<", ",", "."]:
        if user_input in [">", "."]:
            skip_song(1)
        else:
            skip_song(-1)

    elif config.isplaying:
        if user_input == "":
            play_queue.put(("TOGGLE_PAUSE", None))
    
    elif user_input == "":
        config.isplaying = True
        play_current_song()
        time.sleep(0.2)


def check_autoplay():
    current_time = max(0, config.playback.curr_pos)
    total_time = config.playback.duration

    if config.autoplay and not config.pause and current_time >= total_time -1 and not config.song_finished:
        play_queue.put(("AUTOPLAY", None))
        config.song_finished = True


def audio_thread():
    autoplay_deadline = None
    while True:
        if autoplay_deadline is not None and time.monotonic() >= autoplay_deadline:
            autoplay_deadline = None
            config.selected_index = (config.selected_index + 1) % config.total_songs
            config.song_finished = False
            play_current_song()

        try:
            timeout = 0.5
            if autoplay_deadline is not None:
                timeout = min(timeout, max(0, autoplay_deadline - time.monotonic()))

            order, value = play_queue.get(timeout=timeout)

            match order:
                case "PLAY":
                    file_name, _ = value
                    song_path = config.files / file_name
                    config.playback.load_file(str(song_path))
                    config.playback.play()
                    config.playback.set_volume(config.current_volume)
                    config.pause = False
                    autoplay_deadline = None
                case "TOGGLE_PAUSE":
                    if config.pause:
                        config.playback.resume()
                        config.pause = False
                    else:
                        config.playback.pause()
                        config.pause = True
                case "SKIP":
                    config.selected_index = (config.selected_index + value) % config.total_songs
                    if config.isplaying: play_current_song()
                    else: load_menu_song()
                case "VOLUME":
                    config.playback.set_volume(value)
                case "AUTOPLAY":
                    autoplay_deadline = time.monotonic() + config.autoplay_interval
                case "LOAD_MENU":
                    song_path = config.files / value
                    config.playback.load_file(str(song_path))
                    try:
                        config.menu_duration_str = format_time(config.playback.duration)
                    except Exception:
                        config.menu_duration_str = "0m 0s"
                case "STOP":
                    config.playback.stop()
                    break
        except queue.Empty:
            pass


def input_thread():
    while not config.boombox_shutdown:
        user_input = None
        if msvcrt.kbhit():
            keyboard = msvcrt.getch()
            if keyboard in [b'\xe0', b'\x00']:
                arrow = msvcrt.getch()
                if arrow == b'M': user_input = ">"
                elif arrow == b'K': user_input = "<"
                elif arrow == b'H': user_input = "up"
                elif arrow == b'P': user_input = "down"
            else:
                try:
                    user_input = keyboard.decode('utf-8', errors='ignore').lower()
                    if user_input == "\r": user_input = ""
                except: user_input = None
        time.sleep(0.05)
        if user_input == "s":
            config.boombox_shutdown = True
            break
        if user_input is not None:
            process_input(user_input)

