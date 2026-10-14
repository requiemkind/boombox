# bibliotecas
from just_playback import Playback # tocador de musica
from pathlib import Path # pra mostrar qual música é
import time
import threading
import sys

# Caminho pra poder aparecer a música atual e musica atual
files = Path(__file__).parent / 'songs'
mainsong = sorted(files.glob('*.mp3'))[5]

# Tocador de música
playback = Playback()
playback.load_file(str(mainsong))
playback.play()
playback.set_volume(0.01)

print(f"Now playing: {mainsong.stem}\n")

parar = False
def esperar_enter():
    global parar
    input()
    parar = True

threading.Thread(target=esperar_enter, daemon=True).start()

print("Pressione Enter para parar...")

try:
    while playback.active and not parar:

        atual = playback.curr_pos
        total = playback.duration
        print(f"\r{atual:.0f}s / {total:.0f}s   ", end="", flush=True)
        time.sleep(0.1)

except KeyboardInterrupt:
    parar = True

playback.stop()
print("\nAudio Encerrado\n")
