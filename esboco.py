# bibliotecas
from just_playback import Playback # tocador de musica
from pathlib import Path # pra mostrar qual música é
import time
import threading # faz que o input não pare a contagem
import shutil # pra ficar bonitinho no terminal

# Caminho pra poder aparecer a música atual e musica atual
files = Path(__file__).parent / 'songs'
mainsong = sorted(files.glob('*.mp3'))[3]

# Tocador de música
playback = Playback()
playback.load_file(str(mainsong))
playback.play()
playback.set_volume(0.1)

titulos = {
    "vampira.mp3": " Willyrodriguezwastaken - Vampira ",
    "lupinlovinit.mp3": " Tommy Snyder - Lovin' You ",
    "luvsic2acoustica.mp3": " Nujabes - Luv(sic) Part 2 feat.Shing02 Acoustica ",
    "onceinalullaby.mp3": " Chris Christodolou - Once in a Lullaby ",
    "pentatonixattention.mp3": " Charlie Puth - Attention (Pentatonix Cover) ",
    "escalofrios.mp3": " Cataratas en Siberia - Escalofríos ",
}

titulo_base = titulos[mainsong.name]
titulo = titulo_base + "   " + titulo_base # 3 espaços + cópia

i = 0
limite = len(titulo_base) + 3 # tamanho de UM título + os 3 espaços

# Centralização
largura = shutil.get_terminal_size().columns
espacos_now = (largura - len("Now playing:")) // 2
espacos_titulo = (largura - 14) // 2
espacos_msg = (largura - len("Pressione Enter para parar...")) // 2

# como aparece no terminal:
print("\n")
print(f"{' ' * espacos_now}Now playing:")
print()                                    # linha em branco 1 (título)
print()                                    # linha em branco 2 (tempo)
print()                                    # ← espaço entre o tempo e a msg
print(f"{' ' * espacos_msg}Pressione Enter para parar...", end="")

# Sobe 3 linhas pra ficar na região reservada
print("\033[F\033[F\033[F", end="", flush=True)

parar = False
def esperar_enter():
    global parar
    input()
    parar = True

threading.Thread(target=esperar_enter, daemon=True).start()

try:
    while playback.active and not parar:
    # pegando o tempo atual e total    
        atual = playback.curr_pos
        total = playback.duration

        tempo_str = f"{atual:.0f}s / {total:.0f}s"
        espacos_tempo = (largura - len(tempo_str)) // 2

    # Linha 1: título rolando
        print(f"\r{' ' * espacos_titulo}{titulo[i:i+14]}\033[K", end="", flush=True)

    # Linha 2: tempo
        print(f"\n{' ' * espacos_tempo}{tempo_str}\033[K", end="", flush=True)

    # Sobe uma linha pra próxima iteração
        print(f"\033[F", end="", flush=True)

        time.sleep(0.5)
        i = (i + 1) % limite

except KeyboardInterrupt:
    parar = True

playback.stop()
print()
print()
print("\nAudio Encerrado\n")
