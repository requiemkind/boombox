from pathlib import Path
from just_playback import Playback
import os, sys, ctypes

base_path = Path(__file__).parent.parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent

if os.name == 'nt':
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

files = base_path / 'songs'
playback = Playback()

isplaying = False
pause = False
boombox_shutdown = False
autoplay = False
song_finished = False

selected_index = 0
current_volume = 0.1 # optimal (10%)
scroll_pos = 5
autoplay_interval = 1.5 # autoplay interval
selected_option = 0
total_songs = 0

playing_displayed = ""
menu_duration_str = "0m 0s"

listed_songs_keys = []
listed_songs_files = []
custom_titles = {}
