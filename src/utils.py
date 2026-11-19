from wcwidth import wcswidth
import shutil

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
  |    o                                  10%   |
  |                                             |
  |                   [POWER]                   |
  |_____________________________________________|
         |                               |
         |_______________________________|"""


def center_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    txt_alignment = (fullsize_x - wcswidth(txt)) // 2
    txt = " " * txt_alignment + txt
    return txt


def ascii_alignment(txt):
    fullsize_x = shutil.get_terminal_size().columns
    lines = txt.splitlines()
    max_width = max((wcswidth(line) for line in lines), default=0)
    alignment = max(0, (fullsize_x - max_width) // 2)
    return "\n".join(" " * alignment + line for line in lines)


def visual_center(txt, width): # for different character widths
    return txt.center(width - (wcswidth(txt) - len(txt)))


def clean_ascii():
    return [line.rstrip() for line in boombox().strip("\n").splitlines()]


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

    return f"[{bar}] {int((vol * 100) + 0.01)}"


def title_rolling(title, scroll_pos): # 'Mobius strip' logic
    title_rolling = ("     " + title + "     " + title)[scroll_pos : scroll_pos+14]
    scroll_pos = (scroll_pos + 1) % (wcswidth(title) + 5)

    return title_rolling

