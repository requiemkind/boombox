import shutil, time
from wcwidth import wcswidth
import src.config as config
from src import player
from src.utils import *

def ascii_buttons(art_lines):
    autoplay_char = "@" if config.autoplay else "o"
    volume_str = f"{int((config.current_volume * 100) + 0.01):>3}%"
    art_lines[9] = art_lines[9].replace("o", autoplay_char)
    art_lines[9] = art_lines[9].replace(" 10%", volume_str)
    return art_lines


def ascii_cursor_fix(art_lines):
    terminal_width = shutil.get_terminal_size().columns
    art_width = max(wcswidth(line) for line in art_lines)
    alignment = max(0, (terminal_width - art_width) // 2)

    control_line = art_lines[7]
    target_index = control_line.index("[Enter]") + 3
    center_col = alignment + target_index + 1

    print(f"\033[10;{center_col}H", end="", flush=True)


def title_rolling(title):
    title_rolling = ("     " + title + "     " + title)[config.scroll_pos : config.scroll_pos+14]
    config.scroll_pos = (config.scroll_pos + 1) % (wcswidth(title) + 5)
    return title_rolling


def update_player_metrics():
    current_time = max(0, config.playback.curr_pos)
    total_time = config.playback.duration
    time_str = format_time(current_time, total_time)
    progress = progress_bar(current_time, total_time, width=30)
    roll_txt = title_rolling(config.playing_displayed)
    return time_str, progress, roll_txt


def ascii_menu():
    art_lines = clean_ascii()
    song_title = config.listed_songs_keys[config.selected_index]
    number = f"{config.selected_index + 1}."
    
    if wcswidth(song_title) > 14:
        while wcswidth(song_title + "...") > 14:
            song_title = song_title[:-1]
        song_title += "..."
        
    song_text = f"{number} {song_title}  [{config.menu_duration_str}]"
    select_text = f"Select your track ({config.total_songs}):"

    prefix = "  | | "
    suffix = " | |"
    content_width = len(art_lines[3]) - len(prefix) - len(suffix)

    art_lines[3] = prefix + visual_center(select_text, content_width) + suffix
    art_lines[4] = prefix + visual_center(song_text, content_width) + suffix
    art_lines = ascii_buttons(art_lines)

    screen = "\n".join(art_lines)
    print("\033[H\033[J\033[3J", end='')
    print(ascii_alignment(screen), end='')
    ascii_cursor_fix(art_lines)


def ascii_active(time_str, rolling_text):
    art_lines = clean_ascii()
    prefix = "  | | "
    suffix = " | |"
    content_width = len(art_lines[3]) - len(prefix) - len(suffix)

    art_lines[3] = prefix + "Now playing:".center(content_width) + suffix
    art_lines[4] = prefix + visual_center(rolling_text, content_width) + suffix
    art_lines[5] = prefix + time_str[:content_width].center(content_width) + suffix
    art_lines[6] = "  | |_________________________________________| |"

    art_lines = ascii_buttons(art_lines)
    screen = "\n".join(art_lines)

    print("\033[H\033[J\033[3J", end='')
    print(ascii_alignment(screen), end='')
    ascii_cursor_fix(art_lines)


def ascii_loop():
    try:
        while not config.boombox_shutdown:
            if not config.isplaying:
                ascii_menu()
            else:
                time_str, _, roll_txt = update_player_metrics()
                player.check_autoplay()
                ascii_active(time_str, roll_txt)
            time.sleep(0.5) # title rolling speed
    except KeyboardInterrupt:
        config.boombox_shutdown = True

