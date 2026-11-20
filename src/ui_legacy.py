import time
import src.config as config
from src import player
from src.utils import *

def boombox_menu(menu_duration):
    song_name = config.listed_songs_keys[config.selected_index]
    order = f"{config.selected_index + 1}."

    design = f"""

{center_alignment(f"Select your track (total: {config.total_songs}):")}\033[K
{center_alignment(f"{order} {song_name.strip()}")}\033[K
{center_alignment(menu_duration)}\033[K

{center_alignment("[ < ] [Enter] [ > ]")}\033[K
{center_alignment("[s] to stop")}\033[K
"""
    return design


def boombox_active(time_str, rolling_text, ispaused, volume, progress):
    play_icon = " ► " if ispaused else "❚❚ "
    autoplaystate = "ON" if config.autoplay else "OFF"
     
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

    return f"[{bar}] {int((vol * 100) + 0.01)}"


def update_legacy_metrics():
    current_time = max(0, config.playback.curr_pos)
    total_time = config.playback.duration
    time_str = format_time(current_time, total_time)
    progress = progress_bar(current_time, total_time, width=30)

    title = config.playing_displayed
    roll_txt = ("     " + title + "     " + title)[config.scroll_pos : config.scroll_pos+14]
    config.scroll_pos = (config.scroll_pos + 1) % (wcswidth(title) + 5)
    
    volume = volume_bar(config.current_volume, width=20)
    return time_str, progress, roll_txt, volume


def render_interface(time_str, roll_txt):
    if not config.isplaying:
        print(boombox_menu(config.menu_duration_str), end='')
        print(center_alignment("") + "\033[s", end='', flush=True)
    else:
        volume = volume_bar(config.current_volume, width=20)
        progress = progress_bar(config.playback.curr_pos, config.playback.duration, width=30)
        
        player.check_autoplay()
        print(boombox_active(time_str, roll_txt, config.pause, volume, progress), end='')
        print("\033[2A\033[G" + center_alignment("") + "\033[s", end='', flush=True)


def legacy_loop():
    try:
        while not config.boombox_shutdown:
            print("\033[H\033[J\033[3J", end='')
            time_str, _, roll_txt, _ = update_legacy_metrics()
            render_interface(time_str, roll_txt)
            print("\033[u", end='', flush=True)
            time.sleep(0.1 if not config.isplaying else 0.5)
    except KeyboardInterrupt:
        config.boombox_shutdown = True

