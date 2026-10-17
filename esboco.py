# ============================================
# PROJETO BOOMBOX
# Tocador de música em terminal com:
#   - Rolagem de título estilo rádio
#   - Contador de tempo
#   - Pause/resume com Enter
#   - Sair com [s]
# ============================================

# bibliotecas
from just_playback import Playback # tocador de musica
from pathlib import Path # pra mostrar qual música é
import time
import threading # faz que o input não pare a contagem
import shutil # pra ficar bonitinho no terminal
import rich

# Caminho pra poder aparecer a música atual e musica atual
files = Path(__file__).parent / 'songs'
song_list = sorted(files.glob('*.mp3'))

# current song
indice_selecionado = 0
mainsong = song_list[indice_selecionado]

tocando = False
playback = Playback()

# volume baixo
playback.set_volume(0.1)

titulos = {
    "vampira.mp3": " Willyrodriguezwastaken - Vampira ",
    "lupinlovinit.mp3": " Tommy Snyder - Lovin' You ",
    "luvsic2acoustica.mp3": " Nujabes - Luv(sic) Part 2 feat.Shing02 Acoustica ",
    "onceinalullaby.mp3": " Chris Christodolou - Once in a Lullaby ",
    "pentatonixattention.mp3": " Charlie Puth - Attention (Pentatonix Cover) ",
    "escalofrios.mp3": " Cataratas en Siberia - Escalofríos ",
    "luvsic5.mp3": " Nujabes - Luv(sic) Part 5 feat.Shing02 ",
    "waitingforyou.mp3": " Akira Yamaoka - Waiting for you "
}

titulo_base = titulos[mainsong.name]
titulo = titulo_base + "   " + titulo_base
i = 0  # Reseta a rolagem pro começo
limite = len(titulo_base) + 3

# Centralização
largura = shutil.get_terminal_size().columns
espacos_now = (largura - len("Now playing:")) // 2
espacos_titulo = (largura - 14) // 2 # 14 = largura fixa da janela de rolagem
espacos_msg = (largura - len("Pressione Enter para pausar/retomar, ou [s] sair... ")) // 2

# como aparece no terminal:

def desenhar_tela():
    global tocando, titulo_base, espacos_titulo_menu, espacos_msg

    # 1. Limpa a tela e vai pro topo
    print("\033[2J\033[H", end="", flush=True)
    print("\n" * 5, end="", flush=True)
    
    # 2. Define os textos baseados na fase
    if not tocando:
        texto_topo = f"Select your track ({len(song_list)}):"
        texto_baixo = "[ < ] ❚❚ [ > ] Use [Enter] to play"
        # Calcula a centralização exata pra estes textos
        esp_top = (largura - len(texto_topo)) // 2
        esp_msg = (largura - len(texto_baixo)) // 2
        
        print(f"{' ' * esp_top}{texto_topo}")
    else:
        texto_topo = "Now playing:"
        texto_baixo = "[ < ] ❚❚ [ > ]   [s] Sair"
        esp_top = (largura - len(texto_topo)) // 2
        esp_msg = (largura - len(texto_baixo)) // 2
        
        print(f"{' ' * esp_top}{texto_topo}")

    # 3. Imprime as linhas reservadas (título e tempo)
    print() # linha 1
    print() # linha 2
    print() # linha 3 (espaço)
    
    # 4. Imprime a mensagem de baixo
    print(f"{' ' * esp_msg}{texto_baixo}", end="")
    
    # 5. Sobe pra região reservada e salva a posição do cursor
    print("\033[F\033[F\033[F", end="", flush=True)
    print("\033[s", end="", flush=True)

desenhar_tela()

parar = False
pausado = False

