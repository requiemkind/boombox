import sys, os, threading, time, msvcrt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.config as config
from src import player
from src import ui_ascii
from src import ui_legacy
from src.utils import clean_ascii, ascii_alignment

def choice_menu():
    print("\033[?25l\033[H\033[J\033[2J", end='')
    art_lines = clean_ascii()
    selection_ui = [""] * len(art_lines)

    selection_ui[4] = "  Please select your Boombox UI:  "
    selection_ui[5] = "          ASCII                  "
    selection_ui[6] = "          Legacy Version         "

    if config.selected_option == 0:
        selection_ui[5] = "      >>  ASCII"
    else:
        selection_ui[6] = "      >>  Legacy Version"

    screen = "\n".join(art_lines[i] + "    " + selection_ui[i] for i in range(len(art_lines)))
    print(ascii_alignment(screen), end='')


def get_choice():
    previous_choice = -1
    while True:
        if config.selected_option != previous_choice:
            choice_menu()
            previous_choice = config.selected_option
            
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                arrow = msvcrt.getch()
                if arrow == b'P': config.selected_option = (config.selected_option + 1) % 2
                elif arrow == b'H': config.selected_option = (config.selected_option - 1) % 2
            else:
                char = key.decode('utf-8', errors='ignore').lower()
                if char in ["s", ".", ">"]: config.selected_option = (config.selected_option + 1) % 2
                elif char in ["w", ",", "<"]: config.selected_option = (config.selected_option - 1) % 2
                elif char == "\r":
                    return "ascii" if config.selected_option == 0 else "legacy"
        
        time.sleep(0.1)


def start_boombox():
    player.load_songs()

    if config.total_songs == 0:
        print("Empty Boombox! ('songs' folder is empty)")
        time.sleep(5)
        os._exit(0)

    t_audio = threading.Thread(target=player.audio_thread, daemon=True)
    t_audio.start()

    player.load_menu_song()
    mode = get_choice()

    t_input = threading.Thread(target=player.input_thread, daemon=True)
    t_input.start()

    print("\033[?25h")
    if mode == "ascii":
        ui_ascii.ascii_loop()
    else:
        ui_legacy.legacy_loop()

    t_input.join()
    player.play_queue.put(("STOP", None))
    t_audio.join()

    print("\033[H\033[J", end='') 
    print("\nThank you for using Boombox Project. Hope you enjoyed it.") # :)
    time.sleep(2)


if __name__ == "__main__":
    start_boombox()