def esperar_enter():
    global parar, pausado, tocando, indice_selecionado, titulo_base, titulo, i, limite
    
    while True:
        print("\033[u", end="", flush=True)
        print("\033[E\033[E\033[E", end="", flush=True)
        
        comando = input()
        
        if not tocando:
            if comando == ">":
                indice_selecionado = (indice_selecionado + 1) % len(song_list)
                desenhar_tela()
                
            elif comando == "<":
                indice_selecionado = (indice_selecionado - 1) % len(song_list)
                desenhar_tela()
                
            elif comando == "": 
                mainsong = song_list[indice_selecionado]
                playback.load_file(str(mainsong))
                playback.play()
                playback.set_volume(0.1)
                
                titulo_base = titulos[mainsong.name]
                titulo = titulo_base + "   " + titulo_base
                i = 0
                limite = len(titulo_base) + 3
                
                tocando = True
                desenhar_tela()
                
            elif comando.strip().lower().startswith("s"):
                parar = True
                break
        else:
            if comando.strip().lower().startswith("s"):
                parar = True
                break

            elif comando == ">":
                playback.stop()
                indice_selecionado = (indice_selecionado + 1) % len(song_list)

                mainsong = song_list[indice_selecionado]
                playback.load_file(str(mainsong))
                playback.play()
            # só pro teu miolo n estourar:
                playback.set_volume(0.1)

            # atualiza a exibição
                titulo_base = titulos[mainsong.name]
                titulo = titulo_base + "   " + titulo_base
                i = 0
                limite = len(titulo_base) + 3
                pausado = False

                desenhar_tela()

            elif comando == "<":
                playback.stop()
                indice_selecionado = (indice_selecionado - 1) % len(song_list)

                mainsong = song_list[indice_selecionado]
                playback.load_file(str(mainsong))
                playback.play()
            # pra tu não morrer²
                playback.set_volume(0.1)

                titulo_base = titulos[mainsong.name]
                titulo = titulo_base + "   " + titulo_base
                i = 0
                limite = len(titulo_base) + 3
                pausado = False
                
                desenhar_tela()

            else:
                if pausado:
                    playback.resume()
                    pausado = False
                else:
                    playback.pause()
                    pausado = True

threading.Thread(target=esperar_enter, daemon=True).start()

# importe pro pause não ficar esquisito
atual = 0
total = playback.duration

try:
    while not parar:
        if not tocando:
            # FASE 1: MENU DE SELEÇÃO
            # Pega a música atual e o título bonito dela
            mainsong = song_list[indice_selecionado]
            titulo_base = titulos[mainsong.name]
            
            # Pega a duração sem tocar (usando o playback temporariamente)
            playback.load_file(str(mainsong))
            duracao = playback.duration
            
            # Formata o tempo (ex: 3m 53s)
            minutos = int(duracao // 60)
            segundos = int(duracao % 60)
            tempo_str = f"{minutos}m {segundos}s"

            # Move o cursor pra região reservada e desenha
            print("\033[u", end="", flush=True)
            # Título (centralizado)

            texto_numerado = f"{indice_selecionado + 1}. {titulo_base.strip()}"

            espacos_titulo_menu = (largura - len(texto_numerado)) // 2
            print(f"\r{' ' * espacos_titulo_menu}{texto_numerado}\033[K", end="", flush=True)
            # Tempo (centralizado)
            espacos_tempo = (largura - len(tempo_str)) // 2
            print(f"\n{' ' * espacos_tempo}{tempo_str}\033[K", end="", flush=True)
            
            time.sleep(0.2) # Pausa pra não fritar a CPU, já que não tem animação aqui

        else:
            # FASE 2: TOCANDO MÚSICA
            if not pausado:
                atual = playback.curr_pos
                total = playback.duration
                i = (i + 1) % limite

            tempo_str = f"{atual:.0f}s / {total:.0f}s"
            espacos_tempo = (largura - len(tempo_str)) // 2

            print("\033[u", end="", flush=True) 
            
            print(f"\r{' ' * espacos_titulo}{titulo[i:i+14]}\033[K", end="", flush=True)
            print(f"\n{' ' * espacos_tempo}{tempo_str}\033[K", end="", flush=True)

            time.sleep(0.5)

except KeyboardInterrupt:
    parar = True

playback.stop()
print("\033[K", end="")   # limpa a linha atual (onde o s tava)
print("\033[E\033[E\033[E", end="")
print("\nAudio Encerrado\n")
