from logging import exception
import tkinter as tk
from deep_translator.google import GoogleTranslator
from gradio.themes.utils.colors import yellow
from pandas._libs.tslibs import Resolution
import pygame as py
import threading
import os

import torch
from diffusers import FluxKontextPipeline
from diffusers import FluxTransformer2DModel
from transformers import T5EncoderModel
from optimum.quanto import freeze, qfloat8, quantize
from PIL import Image
from deep_translator import GoogleTranslator as G
import os
import threading
from tkinter import ttk

path_file = None

if os.path.exists("select.txt"):
    with open("select.txt", 'r') as f:
        path_file = f.readline().strip()

if path_file and os.path.exists(path_file):
    Nome = os.path.basename(path_file).split('.')[0]
    print(f"Nome: {Nome}")
else:
    print("Errore: File non trovato o percorso non valido")
    Nome = "Sconosciuto"

 


import sys
import subprocess
import random
import os
from PIL import Image

# ========== CARICAMENTO SAVE ==========
if os.path.exists(f"{Nome}_save.txt"):
    print("Caricamento save...")
    with open(f"{Nome}_save.txt", 'r') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':')
                if key == "fame":
                    fame = int(value)
                elif key == "sete":
                    sete = int(value)
                elif key == "last_fame_update":
                    last_fame_update = int(value)
                elif key == "last_sete_update":
                    last_sete_update = int(value)
                elif key == "frame_count":
                    frame_count = int(value)
                elif key == "vita_girl":
                    vita_girl = int(value)
                elif key == "vita_player":
                    vita_player = int(value)
                elif key == "contaTDattaco":
                    contaTDattaco = int(value)
                elif key == "countg":
                    countg = int(value)
                # ========== CARICA IL RECORD ==========
                elif key == "record_secondi":
                    record_secondi_saved = float(value)
                elif key == "record_cum":
                    record_cum_saved = int(value)
                # ======================================
    
    # ========== RICOSTRUISCI IL RECORD ==========
    try:
        if record_secondi_saved > 0 and record_cum_saved > 0:
            record = (record_secondi_saved, record_cum_saved)
            rate = record_cum_saved / record_secondi_saved
            print(f"✅ Record caricato: {record_cum_saved} cum in {record_secondi_saved:.2f}s ({rate:.2f}/s)")
        else:
            record = None
            print("ℹ️ Nessun record presente")
    except:
        record = None
        print("⚠️ Errore caricamento record, resettato")
    # ============================================
    
    # Reset contatori pen_sega (questi NON vanno salvati, ripartono da 0)
    count_cum = 0
    sega_frame_count = 0
    
    print(f"{Nome}_save caricato.....!")
else:
    # Valori di default se non esiste il save
    fame = 0
    sete = 0
    last_fame_update = 0
    last_sete_update = 0
    frame_count = 0
    vita_girl = 100
    vita_player = 100
    contaTDattaco = 1
    countg = 1
    
    # ========== INIZIALIZZA RECORD A NONE ==========
    record = None
    count_cum = 0
    sega_frame_count = 0
    print("Nessun save trovato, valori di default caricati")
    # ===============================================

# Variabile globale per controllare il loop Pygame
running = True
screen = None
current_image = None
is_generating = False

milles = 0
second = 0
minut = 0
ore = 0
Day = 0

# Variabili per il sistema di cibo/bevanda
cibo = 0  # 0=nessuno, 1=generato, 2=composto in NanoBanana/Kontext
bevanda = 0  # 0=nessuno, 1=generato, 2=composto in NanoBanana/Kontext

# Altre variabili
max_girls = random.randint(10, 20)
dead1 = False
dead2 = False

import os

if os.path.exists("impo.txt"):
    try:
        # Leggi il file impo.txt
        with open("impo.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Inizializza valori di default
        max_soglia_fame = 3600000  # 1 ora default
        max_soglia_sete = 3600000  # 1 ora default
        tempodiattacco = 600000    # 10 min default
        
        # Leggi i valori dal file
        for line in lines:
            line = line.strip()
            if line.startswith('fame:'):
                max_soglia_fame = int(line.split(':')[1].replace(';', ''))
            elif line.startswith('sete:'):
                max_soglia_sete = int(line.split(':')[1].replace(';', ''))
            elif line.startswith('attacco:'):
                tempodiattacco = int(line.split(':')[1].replace(';', ''))
        
        print(f"✅ Impostazioni caricate da impo.txt:")
        print(f"  Fame: {max_soglia_fame}ms ({max_soglia_fame/3600000:.1f}h)")
        print(f"  Sete: {max_soglia_sete}ms ({max_soglia_sete/3600000:.1f}h)")
        print(f"  Attacco: {tempodiattacco}ms ({tempodiattacco/60000:.1f}min)")
        
    except Exception as e:
        print(f"❌ Errore lettura impo.txt: {e}")
        # Valori di default in caso di errore
        tempodiattacco = 600000      # 10 minuti
        max_soglia_fame = 3600000    # 1 ora
        max_soglia_sete = 3600000    # 1 ora
else:
    # File non esiste, usa valori di default
    print("⚠️ impo.txt non trovato, uso valori di default")
    tempodiattacco = 600000      # 10 minuti
    max_soglia_fame = 3600000    # 1 ora
    max_soglia_sete = 3600000    # 1 ora


dim = 100
# Carica Immagini da g_00000 a g_00003
girls = [Image.open(f"./framesg/g_0000{k}.png").convert("RGBA").resize((dim, dim)) for k in range(4)]
# Carica Immagini da g_00004 a g_00007
girls_M = [Image.open(f"./framesg/g_0000{k}.png").convert("RGBA").resize((dim, dim)) for k in range(4, 8)]
# Carica Immagini da g_00008 a g_00011
girls_S = [Image.open(f"./framesg/g_0000{k}.png" if k < 10 else f"./framesg/g_000{k}.png").convert("RGBA").resize((dim, dim)) for k in range(8, 12)]
# da g_00012 a g_00015
girls_D = [Image.open(f"./framesg/g_000{k}.png").convert("RGBA").resize((dim, dim)) for k in range(12, 16)]

x1 = 0
y1 = 0
x2 = 0
y2 = 0
current1 = None
current2 = None
attaco = False
select = False

stampa_parametri=True

gun= Image.open("gun1.png").convert("RGBA")
gunfire= Image.open("gun2.png").convert("RGBA")




# Funzione di conversione PIL -> Pygame (FUORI dalla funzione avvia_pygame)
def pil_to_pygame(pil_image):
    import pygame as py
    return py.image.fromstring(
        pil_image.tobytes(), pil_image.size, pil_image.mode
    )
# Converti in Pygame surface subito (PRIMA di avvia_pygame)
gun_pygame = pil_to_pygame(gun)
gunfire_pygame = pil_to_pygame(gunfire)

# MUSICA DI SOTTOFONDO (musica rilassante standard)
musica_normale = r"./music//Whispers of the Canopy.mp3"  # Sostituisci con il nome del tuo file

# MUSICA DI ATTACCO (musica adrenalinica)
musica_attacco = r"./music//War Cry.mp3"  # Sostituisci con il nome del tuo file

# EFFETTO SONORO SPARO
suono_sparo = None  # Lo caricheremo dopo py.init()

fase_dorme1=False
fase_dorme2=False
fase_dorme3=False

#velori combobox pens dichiuarta nel main 
#['Disabilita Pen','Pen_frontal','Pen_right','Pen_left']

pen_f=Image.open('./pen//Pen_frontal.png')
pen_l=Image.open('./pen//Pen_left.png')
pen_r=Image.open('./pen//Pen_right.png')

pen_f_piss= Image.open('./pen//Pen_frontal_piss.png')
pen_f_s1= Image.open('./pen//Pen_frontal_s1.png')
pen_f_s2= Image.open('./pen//Pen_frontal_s2.png')

cum = []
# Immagini da c1.png a c6.png in cum
for c in range(1, 7): 
    cum.append(Image.open(f"./cum//c{c}.png"))

p = False
s = 0
conta_S = 0
newimagevuota = None
cum_pygame = []  # Lista per le versioni pygame delle immagini cum

pen_current = None


sega_frame_count = 0  # Contatore frame SOLO per pen_sega (si resetta)

def avvia_pygame():
    global screen, current_image, is_generating, pen_f_piss, pen_f_s1, pen_f_s2, cum, p, s
    global milles, second, minut, ore, Day
    global vita_girl, vita_player
    global fame, sete, last_fame_update, last_sete_update
    global cibo, bevanda
    global frame_count
    global x1, y1, x2, y2, current1, current2, attaco, select, max_girls, countg, dead1, dead2, tempodiattacco, contaTDattaco
    global ind, ind2
    global running, stampa_parametri
    global gun_pygame, gunfire_pygame, suono_sparo
    global max_soglia_fame, max_soglia_sete, fase_dorme3, fase_dorme2, fase_dorme1 
    global pen_f, pen_r, pen_l, pen_current, pens, azione, compi_azione, conta_S
    global newimagevuota, cum_pygame
    global record, count_cum, sega_frame_count
     
    # Inizializza Pygame
    py.init()

    # Inizializza il mixer audio
    py.mixer.init()
    
    # Carica l'effetto sonoro dello sparo
    try:
        suono_sparo = py.mixer.Sound("./music//deagle-shot-sound.mp3")
        suono_sparo.set_volume(0.7)  # Volume 0.0 - 1.0
    except:
        print("ATTENZIONE: File sparo.wav non trovato!")
        suono_sparo = None
    
    # Carica e avvia la musica di sottofondo normale
    try:
        py.mixer.music.load(musica_normale)
        py.mixer.music.set_volume(0.5)
        py.mixer.music.play(-1)
    except:
        print("ATTENZIONE: File musica_normale.mp3 non trovato!")
    
    musica_attacco_attiva = False
    current_gun = gun_pygame
    
    # Disabilita lo scaling DPI di Windows
    import ctypes
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass
    
    # Calcola la posizione centrata
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{(1920-1024)//2},0'
    
    # Crea finestra
    screen = py.display.set_mode((1024, 1024), py.HWSURFACE | py.DOUBLEBUF)
    hardware_surface = py.Surface((1024, 1024), py.HWSURFACE | py.DOUBLEBUF)
    py.display.set_caption("Game Display")
    
    # Font per il testo
    font = py.font.Font(None, 48)
    timer_font = py.font.Font(None, 24)
    
    clock = py.time.Clock()

    # Converti le immagini PIL in Surface pygame PRIMA del loop
    pen_f_pygame = pil_to_pygame(pen_f)
    pen_f_piss_pygame = pil_to_pygame(pen_f_piss)
    pen_f_s1_pygame = pil_to_pygame(pen_f_s1)
    pen_f_s2_pygame = pil_to_pygame(pen_f_s2)
    pen_l_pygame = pil_to_pygame(pen_l)
    pen_r_pygame = pil_to_pygame(pen_r)
    pen_current_pygame = None
    
    # Converti le immagini cum in pygame
    for cum_img in cum:
        cum_pygame.append(pil_to_pygame(cum_img))
    
    # Inizializza l'immagine vuota per il cum come surface pygame
    newimagevuota = py.Surface((1024, 1024), py.SRCALPHA)
    newimagevuota.fill((0, 0, 0, 0))  # Trasparente
    
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
                py.mixer.music.stop()
                window.quit()
            
            # Click sinistro
            if event.type == py.MOUSEBUTTONDOWN and event.button == 1 and attaco == False and pen_current_pygame is not None:
                if pens.get() == 'pen_sega':
                    conta_S += 1  # Incrementa il contatore
                    s += 1
                    if s > 2:
                        s = 0
                    
                    # Ogni 10 click aggiungi una macchia di cum
                    if conta_S >= 10:
                        count_cum += 1  # Incrementa il contatore totale di cum
                        selectcum = random.choice(cum_pygame)
                        mouse_pos = py.mouse.get_pos()
                        
                        # Calcola posizione centrata sulla macchia
                        cum_rect = selectcum.get_rect()
                        cum_rect.center = mouse_pos
                        
                        # Disegna la macchia sulla surface trasparente
                        newimagevuota.blit(selectcum, cum_rect)
                        
                        # Reset contatore
                        conta_S = 0
                        print(f"Cum aggiunto alla posizione {mouse_pos}")
                        
                        # ========== CALCOLO RECORD ==========
                        # Usa il contatore dedicato per pen_sega
                        secondi_trascorsi = sega_frame_count / 60  # 60 FPS = 1 secondo ogni 60 frame
                        
                        # Calcola il "rate" = cum per secondo
                        if secondi_trascorsi > 0:
                            rate_attuale = count_cum / secondi_trascorsi
                        else:
                            rate_attuale = 0
                        
                        # Aggiorna il record se:
                        # 1. Non esiste ancora (record == None)
                        # 2. Il rate attuale è migliore del record precedente
                        if record is None:
                            record = (secondi_trascorsi, count_cum)
                            print(f"NUOVO RECORD: {count_cum} cum in {secondi_trascorsi:.2f}s (rate: {rate_attuale:.2f} cum/s)")
                        else:
                            record_secondi, record_cum = record
                            if record_secondi > 0:
                                rate_record = record_cum / record_secondi
                            else:
                                rate_record = 0
                            
                            if rate_attuale > rate_record:
                                record = (secondi_trascorsi, count_cum)
                                print(f"NUOVO RECORD: {count_cum} cum in {secondi_trascorsi:.2f}s (rate: {rate_attuale:.2f} cum/s)")
                        # ====================================

                elif pens.get() == 'Pen_frontal':
                    p = not p
            
        # Salva screenshot con click destro
        if event.type == py.MOUSEBUTTONDOWN and event.button == 3 and attaco == False and pen_current_pygame is not None:
            
            def save_screenshot_with_background(background_path, output_name):
                """Funzione helper per salvare screenshot con un background specifico"""
                # Crea una nuova immagine PIL vuota 1024x1024
                new_image = Image.new('RGB', (1024, 1024), (0, 0, 0))
                
                # Carica l'immagine di sfondo
                try:
                    background = Image.open(background_path)
                    bg_x = (1024 - background.width) // 2
                    bg_y = (1024 - background.height) // 2
                    new_image.paste(background, (bg_x, bg_y))
                except Exception as e:
                    print(f"ATTENZIONE: File {background_path} non trovato! Errore: {e}")
                
                # Converti la pen pygame in PIL
                pen_string = py.image.tostring(pen_current_pygame, 'RGBA')
                pen_pil = Image.frombytes('RGBA', pen_current_pygame.get_size(), pen_string)
                
                # Calcola la posizione del pennello
                mouse_pos = py.mouse.get_pos()
                
                if pens.get() == 'Pen_right':
                    pen_x = mouse_pos[0] - 1753
                    pen_y = mouse_pos[1] - 1024
                elif pens.get() == 'Pen_left':
                    pen_x = mouse_pos[0] - 295
                    pen_y = mouse_pos[1] - 1024
                elif pens.get() == 'Pen_frontal' or pens.get() == 'pen_sega':
                    pen_rect_temp = pen_current_pygame.get_rect()
                    pen_rect_temp.centerx = mouse_pos[0]
                    pen_rect_temp.top = mouse_pos[1]
                    pen_x = pen_rect_temp.x
                    pen_y = pen_rect_temp.y
                
                # Incolla il pennello sulla nuova immagine
                new_image.paste(pen_pil, (pen_x, pen_y), pen_pil)
                
                # Se c'è cum, aggiungilo anche allo screenshot
                if pens.get() == 'pen_sega' and newimagevuota:
                    cum_string = py.image.tostring(newimagevuota, 'RGBA')
                    cum_pil = Image.frombytes('RGBA', newimagevuota.get_size(), cum_string)
                    new_image.paste(cum_pil, (0, 0), cum_pil)
                
                # Salva l'immagine
                new_image.save(output_name)
                print(f"Screenshot salvato come '{output_name}'")
            
            # Salva screenshot con background originale
            save_screenshot_with_background(f"{Nome}_photogamer.png", "screenshot_original.png")
            
            # Salva screenshot con background generato da SD (se esiste)
            if os.path.exists("./sdImage.png"):
                save_screenshot_with_background("./sdImage.png", "screenshot_generated.png")
            else:
                print("sdImage.png non trovato, screenshot con AI non salvato")
            compi_azione.config(state='normal')
            azione.config(state='readonly')
        
        # Rendering - SFONDO ROSSO SANGUE
        screen.fill((101, 0, 0))

        if is_generating:
            text = font.render("Attendi Generazione Immagine Iniziale...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(512, 512))
            screen.blit(text, text_rect)
        elif current_image:
            screen.blit(current_image, (0, 0))
        elif not current_image:
            py.display.flip()

        if attaco == False:
            # Seleziona la pen corretta
            if pens.get() == 'Pen_frontal' and p == False:
                pen_current_pygame = pen_f_pygame
                s = 0
                # RESET contatori quando cambi pen
                sega_frame_count = 0
                count_cum = 0
                record = None
            elif pens.get() == 'pen_sega' and p == False and s == 0:
                pen_current_pygame = pen_f_pygame
                p = False
                # Incrementa il contatore SOLO quando pen_sega è attiva
                sega_frame_count += 1
            elif pens.get() == 'pen_sega' and p == False and s == 1:
                pen_current_pygame = pen_f_s1_pygame
                p = False
                # Incrementa il contatore SOLO quando pen_sega è attiva
                sega_frame_count += 1
            elif pens.get() == 'pen_sega' and p == False and s == 2:
                pen_current_pygame = pen_f_s2_pygame
                p = False
                # Incrementa il contatore SOLO quando pen_sega è attiva
                sega_frame_count += 1
            elif pens.get() == 'Pen_frontal' and p == True:
                pen_current_pygame = pen_f_piss_pygame
                # RESET contatori quando cambi pen
                sega_frame_count = 0
                count_cum = 0
                record = None
            elif pens.get() == 'Pen_right':
                pen_current_pygame = pen_r_pygame
                p = False
                s = 0
                # RESET contatori quando cambi pen
                sega_frame_count = 0
                count_cum = 0
                record = None
            elif pens.get() == 'Pen_left':
                pen_current_pygame = pen_l_pygame
                p = False
                s = 0
                # RESET contatori quando cambi pen
                sega_frame_count = 0
                count_cum = 0
                record = None
            else:
                pen_current_pygame = None
                p = False
                s = 0
                # RESET contatori quando cambi pen
                sega_frame_count = 0
                count_cum = 0
                record = None
            
            # Disegna la pen
            if pen_current_pygame is not None:
                mouse_pos = py.mouse.get_pos()
                pen_rect = pen_current_pygame.get_rect()
                
                if pens.get() == 'Pen_right':
                    pen_rect.x = mouse_pos[0] - 1753
                    pen_rect.y = mouse_pos[1] - 1024
                elif pens.get() == 'Pen_left':
                    pen_rect.x = mouse_pos[0] - 295
                    pen_rect.y = mouse_pos[1] - 1024
                elif pens.get() == 'Pen_frontal' or pens.get() == 'pen_sega':
                    pen_rect.centerx = mouse_pos[0]
                    pen_rect.top = mouse_pos[1]
                
                # Disegna prima il layer di cum
                if pens.get() == 'pen_sega':
                    screen.blit(newimagevuota, (0, 0))
                
                # Poi disegna la pen SOPRA il cum
                screen.blit(pen_current_pygame, pen_rect)
        
        # Mostra il contatore per debug
        if pens.get() == 'pen_sega':
            counter_text = timer_font.render(f"Clicks: {conta_S}/10", True, (255, 255, 255))
            screen.blit(counter_text, (10, 70))
        
        # ========== MOSTRA IL RECORD SEMPRE (fuori dal blocco attaco) ==========
        # Mostra il RECORD in alto a destra (sempre visibile)
        if record is None:
            # Se non c'è ancora un record, mostra valori iniziali
            record_text = timer_font.render("RECORD: 0 cum in 0.0s (0.00/s)", True, (255, 215, 0))
        else:
            # Mostra il record attuale
            record_secondi, record_cum = record
            rate_record = record_cum / record_secondi if record_secondi > 0 else 0
            record_text = timer_font.render(
                f"RECORD: {record_cum} cum in {record_secondi:.1f}s ({rate_record:.2f}/s)", 
                True, 
                (255, 215, 0)  # Colore oro per il record
            )
        
        # Posiziona in alto a sinistra, spostato 30px in basso
        record_rect = record_text.get_rect()
        record_rect.topleft = (10, 90)  # 10px dal bordo sinistro, 40px dall'alto (30px sotto il contatore)
        screen.blit(record_text, record_rect)
        # ======================================================================
        


             
        
        # Calcolo del tempo (assumendo 60 FPS)
        #se dorma avanza di 8 ore = 
        if fase_dorme3==True:
            frame_count += 1728000
            fase_dorme1=False
            fase_dorme2=False
            fase_dorme3=False
        else:    
            frame_count += 1
        total_seconds = frame_count // 60
        
        Day = total_seconds // 86400
        ore = (total_seconds % 86400) // 3600
        minut = (total_seconds % 3600) // 60
        second = total_seconds % 60
        
        if Day >= 100:
            Day = 99
            ore = 23
            minut = 59
            second = 59
        
        # Aggiorna SETE ogni 2 ore (432000 frame)
        if (frame_count - last_sete_update) * (1000 / 60) >= max_soglia_sete:
            sete = min(100, sete + 1)
            last_sete_update = frame_count

        # Aggiorna FAME in base all'impostazione caricata
        if (frame_count - last_fame_update) * (1000 / 60) >= max_soglia_fame:
            fame = min(100, fame + 1)
            last_fame_update = frame_count
        
        if stampa_parametri == True:
            # Calcola millisecondi trascorsi
            tempo_trascorso_sete_ms = (frame_count - last_sete_update) * (1000 / 60)
            tempo_trascorso_fame_ms = (frame_count - last_fame_update) * (1000 / 60)
            
            # Converti in minuti per visualizzazione
            tempo_trascorso_sete_minuti = tempo_trascorso_sete_ms / 60000
            tempo_trascorso_fame_minuti = tempo_trascorso_fame_ms / 60000
            soglia_sete_minuti = max_soglia_sete / 60000
            soglia_fame_minuti = max_soglia_fame / 60000
            
            print(f"Tempo trascorso SETE: {tempo_trascorso_sete_minuti:.2f}/{soglia_sete_minuti:.0f} minuti")
            print(f"Tempo trascorso FAME: {tempo_trascorso_fame_minuti:.2f}/{soglia_fame_minuti:.0f} minuti")
        
        # Effetti su vita del player per fame/sete alta
        if sete >= 80 or fame >= 80:
            if frame_count % 60 == 0:
                vita_player = max(0, vita_player - 1)
        
        # Renderizza il timer in alto a destra
        timer_text = f"Tempo: {Day}/100 giorni {ore:02d}:{minut:02d}:{second:02d}"
        timer_surface = timer_font.render(timer_text, True, (255, 255, 0))
        timer_rect = timer_surface.get_rect(topright=(1010, 10))
        
        bg_rect = py.Rect(timer_rect.x - 5, timer_rect.y - 5, 
                          timer_rect.width + 10, timer_rect.height + 10)
        py.draw.rect(screen, (180, 0, 0), bg_rect)
        screen.blit(timer_surface, timer_rect)
        
        # Barra vita Girl
        girl_bar_y = timer_rect.bottom + 10
        girl_label = timer_font.render("Girl:", True, (255, 255, 0))
        screen.blit(girl_label, (timer_rect.x, girl_bar_y))
        
        bar_width = 150
        bar_height = 18
        bar_x = timer_rect.x + girl_label.get_width() + 8
        py.draw.rect(screen, (180, 0, 0), (bar_x, girl_bar_y, bar_width, bar_height))
        
        girl_bar_fill = int((vita_girl / 100) * bar_width)
        if vita_girl > 66:
            girl_color = (0, 255, 0)
        elif vita_girl > 33:
            girl_color = (255, 255, 0)
        else:
            girl_color = (255, 0, 0)
        
        if girl_bar_fill > 0:
            py.draw.rect(screen, girl_color, (bar_x, girl_bar_y, girl_bar_fill, bar_height))
        
        girl_percent = timer_font.render(f"{vita_girl}%", True, (0, 0, 0))
        girl_percent_rect = girl_percent.get_rect(center=(bar_x + bar_width // 2, girl_bar_y + bar_height // 2))
        screen.blit(girl_percent, girl_percent_rect)
        
        # Barra vita Player
        player_bar_y = girl_bar_y + bar_height + 8
        player_label = timer_font.render("Player:", True, (255, 255, 0))
        screen.blit(player_label, (timer_rect.x, player_bar_y))
        
        bar_x_player = timer_rect.x + player_label.get_width() + 8
        py.draw.rect(screen, (180, 0, 0), (bar_x_player, player_bar_y, bar_width, bar_height))
        
        player_bar_fill = int((vita_player / 100) * bar_width)
        if vita_player > 66:
            player_color = (0, 255, 0)
        elif vita_player > 33:
            player_color = (255, 255, 0)
        else:
            player_color = (255, 0, 0)
        
        if player_bar_fill > 0:
            py.draw.rect(screen, player_color, (bar_x_player, player_bar_y, player_bar_fill, bar_height))
        
        player_percent = timer_font.render(f"{vita_player}%", True, (0, 0, 0))
        player_percent_rect = player_percent.get_rect(center=(bar_x_player + bar_width // 2, player_bar_y + bar_height // 2))
        screen.blit(player_percent, player_percent_rect)

        # Controlli e logica di RESET richiesti dall'utente
        # NOTA BENE: La logica del gioco (es: danno, game over) dovrebbe idealmente
        # risiedere nella funzione di aggiornamento dello stato del gioco,
        # non in questa funzione di disegno.

        # Barre FAME E SETE (Inizio del Disegno)
        bar_width_max = 200
        bar_height_fs = 20
        bar_x_left = 10
        fame_bar_y = 10
        sete_bar_y = 35

        # Calcola la larghezza dell'etichetta più lunga per allineare le barre
        # Usiamo "Sete:" che è più lunga di "Fame:" per garantire l'allineamento.
        label_width = timer_font.render("Sete:", True, (255, 255, 0)).get_width() + 5
        bar_start_x = bar_x_left + label_width


        # --- Barra FAME ---
        # 1. Disegna l'etichetta
        fame_label = timer_font.render("Fame:", True, (255, 255, 0))
        screen.blit(fame_label, (bar_x_left, fame_bar_y))

        # 2. Disegna lo sfondo della barra (lo "zero" della barra)
        sfondo_fame_rect = (bar_start_x, fame_bar_y, bar_width_max, bar_height_fs)
        py.draw.rect(screen, (60, 30, 10), sfondo_fame_rect) # Sfondo Marrone/Nero

        # 3. Calcola il riempimento e il colore
        fame_fill = int((fame / 100) * bar_width_max)

        if fame < 33:
            fame_color = (139, 69, 19) # Marrone scuro (poco pieno)
        elif fame < 66:
            fame_color = (255, 140, 0) # Arancione (medio)
        else:
            fame_color = (255, 0, 0)   # Rosso (molto pieno)

        # 4. Disegna il riempimento EFFETTIVO (solo se fame > 0)
        if fame_fill > 0:
            py.draw.rect(screen, fame_color, (bar_start_x, fame_bar_y, fame_fill, bar_height_fs))

        # 5. Disegna la percentuale al centro
        fame_percent = timer_font.render(f"{fame}%", True, (255, 255, 255))
        fame_percent_rect = fame_percent.get_rect(center=(bar_start_x + bar_width_max // 2, fame_bar_y + bar_height_fs // 2))
        screen.blit(fame_percent, fame_percent_rect)


        # --- Barra SETE ---
        # 1. Disegna l'etichetta
        sete_label = timer_font.render("Sete:", True, (255, 255, 0))
        screen.blit(sete_label, (bar_x_left, sete_bar_y))

        # 2. Disegna lo sfondo della barra (lo "zero" della barra)
        sfondo_sete_rect = (bar_start_x, sete_bar_y, bar_width_max, bar_height_fs)
        py.draw.rect(screen, (0, 20, 40), sfondo_sete_rect) # Sfondo Blu Scuro/Nero

        # 3. Calcola il riempimento e il colore
        sete_fill = int((sete / 100) * bar_width_max)

        if sete < 33:
            sete_color = (135, 206, 235) # Azzurro chiaro (poco pieno)
        elif sete < 66:
            sete_color = (0, 0, 255)     # Blu (medio)
        else:
            sete_color = (255, 0, 0)     # Rosso (molto pieno)

        # 4. Disegna il riempimento EFFETTIVO (solo se sete > 0)
        if sete_fill > 0:
            py.draw.rect(screen, sete_color, (bar_start_x, sete_bar_y, sete_fill, bar_height_fs))

        # 5. Disegna la percentuale al centro
        sete_percent = timer_font.render(f"{sete}%", True, (255, 255, 255))
        sete_percent_rect = sete_percent.get_rect(center=(bar_start_x + bar_width_max // 2, sete_bar_y + bar_height_fs // 2))
        screen.blit(sete_percent, sete_percent_rect)

        # Timer di attacco
        # Timer di attacco
        if (contaTDattaco * (1000 / 60)) < tempodiattacco:
            contaTDattaco += 1
            if stampa_parametri == True:
                tempo_trascorso_attacco_ms = contaTDattaco * (1000 / 60)
                tempo_trascorso_minuti = tempo_trascorso_attacco_ms / 60000
                tempo_max_minuti = tempodiattacco / 60000
                print(f"Tempo di attacco: {tempo_trascorso_minuti:.2f}/{tempo_max_minuti:.2f} minuti")

        if (contaTDattaco * (1000 / 60)) >= tempodiattacco:
            if pens.get()=='Disabilita Pen':
                attaco = True
        if stampa_parametri==True:
            print(f"ragazze generate {countg} di max {max_girls}")
        
        if countg == max_girls:
            attaco = False
            contaTDattaco = 0
            countg = 1
       

        # ========== SISTEMA DI ATTACCO RAGAZZE ==========
        if attaco == True and current_image is not None:
            # CAMBIA MUSICA QUANDO PARTE L'ATTACCO
            if musica_attacco_attiva == False:
                try:
                    py.mixer.music.load(musica_attacco)
                    py.mixer.music.set_volume(0.5)  # Volume musica d'attacco
                    py.mixer.music.play(-1)  # Loop
                    musica_attacco_attiva = True
                except:
                    print("ATTENZIONE: File musica_attacco.mp3 non trovato!")
            py.display.flip()  # ← AGGIUNGI QUESTO!
            background_snapshot = screen.copy()
            
            if select == False:
                ind = random.randint(0, len(girls) - 1)
                ind2 = random.randint(0, len(girls) - 1)
                select = True
                dead1 = False
                dead2 = False
                current1 = girls[ind]
                current2 = girls[ind2]
            
                x1 = random.randint(10, screen.get_width() - dim)
                y1 = 10
                x2 = screen.get_width() - dim
                y2 = screen.get_height() - dim - 20
            
            # FASE 1: MOVIMENTO
            for _ in range(100):
                frame_count += 1
                
                for event in py.event.get():
                    if event.type == py.QUIT:
                        running = False
                        window.quit()
                    if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = event.pos
                        girl1_rect = py.Rect(x1, y1, dim, dim)
                        girl2_rect = py.Rect(x2, y2, dim, dim)
                        if suono_sparo:
                            suono_sparo.play()
                        
                        if girl1_rect.collidepoint(mouse_pos) and dead1 == False:
                            current1 = girls_D[ind]
                            dead1 = True
                        
                        if girl2_rect.collidepoint(mouse_pos) and dead2 == False:
                            current2 = girls_D[ind2]
                            dead2 = True
                        
                        current_gun = gunfire_pygame
                    else:
                        # Variabile per tracciare lo stato della pistola
                        current_gun = gun_pygame
                        
                    
                screen.blit(background_snapshot, (0, 0))
                screen.blit(pil_to_pygame(current1), (x1, y1))
                screen.blit(pil_to_pygame(current2), (x2, y2))
                
                # PISTOLA ANCHE QUI
                # PISTOLA - mirino a x=512, y=92
                mouse_x, mouse_y = py.mouse.get_pos()
                gun_x = mouse_x - 512
                gun_y = mouse_y - 92
                screen.blit(current_gun, (gun_x, gun_y))

                if dead1 == True: 
                    y1 += 10
                else:
                    y1 += 1

                if dead2 == True:
                    x2 -= 10
                else:
                    x2 -= 1
                
                py.display.flip()
                clock.tick(60)
            
            # FASE 2: MIRA
            if dead1 == False:
                current1 = girls_M[ind]
            if dead2 == False:
                current2 = girls_M[ind2]
            
            if dead1 == False or dead2 == False:
                for _ in range(60):
                    for event in py.event.get():
                        if event.type == py.QUIT:
                            running = False
                            window.quit()
                        if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = event.pos
                            girl1_rect = py.Rect(x1, y1, dim, dim)
                            girl2_rect = py.Rect(x2, y2, dim, dim)
                            
                            if girl1_rect.collidepoint(mouse_pos) and dead1 == False:
                                current1 = girls_D[ind]
                                dead1 = True
                            
                            if girl2_rect.collidepoint(mouse_pos) and dead2 == False:
                                current2 = girls_D[ind2]
                                dead2 = True
                            
                            current_gun = gunfire_pygame
                            gun_flash_timer = 5
                    
                    screen.blit(background_snapshot, (0, 0))
                    screen.blit(pil_to_pygame(current1), (x1, y1))
                    screen.blit(pil_to_pygame(current2), (x2, y2))
                    
                    # PISTOLA ANCHE QUI
                    # PISTOLA - mirino a x=512, y=92
                    mouse_x, mouse_y = py.mouse.get_pos()
                    gun_x = mouse_x - 512
                    gun_y = mouse_y - 92
                    screen.blit(current_gun, (gun_x, gun_y))
                    
                    py.display.flip()
                    clock.tick(60)
            
            # FASE 3: SPARO
            if dead1 == False:
                current1 = girls_S[ind]
            if dead2 == False:
                current2 = girls_S[ind2]
            
            if dead1 == False or dead2 == False:
                for _ in range(60):
                    for event in py.event.get():
                        if event.type == py.QUIT:
                            running = False
                            window.quit()
                        if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = event.pos
                            girl1_rect = py.Rect(x1, y1, dim, dim)
                            girl2_rect = py.Rect(x2, y2, dim, dim)
                            
                            if girl1_rect.collidepoint(mouse_pos) and dead1 == False:
                                current1 = girls_D[ind]
                                dead1 = True
                            
                            if girl2_rect.collidepoint(mouse_pos) and dead2 == False:
                                current2 = girls_D[ind2]
                                dead2 = True
                            
                            current_gun = gunfire_pygame
                           
                    
                    screen.blit(background_snapshot, (0, 0))
                    screen.blit(pil_to_pygame(current1), (x1, y1))
                    screen.blit(pil_to_pygame(current2), (x2, y2))
                    
                    # PISTOLA ANCHE QUI
                    # PISTOLA - mirino a x=512, y=92
                    mouse_x, mouse_y = py.mouse.get_pos()
                    gun_x = mouse_x - 512
                    gun_y = mouse_y - 92
                    screen.blit(current_gun, (gun_x, gun_y))
                    
                    py.display.flip()
                    clock.tick(60)
            
            if dead1 == False or dead2 == False:
                vita_player -= 2

            if y1 >= screen.get_height() or x2 <= 0:
                select = False
                dead1 = False
                dead2 = False
                countg += 1

        # Game Over
        if sete == 100 or fame == 100 or vita_player==0:
            if sete == 100 or fame == 100:
                vita_girl = 0
            game_over_font = py.font.Font(None, 100)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            
            instruction_font = py.font.Font(None, 36)
            instruction_text = instruction_font.render("Premi un tasto per tornare al menu", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 80))
            
            overlay = py.Surface((1024, 1024))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            screen.blit(game_over_text, game_over_rect)
            screen.blit(instruction_text, instruction_rect)
            
            py.display.flip()
            
            waiting = True
            while waiting:
                for event in py.event.get():
                    if event.type == py.QUIT:
                        waiting = False
                        running = False
                        py.quit()
                        sys.exit()
                        
                    if event.type == py.KEYDOWN or event.type == py.MOUSEBUTTONDOWN:
                        waiting = False
                        running = False
                        py.quit()
                        os.system("python character.py")
                        
                        try:
                            window.destroy()
                        except:
                            pass
                        
                        sys.exit()
        # QUANDO L'ATTACCO FINISCE, TORNA ALLA MUSICA NORMALE
        if attaco == False and musica_attacco_attiva == True:
            try:
                py.mixer.music.load(musica_normale)
                py.mixer.music.set_volume(50)
                py.mixer.music.play(-1)
                musica_attacco_attiva = False
            except:
                pass
        
        # PISTOLA NEL LOOP PRINCIPALE - SOLO SE ATTACCO E FUORI DALLE ANIMAZIONI
        if attaco == True:
            # PISTOLA - mirino a x=512, y=92
            mouse_x, mouse_y = py.mouse.get_pos()
            gun_x = mouse_x - 512
            gun_y = mouse_y - 92
            screen.blit(current_gun, (gun_x, gun_y))
        
        py.display.flip()
        clock.tick(60)

def on_closing():
    """Gestisce la chiusura della finestra Tkinter"""
    global running
    global fame, sete, last_fame_update, last_sete_update
    global frame_count, vita_girl, vita_player
    global contaTDattaco, countg, Nome
    global record, count_cum, sega_frame_count
    
    try:
        # Save - APRI IN MODALITÀ SCRITTURA 'w'
        with open(f"{Nome}_save.txt", 'w') as f:
            f.write(f"fame:{fame}\n")
            f.write(f"sete:{sete}\n")
            f.write(f"last_fame_update:{last_fame_update}\n")
            f.write(f"last_sete_update:{last_sete_update}\n")
            f.write(f"frame_count:{frame_count}\n")
            f.write(f"vita_girl:{vita_girl}\n")
            f.write(f"vita_player:{vita_player}\n")
            f.write(f"contaTDattaco:{contaTDattaco}\n")
            f.write(f"countg:{countg}\n")
            
            # ========== SALVA IL RECORD ==========
            if record is not None:
                record_secondi, record_cum = record
                f.write(f"record_secondi:{record_secondi}\n")
                f.write(f"record_cum:{record_cum}\n")
            else:
                f.write(f"record_secondi:0\n")
                f.write(f"record_cum:0\n")
            # =====================================
        
        print("Salvataggio completato")
    except Exception as e:
        print(f"Errore durante il salvataggio: {e}")
    
    running = False  # Ferma il loop Pygame
    
    # ========== CHIUSURA FORZATA PYGAME ==========
    try:
        import pygame as py
        py.mixer.music.stop()
        py.mixer.quit()
        py.display.quit()
        py.quit()
        print("Pygame chiuso correttamente")
    except Exception as e:
        print(f"Errore chiusura Pygame: {e}")
    # =============================================
    
    # Chiudi Tkinter
    try:
        window.quit()
        window.destroy()
        print("Tkinter chiuso correttamente")
    except Exception as e:
        print(f"Errore chiusura Tkinter: {e}")
    
    # ========== KILL FORZATO PROCESSI PYTHON ==========
    import sys
    import os
    
    try:
        # Usa psutil per killare i processi python
        import psutil
        current_process = psutil.Process(os.getpid())
        
        # Killa tutti i processi figli
        children = current_process.children(recursive=True)
        for child in children:
            print(f"Killing child process: {child.pid}")
            child.kill()
        
        # Killa il processo corrente
        print(f"Killing current process: {current_process.pid}")
        current_process.kill()
        
    except ImportError:
        print("psutil non installato, uso metodo alternativo")
        # Metodo alternativo senza psutil
        import subprocess
        if os.name == 'nt':  # Windows
            subprocess.call(['taskkill', '/F', '/PID', str(os.getpid())])
        else:  # Linux/Mac
            os.kill(os.getpid(), 9)
    except Exception as e:
        print(f"Errore durante il kill: {e}")
        # Ultima risorsa: exit forzato
        os._exit(0)
    # ==================================================
    
    sys.exit(0)


# Crea finestra Tkinter per i controlli
from tkinterdnd2 import DND_FILES, TkinterDnD

# Crea finestra Tkinter con supporto drag and drop
window = TkinterDnD.Tk()
window.title("Game Life - Controls")
window.geometry('800x800')
window.resizable(False, False)

# Gestisci l'evento di chiusura
window.protocol("WM_DELETE_WINDOW", on_closing)

# Frame per i controlli (per quando aggiungerai i bottoni)
frame_controls = tk.Frame(window)
frame_controls.pack(pady=20)

import webbrowser
import shutil
import time
import os

 

import os
import glob # Utile per la ricerca di file

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk



def get_most_recent_generated_image(path_download):
    """
    Trova l'immagine 'Generated Image' più recente nella cartella download.
    Cerca file .png, e se il nome del file suggerisce la ricerca di 'Generated Image',
    puoi aggiungere una condizione sul nome. L'implementazione qui sotto
    trova il .png più recente.
    """
    
    # 1. Trova tutti i file .png nella cartella di download
    # Per includere solo quelli che iniziano con "Generated Image" (se necessario):
    # list_of_files = glob.glob(os.path.join(path_download, 'Generated Image*.png'))
    
    # Versione che trova il .png più recente, come da logica originale:
    list_of_files = [
        os.path.join(path_download, f) 
        for f in os.listdir(path_download) 
        if f.endswith('.png') # Errore corretto: da 'endwish' a 'endswith'
    ]
    
    if not list_of_files:
        return None
    
    # 2. Trova il file più recente utilizzando la funzione 'max'
    # La chiave (key) per la comparazione è il tempo di modifica del file (os.path.getmtime)
    most_recent_file = max(list_of_files, key=os.path.getmtime)
    
    # 3. Ritorna solo il nome del file (non il percorso completo)
    return os.path.basename(most_recent_file)

def f_Reve():
    global current_image,azione,compi_azione,cibo, bevanda,stampa_parametri,Nome,fase_dorme1,fase_dorme2
    stampa_parametri=False
    path_download = r"C:\Users\User\Downloads"
    
    # Trova l'immagine più recente prima di aprire il browser
    recente = get_most_recent_generated_image(path_download)
    print(f"Immagine più recente prima: {recente}")
    
    # Apri NanoBanana
    webbrowser.open("https://app.reve.com/home")
    
    print("Attendo nuova immagine generata...")
    
    # Monitora la cartella per nuove immagini
    while True:
        time.sleep(2)  # Controlla ogni 2 secondi
        
        new_recente = get_most_recent_generated_image(path_download)
        
        # Se c'è una nuova immagine (diversa dalla precedente)
        if new_recente and new_recente != recente:
            print(f"Nuova immagine trovata: {new_recente}")
            
            # Percorso completo del file scaricato
            source_path = os.path.join(path_download, new_recente)
            
            # Aspetta che il file sia completamente scaricato
            time.sleep(1)
            
            try:
                # Rimuovi la vecchia immagine
                if os.path.exists(f"{Nome}_photogamer.png"):
                    os.remove(f"{Nome}_photogamer.png")
                
                # Copia la nuova immagine
                shutil.copyfile(source_path, f"{Nome}_photogamer.png")
                print("Immagine copiata con successo!")
                
                # Carica la nuova immagine in Pygame
                pil_image = Image.open(f"{Nome}_photogamer.png").convert("RGB")
                
                # Ridimensiona proporzionalmente
                original_width, original_height = pil_image.size
                scale = min(1024 / original_width, 1024 / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                pil_image_resized = pil_image.resize((new_width, new_height), Image.LANCZOS)
                
                # Crea canvas nero e centra l'immagine
                canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
                x_offset = (1024 - new_width) // 2
                y_offset = (1024 - new_height) // 2
                canvas.paste(pil_image_resized, (x_offset, y_offset))
                
                mode = canvas.mode
                size = canvas.size
                data = canvas.tobytes()
                
                current_image = py.image.fromstring(data, size, mode)
                print("Immagine aggiornata nello schermo!")
                compi_azione.config(state='normal')
                azione.config(state='readonly')  # o 'normal' se vuoi permettere input manuale
                if cibo==1:
                    cibo=2
                if bevanda==1:
                    bevanda=2
                stampa_parametri=True
                if fase_dorme1==True:
                    fase_dorme2=True
                    print(f"fase 2 {fase_dorme2}")
                
                break
                
            except Exception as e:
                print(f"Errore durante la copia dell'immagine: {e}")
                continue
        
def f_Nano():
    global current_image, azione, compi_azione, cibo, bevanda, stampa_parametri, Nome
    stampa_parametri = False
    
    # ATTENZIONE: Questo percorso è specifico per Windows. 
    # Assicurati che il percorso sia corretto e accessibile in esecuzione.
    path_download = r"C:\Users\User\Downloads"
    
    # 1. Trova l'immagine più recente prima di aprire il browser
    try:
        recente = get_most_recent_generated_image(path_download)
        print(f"Immagine più recente prima: {recente}")
    except FileNotFoundError:
        print(f"Errore: Cartella di download non trovata o inaccessibile: {path_download}")
        return

    # 2. Apri NanoBanana (l'URL è solo un esempio)
    print("Apertura del servizio di generazione immagini Nano...")
    webbrowser.open("https://aistudio.google.com/prompts/new_chat")
    
    print("Attendo nuova immagine generata...")
    
    # 3. Monitora la cartella per nuove immagini
    while True:
        time.sleep(2)  # Controlla ogni 2 secondi
        
        new_recente = get_most_recent_generated_image(path_download)
        
        # Se c'è una nuova immagine (diversa dalla precedente)
        if new_recente and new_recente != recente:
            print(f"Nuova immagine trovata: {new_recente}")
            
            # Percorso completo del file scaricato
            source_path = os.path.join(path_download, new_recente)
            
            # Aspetta un po' per assicurarsi che il download sia completo
            time.sleep(3) # Aumentato a 3 secondi per maggiore sicurezza nel download
            
            try:
                # 4. Rimuovi la vecchia immagine (se esiste) e copia la nuova
                destination_path = f"{Nome}_photogamer.png"
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                
                shutil.copyfile(source_path, destination_path)
                print("Immagine copiata con successo!")
                
                # 5. Carica la nuova immagine e la prepara per Pygame
                pil_image = Image.open(destination_path).convert("RGB")
                
                # Ridimensiona proporzionalmente a 1024x1024 (mantenendo l'aspetto)
                original_width, original_height = pil_image.size
                target_size = 1024
                scale = min(target_size / original_width, target_size / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                pil_image_resized = pil_image.resize((new_width, new_height), Image.LANCZOS)
                
                # Crea canvas nero e centra l'immagine
                canvas = Image.new('RGB', (target_size, target_size), (0, 0, 0))
                x_offset = (target_size - new_width) // 2
                y_offset = (target_size - new_height) // 2
                canvas.paste(pil_image_resized, (x_offset, y_offset))
                
                # 6. Aggiorna l'immagine di Pygame
                mode = canvas.mode
                size = canvas.size
                data = canvas.tobytes()
                
                current_image = py.image.fromstring(data, size, mode)
                print("Immagine aggiornata nello schermo!")
                
                # 7. Aggiorna lo stato del gioco/UI
                compi_azione.config(state='normal')
                azione.config(state='readonly')
                
                # Aggiornamento stato oggetti (cibo e bevanda)
                if cibo == 1:
                    cibo = 2
                if bevanda == 1:
                    bevanda = 2
                stampa_parametri = True
                if fase_dorme1==True:
                    fase_dorme2=True
                    print(f"fase 2 {fase_dorme2}")
                
                break # Esce dal ciclo while True
                
            except Exception as e:
                print(f"Errore durante la copia o l'elaborazione dell'immagine: {e}")
                # Potrebbe essere che il file è ancora in uso/incompleto, prova ancora al prossimo ciclo
                time.sleep(1)
                continue


# --- DEFINIZIONI BOTTONI CORRETTE ---

# Carica e prepara il logo per il bottone Reve (Assumiamo che Reve sia un altro modello o un'altra azione)
# Se 'reve.png' e 'logoN.png' non esistono, il blocco 'try' fallirà e verrà usato il fallback testuale.
try:
    # --- BOTTONE REVE ---
    logo_reve = Image.open("reve.png").convert("RGBA")  # Mantieni la trasparenza
    logo_reve = logo_reve.resize((100, 50), Image.LANCZOS)
    logo_reve_tk = ImageTk.PhotoImage(logo_reve)
    
    Reve = tk.Button(
        frame_controls, 
        image=logo_reve_tk,
        bg="LightSkyBlue", 
        activebackground="DeepSkyBlue", # Colore standard
        # NOTA BENE: Questo bottone chiama f_Reve. Se non esiste, devi definirla.
        # Ho mantenuto f_Reve nel command come nell'originale, ma devi verificarlo.
        command=lambda: threading.Thread(target=f_Reve, daemon=True).start(), 
        borderwidth=2,  
        relief="raised",  
        highlightthickness=0
    )
    Reve.image = logo_reve_tk  
    Reve.grid(row=0, column=0, padx=5, pady=5)
    
except FileNotFoundError:
    print("Logo reve.png non trovato, uso bottone testuale 'REVE'")
    # Fallback: bottone testuale se il logo non esiste
    Reve = tk.Button(
        frame_controls, 
        text="REVE",
        bg="LightSkyBlue", 
        activebackground="DeepSkyBlue", 
        command=lambda: threading.Thread(target=f_Reve, daemon=True).start()
    )
    Reve.grid(row=0, column=0, padx=5, pady=5)


# Carica e prepara il logo per il bottone Nano (NanoBanana)
try:
    # --- BOTTONE NANO (NANO BANANA) ---
    logo_nano2 = Image.open("logoN.png").convert("RGBA")  # Mantieni la trasparenza
    logo_nano2 = logo_nano2.resize((100, 50), Image.LANCZOS)
    logo_nano_tk2 = ImageTk.PhotoImage(logo_nano2)
    
    Nano = tk.Button(
        frame_controls, 
        image=logo_nano_tk2,
        bg="LightYellow", 
        activebackground="gold", # Corretto da "Deepyellow" a "gold" (colore standard Tkinter)
        
        # *** CORREZIONE CRITICA: CHIAMARE f_Nano ***
        command=lambda: threading.Thread(target=f_Nano, daemon=True).start(),
        
        borderwidth=2,  
        relief="raised", 
        highlightthickness=0
    )
    Nano.image = logo_nano_tk2  
    Nano.grid(row=0, column=1, padx=5, pady=5)
    
except FileNotFoundError:
    print("Logo logoN.png non trovato, uso bottone testuale 'Nano Banana'")
    # Fallback: bottone testuale se il logo non esiste
    Nano = tk.Button(
        frame_controls, 
        text="Nano Banana",
        bg="LightYellow", 
        activebackground="gold", # Corretto da "Deepyellow"
        
        # *** CORREZIONE CRITICA: CHIAMARE f_Nano ***
        command=lambda: threading.Thread(target=f_Nano, daemon=True).start()
    )
    # NOTA: La colonna per Nano era 0 nel codice originale del fallback, l'ho corretta a 1
    Nano.grid(row=0, column=1, padx=5, pady=5)
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os


def f_costum_character():
    global Nome, screen, current_image, is_generating
    
    # 1. Apre il dialogo file
    filepathfull = filedialog.askopenfilename(
        title="Seleziona immagine",
        filetypes=[("Immagini", "*.png;*.jpg;*.jpeg")]
    )
    
    # 2. CONTROLLO DI SICUREZZA: Se l'utente preme annulla, usciamo dalla funzione
    if not filepathfull:
        return 

    try:
        image = Image.open(filepathfull)
        w, h = image.size
        
        # 3. Logica di ridimensionamento (Corretta!)
        if w >= h:
            wr = 1024
            hr = (1024 * h) // w
        else:
            wr = (1024 * w) // h
            hr = 1024
        
        # Ridimensiona l'immagine con le nuove dimensioni calcolate
        image = image.resize((wr, hr), Image.BICUBIC)
        
        # Backup dell'immagine precedente se esiste
        if os.path.exists(f"{Nome}_photogamer.png"):
            if os.path.exists(f"{Nome}_photogamer_copy.png"):
                os.remove(f"{Nome}_photogamer_copy.png")
            shutil.copy(f"{Nome}_photogamer.png", f"{Nome}_photogamer_copy.png")
        
        # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
        canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
        x_offset = (1024 - wr) // 2  # Usa wr invece di new_width
        y_offset = (1024 - hr) // 2  # Usa hr invece di new_height
        canvas.paste(image, (x_offset, y_offset))
        
        # Salva l'immagine
        canvas.save(f"{Nome}_photogamer.png")
        print(f"Immagine salvata come {Nome}_photogamer.png")
        
        # Converti PIL Image in Pygame Surface
        mode = canvas.mode
        size = canvas.size
        data = canvas.tobytes()

        # Crea surface Pygame dall'immagine
        pygame_image = py.image.fromstring(data, size, mode)
        current_image = pygame_image
        
        is_generating = False
        
    except Exception as e:
        print(f"Errore durante l'elaborazione dell'immagine: {e}")

# Definizione del bottone corretta
custom_character = tk.Button(
    frame_controls, 
    text="Custom Character", 
    bg='#8B4513',
    fg='white',
    command=f_costum_character
)
custom_character.grid(row=0, column=2)





# Dizionari con descrizioni dettagliate
cibi_dict = {
    "Pizza Margherita": "a delicious italian margherita pizza with tomato sauce, mozzarella cheese and fresh basil leaves",
    "Sushi": "fresh sushi platter with nigiri, maki rolls and sashimi, beautifully arranged",
    "Pasta Carbonara": "creamy carbonara pasta with guanciale, egg yolk, pecorino cheese and black pepper",
    "Hamburger": "juicy gourmet burger with beef patty, lettuce, tomato, cheese and special sauce",
    "Insalata": "fresh colorful salad with mixed greens, cherry tomatoes, cucumbers and olive oil"
}

bevande_dict = {
    "Caffè Espresso": "a perfect italian espresso coffee in a small white cup with crema on top",
    "Cappuccino": "creamy cappuccino with milk foam art in a ceramic cup",
    "Succo d'Arancia": "fresh squeezed orange juice in a tall glass with ice and orange slice",
    "Vino Rosso": "glass of red wine with a wine bottle in the background, elegant setting",
    "Cocktail Mojito": "refreshing mojito cocktail with mint leaves, lime, ice and rum in a highball glass",
    "Bicchiere d'Acqua": "clear glass of fresh water with ice cubes and water droplets on the outside",
    "Acqua Minerale": "bottle of sparkling mineral water next to a glass filled with bubbling water and ice"
}

outfit_dict = {
    "Casual Estivo": "clothing flat lay, light blue jeans, white t-shirt and sneakers neatly arranged on solid turquoise background, no person, studio photography",
    "Elegante Sera": "clothing flat lay, black suit, white shirt and leather shoes neatly arranged on solid burgundy background, no person, studio photography",
    "Sportivo": "clothing flat lay, training jacket, running pants and sport shoes neatly arranged on solid lime green background, no person, studio photography",
    "Business": "clothing flat lay, grey suit, tie and dress shoes neatly arranged on solid navy blue background, no person, studio photography",
    "Bohemien": "clothing flat lay, flowy dress, sandals and accessories neatly arranged on solid coral background, no person, studio photography",
    "Pantaloncini Corti e Top": "clothing flat lay, denim shorts, casual crop top and canvas shoes neatly arranged on solid yellow background, no person, studio photography",
    "Pantaloncini Scosciati con Canotta": "clothing flat lay, high-cut shorts, belly-showing tank top and flip-flops neatly arranged on solid pink background, no person, studio photography"
}

arredi_dict = {
    "WC/Water Inox": "Stainless steel prison toilet and sink combo unit bolted to a gray concrete wall, stark institutional lighting, close-up, no person, high detail",
    "Letto Singolo da Cella": "Simple metal-frame single cot bed with a thin, folded gray blanket and a worn pillow in a concrete cell corner, sparse lighting, no person",
    "Sedia in Metallo": "A single, slightly rusted metal folding chair sitting on a cracked tiled floor, strong shadows, industrial style, isolated object, no person",
    "Tavolo Pieghevole": "Small, worn wooden folding table against a bare wall, suitable for dining or writing, realistic cell lighting, no person",
    "Scrivania Ufficio": "Clean modern white office desk with a laptop and a single potted plant, minimalistic professional setting, isolated furniture, no person",
    "Divano": "Comfortable, deep blue velvet sofa with decorative throw pillows in a cozy living room setting, ambient light, high quality photo, no person",
    "Vasca da Bagno Vintage": "Elegant vintage clawfoot bathtub with chrome fixtures in a bright, tiled bathroom, soap dish visible, clean and isolated, no person"
}

def genera(p, out):
    global visual_cibi, visual_bevande, visual_outfit, visual_prompt, text, combocibi, combobevande, combooutfit, compi_azione, cibo, bevanda, stampa_parametri
    # NUOVI GLOBALI: Aggiunti visual_arredi e comboarredi
    global visual_arredi, comboarredi 
    global prompt_it, prompt_en
    stampa_parametri = False
    print("genera ")
    
    # Se p è vuoto, non fare nulla
    if not p or p.strip() == "":
        print("Prompt vuoto, operazione annullata")
        return
        
    p_translated = G(source='it', target='en').translate(p)
    path_model = "Model/realisticVisionV60B1_v51VAE.ckpt"
    pipe = StableDiffusionPipeline.from_single_file(path_model, torch_dtype=torch.bfloat16)
    pipe.to('cuda')
    image = pipe(prompt=p_translated, num_inference_steps=50, guidance_scale=7.5).images[0]
    image.save(out)
    image_resize = image.resize((150, 150), Image.BICUBIC)
    
    # Converti l'immagine PIL in PhotoImage per tkinter
    photo = ImageTk.PhotoImage(image_resize)
    
    text_content = text.get('1.0', tk.END).strip()
    
    # --- LOGICA CIBO ---
    if out == "cibo.png":
        cibo=1
        visual_cibi.create_image(0, 0, image=photo, anchor='nw')
        visual_cibi.image = photo
        
        if text_content == '':
            prompt_it = f'una ragazza che mangia un {combocibi.get()} in prigione'
        else:
            prompt_it = f'una ragazza che mangia un {text_content} in prigione'
            
        compi_azione.config(text="Azione: Mangia")
            
    # --- LOGICA BEVANDA ---
    elif out == "bevanda.png":
        bevanda=1
        visual_bevande.create_image(0, 0, image=photo, anchor='nw')
        visual_bevande.image = photo
        
        if text_content == '':
            prompt_it = f'una ragazza che beve un {combobevande.get()} in prigione'
        else:
            prompt_it = f'una ragazza che beve un {text_content} in prigione'
            
        compi_azione.config(text="Azione: Beve")
            
    # --- LOGICA OUTFIT ---
    elif out == "outfit.png":
        visual_outfit.create_image(0, 0, image=photo, anchor='nw')
        visual_outfit.image = photo
        
        if text_content == '':
            prompt_it = f'una ragazza che indossa un {combooutfit.get()} in prigione'
        else:
            prompt_it = f'una ragazza che indossa un {text_content} in prigione'
            
        compi_azione.config(text="Azione: Veste") # Aggiungo azione mancante
            
    # --- LOGICA ARREDO (OGGETTI) - NUOVO BLOCCO ---
    elif out == "arredo.png":
        # Aggiorna il canvas corretto
        visual_arredi.create_image(0, 0, image=photo, anchor='nw')
        visual_arredi.image = photo
        
        if text_content == '':
            # Seleziona l'elemento dalla combobox arredi
            arredo_selezionato = comboarredi.get()
            # Prompt per un'azione generica di interazione
            prompt_it = f'una ragazza che interagisce con un {arredo_selezionato} in una cella di prigione'
        else:
            # Usa il testo personalizzato
            prompt_it = f'una ragazza che interagisce con un {text_content} in una cella di prigione'
            
        compi_azione.config(text="Azione: Interagisce")

    # --- AGGIORNAMENTO PROMPT FINALE (ESECUTO SOLO SE IL PROMPT_IT E' DEFINITO) ---
    # Questa sezione viene spostata qui, dopo che prompt_it è stato definito in uno dei blocchi precedenti.
    if 'prompt_it' in locals() or 'prompt_it' in globals():
        prompt_en = G(source='it', target='en').translate(prompt_it)
        
        visual_prompt.config(state='normal')  # ABILITA
        visual_prompt.delete('1.0', tk.END)
        visual_prompt.insert('1.0', f'ITA: {prompt_it} | ENG: {prompt_en}')
        visual_prompt.config(state='disabled') # DISABILITA
        
        print(f'ITA: {prompt_it} | ENG: {prompt_en}')
        stampa_parametri = True
    else:
        # Questo caso non dovrebbe più verificarsi se l'argomento 'out' è valido
        print("Errore: Impossibile generare i prompt ITA/ENG. Tipo di output non riconosciuto.")


def on_cibo_select(event):
    """Gestisce la selezione di un cibo dalla combobox"""
    selected = combocibi.get()
    if selected in cibi_dict:
        prompt = cibi_dict[selected]
        # Se text è vuota, usa la descrizione del dizionario
        text_content = text.get('1.0', tk.END).strip()
        if not text_content:
            genera(prompt, "cibo.png")
        else:
            genera(text_content, "cibo.png")

def on_bevanda_select(event):
    """Gestisce la selezione di una bevanda dalla combobox"""
    selected = combobevande.get()
    if selected in bevande_dict:
        prompt = bevande_dict[selected]
        text_content = text.get('1.0', tk.END).strip()
        if not text_content:
            genera(prompt, "bevanda.png")
        else:
            genera(text_content, "bevanda.png")

def on_outfit_select(event):
    """Gestisce la selezione di un outfit dalla combobox"""
    selected = combooutfit.get()
    if selected in outfit_dict:
        prompt = outfit_dict[selected]
        text_content = text.get('1.0', tk.END).strip()
        if not text_content:
            genera(prompt, "outfit.png")
        else:
            # Aggiungi il formato flat lay al testo personalizzato
            custom_prompt = f"flat lay of {text_content}, arranged on vibrant colorful background, no people, product photography style"
            genera(custom_prompt, "outfit.png")
    
def on_arredo_select(event):
    global fase_dorme1
    """Gestisce la selezione di un arredo dalla combobox"""
    selected = comboarredi.get()
    if selected=="Letto Singolo da Cella":
        fase_dorme1=True
        print(f"Fase 1: {fase_dorme1}")
    # Usa il nuovo dizionario 'arredi_dict'
    if selected in arredi_dict:
        prompt = arredi_dict[selected]
        text_content = text.get('1.0', tk.END).strip()
        if not text_content:
            genera(prompt, "arredo.png") # Nome file generato per l'arredo
        else:
            # Gli arredi sono spesso oggetti isolati, quindi usiamo un prompt generico
            custom_prompt = f"realistic photo of a single {text_content}, isolated object, high detail, no people"
            genera(custom_prompt, "arredo.png")


# CIBI
visual_cibi = tk.Canvas(frame_controls, bg='pink', width=150, height=150)
visual_cibi.grid(row=1, column=0, padx=5, pady=5)

genera_cibo = tk.Button(frame_controls, text='Genera Cibo', 
                        command=lambda: genera(text.get('1.0', tk.END).strip(), "cibo.png"))
genera_cibo.grid(row=2, column=0, padx=5, pady=5)

combocibi = ttk.Combobox(frame_controls, values=list(cibi_dict.keys()), state='readonly', width=18)
combocibi.grid(row=3, column=0, padx=5, pady=5)
combocibi.bind('<<ComboboxSelected>>', on_cibo_select)

# BEVANDE
visual_bevande = tk.Canvas(frame_controls, bg='pink', width=150, height=150)
visual_bevande.grid(row=1, column=1, padx=5, pady=5)

genera_bevande = tk.Button(frame_controls, text='Genera Bevanda', 
                           command=lambda: genera(text.get('1.0', tk.END).strip(), "bevanda.png"))
genera_bevande.grid(row=2, column=1, padx=5, pady=5)

combobevande = ttk.Combobox(frame_controls, values=list(bevande_dict.keys()), state='readonly', width=18)
combobevande.grid(row=3, column=1, padx=5, pady=5)
combobevande.bind('<<ComboboxSelected>>', on_bevanda_select)

# OUTFIT
visual_outfit = tk.Canvas(frame_controls, bg='pink', width=150, height=150)
visual_outfit.grid(row=1, column=2, padx=5, pady=5)

genera_outfit = tk.Button(frame_controls, text='Genera Outfit', 
                          command=lambda: genera(text.get('1.0', tk.END).strip(), "outfit.png"))
genera_outfit.grid(row=2, column=2, padx=5, pady=5)

combooutfit = ttk.Combobox(frame_controls, values=list(outfit_dict.keys()), state='readonly', width=18)
combooutfit.grid(row=3, column=2, padx=5, pady=5)
combooutfit.bind('<<ComboboxSelected>>', on_outfit_select)

# OGGETTI / ARREDI (NUOVA SEZIONE)
visual_arredi = tk.Canvas(frame_controls, bg='pink', width=150, height=150)
visual_arredi.grid(row=1, column=3, padx=5, pady=5)

genera_arredi = tk.Button(frame_controls, text='Genera Arredo', # Ho cambiato il testo del pulsante
                         command=lambda: genera(text.get('1.0', tk.END).strip(), "arredo.png"))
genera_arredi.grid(row=2, column=3, padx=5, pady=5)

comboarredi = ttk.Combobox(frame_controls, values=list(arredi_dict.keys()), state='readonly', width=18) # Ho cambiato il nome della combobox e ho usato il nuovo dizionario
comboarredi.grid(row=3, column=3, padx=5, pady=5)
comboarredi.bind('<<ComboboxSelected>>', on_arredo_select) # Ho collegato la nuova funzione

# TEXT AREA
text = tk.Text(frame_controls, width=25, height=5)
text.grid(row=4, column=1, padx=5, pady=10)

def concatenate_images(images, direction="horizontal"):
    """
    Concatena multiple immagini PIL orizzontalmente o verticalmente.
    """
    if not images:
        return None
    
    # Filtra immagini None
    valid_images = [img for img in images if img is not None]
    
    if not valid_images:
        return None
    
    if len(valid_images) == 1:
        return valid_images[0].convert("RGB")
    
    # Converti tutte le immagini in RGB
    valid_images = [img.convert("RGB") for img in valid_images]
    
    if direction == "horizontal":
        # Calcola larghezza totale e altezza massima
        total_width = sum(img.width for img in valid_images)
        max_height = max(img.height for img in valid_images)
        
        # Crea nuova immagine
        concatenated = Image.new('RGB', (total_width, max_height), (255, 255, 255))
        
        # Incolla le immagini
        x_offset = 0
        for img in valid_images:
            # Centra l'immagine verticalmente se le altezze differiscono
            y_offset = (max_height - img.height) // 2
            concatenated.paste(img, (x_offset, y_offset))
            x_offset += img.width
            
    else:  # vertical
        # Calcola larghezza massima e altezza totale
        max_width = max(img.width for img in valid_images)
        total_height = sum(img.height for img in valid_images)
        
        # Crea nuova immagine
        concatenated = Image.new('RGB', (max_width, total_height), (255, 255, 255))
        
        # Incolla le immagini
        y_offset = 0
        for img in valid_images:
            # Centra l'immagine orizzontalmente se le larghezze differiscono
            x_offset = (max_width - img.width) // 2
            concatenated.paste(img, (x_offset, y_offset))
            y_offset += img.height
    
    return concatenated

def Kontext(pf=[], p=''):
    global screen, current_image, is_generating,compi_azione,cibo,bevanda,stampa_parametri,Nome
    
    is_generating = True
    stampa_parametri=False
    
    print(f"uso KonText : path file: {pf}")
    bfl_repo = "black-forest-labs/FLUX.1-Kontext-dev"
    dtype = torch.bfloat16
    images = []
    
    # Carica le immagini
    for img_path in pf:
        img = Image.open(img_path).convert("RGB")
        images.append(img)
    
    print(f"Immagini caricate: {len(images)}")
    
    # Concatena le immagini orizzontalmente
    concatenated_image = concatenate_images(images, "horizontal")
    
    if concatenated_image is None:
        print("Errore: impossibile concatenare le immagini")
        is_generating = False
        return None
    
    print(f"Immagine concatenata - dimensioni: {concatenated_image.size}")
    
    # Carica e quantizza il transformer
    transformer = FluxTransformer2DModel.from_pretrained(
        bfl_repo, 
        subfolder='transformer', 
        torch_dtype=dtype
    )
    quantize(transformer, weights=qfloat8)
    freeze(transformer)
    
    # Carica e quantizza il text encoder
    text_encoder_2 = T5EncoderModel.from_pretrained(
        bfl_repo, 
        subfolder="text_encoder_2", 
        torch_dtype=dtype
    )
    quantize(text_encoder_2, weights=qfloat8)
    freeze(text_encoder_2)
    
    # Carica la pipeline
    pipe = FluxKontextPipeline.from_pretrained(
        bfl_repo,
        transformer=None, 
        text_encoder_2=None, 
        torch_dtype=torch.bfloat16
    )
    
    pipe.transformer = transformer
    pipe.text_encoder_2 = text_encoder_2
    pipe.to("cuda")
    pipe.enable_model_cpu_offload()

    # Traduci il prompt dall'italiano all'inglese
    try:
        translator = G(source='it', target='en')
        p_translated = translator.translate(p)
        print(f"Prompt tradotto: {p_translated}")
    except Exception as e:
        print(f"Errore nella traduzione, uso prompt originale: {e}")
        p_translated = p
    
    # Crea il prompt finale come nell'esempio
    final_prompt = f"From the provided reference images, create a unified, cohesive image such that {p_translated}. Maintain the identity and characteristics of each subject while adjusting their proportions, scale, and positioning to create a harmonious, naturally balanced composition. Blend and integrate all elements seamlessly with consistent lighting, perspective, and style. The final result should look like a single naturally captured scene where all subjects are properly sized and positioned relative to each other, not assembled from multiple sources."
    
    print(f"Prompt finale: {final_prompt}")
    
    # Genera l'immagine usando le dimensioni dell'immagine concatenata
    try:
        image = pipe(
            image=concatenated_image, 
            prompt=final_prompt,
            guidance_scale=3.5,
            #width=concatenated_image.size[0],
            #height=concatenated_image.size[1],
            width=1024,
            height=1024,
            generator=torch.Generator().manual_seed(42),
        ).images[0]
        
        image.save(f"{Nome}_photogamer.png")
        
        # Ridimensiona l'immagine proporzionalmente per adattarla a 1024x1024
        original_width, original_height = image.size

        # Calcola il rapporto di scala mantenendo le proporzioni
        scale = min(1024 / original_width, 1024 / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        # Ridimensiona l'immagine
        image_resized = image.resize((new_width, new_height), Image.LANCZOS)

        # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
        canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
        x_offset = (1024 - new_width) // 2
        y_offset = (1024 - new_height) // 2
        canvas.paste(image_resized, (x_offset, y_offset))

        # Converti PIL Image in Pygame Surface
        mode = canvas.mode
        size = canvas.size
        data = canvas.tobytes()

        # Crea surface Pygame dall'immagine
        pygame_image = py.image.fromstring(data, size, mode)
        current_image = pygame_image

        
        is_generating = False
        
        print("Immagine salvata e caricata con successo!")
        compi_azione.config(state='normal')
        azione.config(state='readonly')  # o 'normal' se vuoi permettere input manuale
        stampa_parametri=True
        if cibo==1:
            cibo=2
        if bevanda==1:
            bevanda=2
        return image
    except Exception as e:
        print(f"Errore durante la generazione: {e}")
        is_generating = False
        return None
# Text widget per renderlo selezionabile - PIÙ PICCOLO
visual_prompt = tk.Text(frame_controls, height=2, width=50, wrap='word', relief='flat', bg='#f0f0f0', font=('Arial', 8))
visual_prompt.grid(row=5, column=0, columnspan=3, padx=2, pady=5, sticky='ew')
visual_prompt.insert('1.0', 'Prompt: ')
visual_prompt.config(state='disabled')

# Bottone Mangia - PIÙ PICCOLO
Mangia = tk.Button(
    frame_controls,
    text="Mangia",
    width=12,
    command=lambda: Kontext(
        [f'{Nome}_photogamer.png', 'cibo.png'],
        f"Una Ragazza che mangia un {combocibi.get() if text.get('1.0', tk.END).strip() == '' else text.get('1.0', tk.END).strip()} in una prigione"
    )
)
Mangia.grid(row=6, column=0, padx=2, pady=2)

# Bottone Beve - PIÙ PICCOLO
Beve = tk.Button(
    frame_controls,
    text="Beve",
    width=12,
    command=lambda: Kontext(
        [f'{Nome}_photogamer.png', 'bevanda.png'],
        f"Una Ragazza che beve un {combobevande.get() if text.get('1.0', tk.END).strip() == '' else text.get('1.0', tk.END).strip()} in una prigione"
    )
)
Beve.grid(row=6, column=1, padx=2, pady=2)

# Bottone Cambia Outfit - PIÙ PICCOLO
cambia_outfit = tk.Button(
    frame_controls,
    text="Outfit",
    width=12,
    command=lambda: Kontext(
        [f'{Nome}_photogamer.png', 'outfit.png'],
        f"Una Ragazza che indossa un {combooutfit.get() if text.get('1.0', tk.END).strip() == '' else text.get('1.0', tk.END).strip()} in una prigione"
    )
)
cambia_outfit.grid(row=6, column=2, padx=2, pady=2)

import os
import shutil
import time
import glob
import subprocess


import threading

def f_azione():
   
    global azione, cibo, bevanda
    global fame, sete, last_fame_update, last_sete_update, frame_count, cibo, bevanda, fase_dorme2, fase_dorme3
    
    def play_video_with_vlc(video_path):
        global cibo, bevanda, fame, sete, last_fame_update, last_sete_update
        """Riproduce il video con VLC a schermo intero"""
        vlc_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\VLC\vlc.exe")
        ]
        
        vlc_path = None
        for path in vlc_paths:
            if os.path.exists(path):
                vlc_path = path
                break
        
        if vlc_path:
            print(f"Riproduzione con VLC: {video_path}")
            subprocess.Popen([vlc_path, '--fullscreen', '--play-and-exit', video_path])
            
            if cibo == 2:
                print("Reset FAME - Cibo consumato!")
                fame = 0
                last_fame_update = frame_count
                cibo = 0
            
            if bevanda == 2:
                print("Reset SETE - Bevanda consumata!")
                sete = 0
                last_sete_update = frame_count
                bevanda = 0
            
            return True
        else:
            print("VLC non trovato")
            return False
    
    def play_video_with_wmp(video_path):
        global cibo, bevanda, fame, sete, last_fame_update, last_sete_update
        """Riproduce il video con Windows Media Player"""
        print(f"Riproduzione con Windows Media Player: {video_path}")
        os.startfile(video_path)
        
        if cibo == 2:
            print("Reset FAME - Cibo consumato!")
            fame = 0
            last_fame_update = frame_count
            cibo = 0
        
        if bevanda == 2:
            print("Reset SETE - Bevanda consumata!")
            sete = 0
            last_sete_update = frame_count
            bevanda = 0

    def wait_and_process_video(initial_video, downloads_path):
        """Attende il download del nuovo video, lo sposta e lo riproduce"""
        global cibo, bevanda, fame, sete, last_fame_update, last_sete_update, frame_count, fase_dorme2, fase_dorme3
        
        print("Attendo nuovo video (attesa infinita)...")
        
        while True:
            video_files = glob.glob(os.path.join(downloads_path, '*.mp4'))
            
            if video_files:
                new_video_recente = max(video_files, key=os.path.getmtime)
                
                if new_video_recente != initial_video:
                    print(f"Nuovo video trovato: {new_video_recente}")
                    
                    file_size = -1
                    stable_count = 0
                    
                    while True:
                        time.sleep(2)
                        try:
                            new_size = os.path.getsize(new_video_recente)
                            if new_size == file_size:
                                stable_count += 1
                                if stable_count >= 3:
                                    print(f"Download completato: {new_size} bytes")
                                    break
                            else:
                                stable_count = 0
                                print(f"Download in corso... {new_size} bytes")
                            file_size = new_size
                        except OSError:
                            print("File temporaneamente inaccessibile, riprovo...")
                            time.sleep(1)
                    
                    try:
                        if os.path.exists('./Animazione.mp4'):
                            os.remove('./Animazione.mp4')
                        
                        shutil.move(new_video_recente, './Animazione.mp4')
                        print("Video spostato in ./Animazione.mp4")
                        
                        if not play_video_with_vlc('./Animazione.mp4'):
                            from tkinter import messagebox
                            risposta = messagebox.askyesno(
                                "VLC non trovato",
                                "VLC non è installato sul sistema.\n\n"
                                "Vuoi aprire il video con Windows Media Player?\n\n"
                                "(Consigliato: installa VLC per una migliore esperienza)"
                            )
                            
                            if risposta:
                                play_video_with_wmp('./Animazione.mp4')
                            else:
                                print("Riproduzione annullata dall'utente")
                        
                    except Exception as e:
                        print(f"Errore durante lo spostamento o riproduzione: {e}")
                    
                    # Disabilita i controlli dopo aver completato
                    compi_azione.config(state='disabled')
                    azione.config(state='disabled')
                    if fase_dorme2 == True:
                        fase_dorme3 = True
                        print(f"fase 3 {fase_dorme3}")
                    break
            
            time.sleep(5)
    
    # Funzione wrapper per eseguire in background
    def run_in_background(initial_video, downloads_path):
        wait_and_process_video(initial_video, downloads_path)
    
    if azione.get() in ['Meta.IA', 'Video NSFW', 'Prompt ASSIST']:
        downloads_path = r'C:\Users\User\Downloads'
        
        # Trova il video mp4 più recente prima di aprire il browser
        video_files = glob.glob(os.path.join(downloads_path, '*.mp4'))
        
        if video_files:
            video_recente = max(video_files, key=os.path.getmtime)
            print(f"Video più recente prima: {video_recente}")
        else:
            video_recente = None
            print("Nessun video trovato inizialmente")
        
        # Apri il browser appropriato
        import webbrowser
        if azione.get() == 'Meta.IA':
            webbrowser.open('https://www.meta.ai/media?locale=it_IT')
        elif azione.get() == 'Video NSFW':
            webbrowser.open('https://video.a2e.ai/image-to-video')
        elif azione.get() == 'Prompt ASSIST':
            webbrowser.open('https://vidfly.ai/apps/image-to-video/')
        
        # Avvia il thread in background per attendere il video
        thread = threading.Thread(
            target=run_in_background, 
            args=(video_recente, downloads_path),
            daemon=True  # Il thread termina quando il programma principale termina
        )
        thread.start()
        print("Thread avviato in background - GUI rimane responsive!")
  

compi_azione = tk.Button(frame_controls, text="Azione", command=f_azione, width=12, state='disabled')
compi_azione.grid(row=7, column=0, padx=2, pady=2)

azione = ttk.Combobox(frame_controls, values=['Meta.IA', 'Video NSFW','Prompt ASSIST'], width=12, state='disabled')
azione.grid(row=7, column=1, columnspan=2, padx=2, pady=2, sticky='w')
azione.set('Meta.IA')

temp_email = tk.Button(frame_controls, text="Email_temp", command=lambda: webbrowser.open("https://adguard.com/it/adguard-temp-mail/overview.html"), width=12)
temp_email.grid(row=7, column=2, padx=2, pady=2)

from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import requests
import matplotlib.pyplot as plt
import torch.nn as nn
import numpy as np
import cv2

from diffusers import StableDiffusionControlNetInpaintPipeline, ControlNetModel,DDIMScheduler
from diffusers.utils import load_image
import numpy as np
import torch

def f_rilevaVestiti():
    global Nome
    print("Detective outfit")
    
    processor = SegformerImageProcessor.from_pretrained("sayeed99/segformer_b3_clothes")
    model = AutoModelForSemanticSegmentation.from_pretrained("sayeed99/segformer_b3_clothes")
    path_image = f"{Nome}_photogamer.png"

    # Correzione: usa Image.open direttamente per file locali
    image = Image.open(path_image).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    outputs = model(**inputs)
    logits = outputs.logits.cpu()

    upsampled_logits = nn.functional.interpolate(
        logits,
        size=image.size[::-1],
        mode="bilinear",
        align_corners=False,
    )

    pred_seg = upsampled_logits.argmax(dim=1)[0]

    # Filtro per abbigliamento
    clothing_labels = {
        4: "Upper-clothes",  # Top/Maglietta
        5: "Skirt",          # Gonna
        6: "Pants",          # Pantaloni/Pantaloncini
        7: "Dress"           # Vestito
    }

    # Crea una maschera per i capi di abbigliamento
    clothing_mask = torch.zeros_like(pred_seg, dtype=torch.bool)
    for label_id in clothing_labels.keys():
        clothing_mask |= (pred_seg == label_id)

    # Converti in array numpy
    mask_array = clothing_mask.numpy().astype(np.uint8) * 255

    # 1. Riempi i buchi interni (zone nere dentro le zone bianche)
    contours, _ = cv2.findContours(mask_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_filled = np.zeros_like(mask_array)
    cv2.drawContours(mask_filled, contours, -1, 255, thickness=cv2.FILLED)

    # 2. Espandi le zone bianche di 10 pixel (dilatazione)
    kernel = np.ones((15, 15), np.uint8)  # 21x21 per espandere di ~10 pixel in tutte le direzioni
    mask_expanded = cv2.dilate(mask_filled, kernel, iterations=1)

    # Converti in immagine PIL
    mask_image = Image.fromarray(mask_expanded, mode='L')

    # Salva la maschera
    mask_image.save("clothing_mask.png")
    print("Maschera salvata come 'clothing_mask.png'")

    # Opzionale: mostra quali capi sono stati rilevati
    detected_clothes = []
    for label_id, label_name in clothing_labels.items():
        if (pred_seg == label_id).any():
            detected_clothes.append(label_name)

    print(f"Capi rilevati: {', '.join(detected_clothes)}")


Rileva_vestiti= tk.Button(frame_controls,text="rileva vestiti",command=f_rilevaVestiti)
Rileva_vestiti.grid(row=8,column=0)

import torch
from diffusers import FluxFillPipeline
from diffusers import FluxTransformer2DModel
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize

def F_Flux():
    global text, MODELS, screen, current_image, Nome, steps, cfg, lora, pathfileref
    print("Flux Fill")
    path_image = f"{Nome}_photogamer.png"
    # Correzione: usa Image.open direttamente per file locali
    image = Image.open(path_image).convert("RGB")
    mask = Image.open("clothing_mask.png").convert('L')

    bfl_repo = "black-forest-labs/FLUX.1-Fill-dev"
    dtype = torch.bfloat16

    transformer = FluxTransformer2DModel.from_single_file(f"Model//{MODELS.get()}.safetensors", torch_dtype=dtype)
    quantize(transformer, weights=qfloat8)
    freeze(transformer)

    text_encoder_2 = T5EncoderModel.from_pretrained(bfl_repo, subfolder="text_encoder_2", torch_dtype=dtype)
    quantize(text_encoder_2, weights=qfloat8)
    freeze(text_encoder_2)

    pipe = FluxFillPipeline.from_pretrained(bfl_repo, torch_dtype=torch.bfloat16)

    pipe.load_lora_weights(f"./Lora//{lora.get()}", adapter_name="lora1")
    pipe.set_adapters(["lora1"], adapter_weights=[0.80])

    pipe.transformer = transformer
    pipe.text_encoder_2 = text_encoder_2

    pipe.enable_model_cpu_offload()  # save some VRAM by offloading the model to CPU

    w, h = image.size
    if text.get('1.0', tk.END).strip() == '':
        prompt_ita = "una ragazza bionda in piedi,totalmente nuda, big breast, capezzoli, figa pelosa,labbra della figa"
    else:
        prompt_ita = text.get('1.0', tk.END)

    prompt = G(source='it', target='en').translate(prompt_ita)
    print(f"prompt: {prompt}")
    image = pipe(
        prompt=prompt,
        image=image,
        mask_image=mask,
        height=h,
        width=w,
        strength=1.0,
        guidance_scale=int(cfg.get()),
        num_inference_steps=int(steps.get()),
        max_sequence_length=512,
        generator=torch.Generator("cpu").manual_seed(0),
    ).images[0]
    image.save("image_fill.png")

    original_width, original_height = image.size

    # Calcola il rapporto di scala mantenendo le proporzioni
    scale = min(1024 / original_width, 1024 / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # Ridimensiona l'immagine
    image_resized = image.resize((new_width, new_height), Image.LANCZOS)

    # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
    canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
    x_offset = (1024 - new_width) // 2
    y_offset = (1024 - new_height) // 2
    canvas.paste(image_resized, (x_offset, y_offset))

    # Converti PIL Image in Pygame Surface
    mode = canvas.mode
    size = canvas.size
    data = canvas.tobytes()

    # Crea surface Pygame dall'immagine
    pygame_image = py.image.fromstring(data, size, mode)
    current_image = pygame_image


def FStable_diffuser_inpainting():
    global text, MODELS, stampa_parametri, Nome, steps, cfg, lora, pathfileref

    stampa_parametri = False
    
    path_image = f"{Nome}_photogamer.png"
    # Correzione: usa Image.open direttamente per file locali
    image = Image.open(path_image).convert("RGB")
    
    if not os.path.exists("clothing_mask.png"):
        print("Detective outfit")
        global screen, current_image
        processor = SegformerImageProcessor.from_pretrained("sayeed99/segformer_b3_clothes")
        model = AutoModelForSemanticSegmentation.from_pretrained("sayeed99/segformer_b3_clothes")
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits.cpu()
        upsampled_logits = nn.functional.interpolate(
            logits,
            size=image.size[::-1],
            mode="bilinear",
            align_corners=False,
        )

        pred_seg = upsampled_logits.argmax(dim=1)[0]

        # Filtro per abbigliamento
        clothing_labels = {
            4: "Upper-clothes",  # Top/Maglietta
            5: "Skirt",          # Gonna
            6: "Pants",          # Pantaloni/Pantaloncini
            7: "Dress"           # Vestito
        }

        # Crea una maschera per i capi di abbigliamento
        clothing_mask = torch.zeros_like(pred_seg, dtype=torch.bool)
        for label_id in clothing_labels.keys():
            clothing_mask |= (pred_seg == label_id)

        # Converti in array numpy
        mask_array = clothing_mask.numpy().astype(np.uint8) * 255

        # 1. Riempi i buchi interni (zone nere dentro le zone bianche)
        contours, _ = cv2.findContours(mask_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask_filled = np.zeros_like(mask_array)
        cv2.drawContours(mask_filled, contours, -1, 255, thickness=cv2.FILLED)

        # 2. Espandi le zone bianche di 10 pixel (dilatazione)
        kernel = np.ones((15, 15), np.uint8)  # 21x21 per espandere di ~10 pixel in tutte le direzioni
        mask_expanded = cv2.dilate(mask_filled, kernel, iterations=1)

        # Converti in immagine PIL
        mask_image = Image.fromarray(mask_expanded, mode='L')

        # Salva la maschera
        mask_image.save("clothing_mask.png")
        print("Maschera salvata come 'clothing_mask.png'")

        # Opzionale: mostra quali capi sono stati rilevati
        detected_clothes = []
        for label_id, label_name in clothing_labels.items():
            if (pred_seg == label_id).any():
                detected_clothes.append(label_name)

        print(f"Capi rilevati: {', '.join(detected_clothes)}")
    else:
        mask_image = Image.open("clothing_mask.png")

    if pathfileref is not None and 'flux' in MODELS.get().lower():
        # Prepara il prompt pulito (rimuovi newline e spazi extra)
        prompt_clean = text.get('1.0', tk.END).strip().replace('\n', ' ')
        
        # Costruisci il comando con le virgolette corrette
        cmd = f'''python tryon_inference.py --model {MODELS.get()}.safetensors --lora {lora.get()} --prompt "{prompt_clean}" --image {Nome}_photogamer.png --mask clothing_mask.png --garment "{pathfileref}" --output_tryon fluxfill_reference.png --steps {int(steps.get())} --guidance_scale {int(cfg.get())} --seed {random.randint(1, 99999)}'''
        
        print(f"Eseguo comando: {cmd}")
        os.system(cmd)

        # Carica l'immagine risultante
        image_resized = Image.open("./fluxfill_reference.png")
        original_width, original_height = image_resized.size
        
        # Calcola il rapporto di scala
        scale = min(1024 / original_width, 1024 / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Ridimensiona l'immagine
        image_resized = image_resized.resize((new_width, new_height), Image.LANCZOS)
        
        # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
        canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
        x_offset = (1024 - new_width) // 2
        y_offset = (1024 - new_height) // 2
        canvas.paste(image_resized, (x_offset, y_offset))

        # Converti PIL Image in Pygame Surface
        mode = canvas.mode
        size = canvas.size
        data = canvas.tobytes()

        # Crea surface Pygame dall'immagine
        pygame_image = py.image.fromstring(data, size, mode)
        current_image = pygame_image
        stampa_parametri = True

    elif pathfileref is None and 'flux' in MODELS.get().lower():
        F_Flux()
        stampa_parametri = True
    else:
        print("Stable diffuser Inpainting")
        init_image = image
        generator = torch.Generator(device="cpu").manual_seed(1)
        
        def make_inpaint_condition(image, image_mask):
            image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
            image_mask = np.array(image_mask.convert("L")).astype(np.float32) / 255.0

            assert image.shape[0:1] == image_mask.shape[0:1], "image and image_mask must have the same image size"
            image[image_mask > 0.5] = -1.0  # set as masked pixel
            image = np.expand_dims(image, 0).transpose(0, 3, 1, 2)
            image = torch.from_numpy(image)
            return image

        control_image = make_inpaint_condition(init_image, mask_image)

        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_inpaint", torch_dtype=torch.float16
        )
        path_local_model = f"Model//{MODELS.get()}.safetensors"
        pipe = StableDiffusionControlNetInpaintPipeline.from_single_file(
            path_local_model, controlnet=controlnet, torch_dtype=torch.float16, safety_checker=None
        )

        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
        pipe.enable_model_cpu_offload()

        w, h = image.size
        if text.get('1.0', tk.END).strip() == '':
            prompt_ita = "una ragazza bionda in piedi, big breast, figa rasata,labia "
        else:
            prompt_ita = text.get('1.0', tk.END)

        prompt = G(source='it', target='en').translate(prompt_ita)
        # generate image
        image = pipe(
            prompt=prompt,
            num_inference_steps=int(steps.get()),
            guidance_scale=int(cfg.get()),
            generator=generator,
            eta=1.0,
            image=init_image,
            mask_image=mask_image,
            control_image=control_image,
            width=w,
            height=h,
        ).images[0]
        image.save("Image2.png")
        # Ridimensiona l'immagine proporzionalmente per adattarla a 1024x1024
        stampa_parametri = True
        original_width, original_height = image.size

        # Calcola il rapporto di scala mantenendo le proporzioni
        scale = min(1024 / original_width, 1024 / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        # Ridimensiona l'immagine
        image_resized = image.resize((new_width, new_height), Image.LANCZOS)

        # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
        canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
        x_offset = (1024 - new_width) // 2
        y_offset = (1024 - new_height) // 2
        canvas.paste(image_resized, (x_offset, y_offset))

        # Converti PIL Image in Pygame Surface
        mode = canvas.mode
        size = canvas.size
        data = canvas.tobytes()

        # Crea surface Pygame dall'immagine
        pygame_image = py.image.fromstring(data, size, mode)
        current_image = pygame_image



Nudifica= tk.Button(frame_controls,text="Nudifica",command=FStable_diffuser_inpainting)
Nudifica.grid(row=8,column=1)

def carica_models():
    import os
    global MODELS
    # Sintassi corretta per list comprehension
    model_list = [os.path.basename(m).split('.')[0] for m in os.listdir('./Model')]
    # Aggiorna i valori della combobox
    MODELS['values'] = model_list

MODELS = ttk.Combobox(frame_controls, values=[])
MODELS.grid(row=8, column=2)
# Bind corretto: evento e funzione
MODELS.bind('<<ComboboxSelected>>', lambda e: carica_models())

# IMPORTANTE: chiamare la funzione con le parentesi ()
carica_models()
MODELS.set('pornworksNudePeoplePhoto_02')

mpens = ['Disabilita Pen','Pen_frontal','Pen_right','Pen_left','pen_sega']
pens = ttk.Combobox(frame_controls, values=mpens)
pens.grid(row=8, column=3, sticky= 'nw') 
pens.set('Disabilita Pen')

# ========== STEPS ==========
lab1 = ttk.Label(frame_controls, text="Steps: 50")
lab1.grid(row=9, column=0, sticky='nw', padx=5)

def update_steps_label(event=None):
    lab1.config(text=f"Steps: {int(steps.get())}")

steps = ttk.Scale(frame_controls, from_=1, to=100, orient='horizontal', command=lambda x: update_steps_label())
steps.set(50)
steps.grid(row=10, column=0, padx=5, pady=5, sticky='ew')

# ========== GUIDANCE SCALE ==========
lab2 = ttk.Label(frame_controls, text="Guidance Scale: 30.0")
lab2.grid(row=9, column=1, sticky='nw', padx=5)

def update_cfg_label(event=None):
    lab2.config(text=f"Guidance Scale: {cfg.get():.1f}")

cfg = ttk.Scale(frame_controls, from_=1.0, to=30.0, orient='horizontal', command=lambda x: update_cfg_label())
cfg.set(30)
cfg.grid(row=10, column=1, padx=5, pady=5, sticky='ew')

# ========== LORA ==========
ttk.Label(frame_controls, text="LoRA:").grid(row=9, column=2, sticky='nw', padx=5)

def loraload(event=None):
    lrs = []
    if os.path.exists("./Lora"):
        for l in os.listdir("./Lora"):
            if l.endswith('.safetensors'):  # Filtra solo i file LoRA
                lrs.append(l)
    lora['values'] = lrs
    if lrs:
        lora.current(0)  # Seleziona il primo elemento

lora = ttk.Combobox(frame_controls, values=[], state='readonly')
lora.grid(row=10, column=2, padx=5, pady=5, sticky='ew')
lora.bind('<Button-1>', loraload)
loraload()

# ========== CANVAS RIFERIMENTO ==========
pathfileref = None

ttk.Label(frame_controls, text="Riferimento:").grid(row=9, column=3, sticky='nw', padx=5)

def loadref(event=None):
    global pathfileref
    from tkinter import filedialog
    
    pathfileref = filedialog.askopenfilename(
        title="Seleziona immagine di riferimento",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
    )
    
    if pathfileref:
        display_image(pathfileref)

def on_drop(event):
    """Gestisce il drop del file"""
    global pathfileref
    # event.data contiene il path del file droppato
    pathfileref = event.data
    
    # Rimuovi eventuali parentesi graffe che Windows aggiunge
    if pathfileref.startswith('{') and pathfileref.endswith('}'):
        pathfileref = pathfileref[1:-1]
    
    display_image(pathfileref)

def display_image(filepath):
    """Visualizza l'immagine nel canvas"""
    try:
        # Rimuovi il placeholder text se presente
        referenze.delete('placeholder')
        
        imgr = Image.open(filepath)
        w, h = imgr.size
        
        # Ridimensiona mantenendo l'aspect ratio per adattarsi al canvas
        canvas_w = 250
        canvas_h = 250
        
        if w >= h:
            new_w = canvas_w
            new_h = int((canvas_w * h) / w)
        else:
            new_h = canvas_h
            new_w = int((canvas_h * w) / h)
        
        imgr = imgr.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Converti per Tkinter
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(imgr)
        
        # Pulisci il canvas e mostra l'immagine centrata
        referenze.delete("all")
        referenze.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=photo,
            anchor='center'
        )
        referenze.image = photo  # Mantieni riferimento
        
        print(f"Immagine caricata: {filepath}")
        
    except Exception as e:
        print(f"Errore nel caricamento dell'immagine: {e}")

# Canvas 250x250 - Occupa row 10 e 11 con rowspan
referenze = tk.Canvas(frame_controls, width=250, height=250, bg='lightgray', relief='sunken', bd=2)
referenze.grid(row=10, column=3, rowspan=2, padx=5, pady=5, sticky='nw')

# Abilita drag and drop sul canvas
referenze.drop_target_register(DND_FILES)
referenze.dnd_bind('<<Drop>>', on_drop)

# Click per aprire file dialog
referenze.bind('<Button-1>', loadref)

# Aggiungi testo informativo sul canvas
referenze.create_text(
    125, 125,
    text="Trascina qui\nun'immagine",
    fill='gray',
    font=('Arial', 9),
    tags='placeholder'
)

from PIL import Image
import threading
import os

def SD_generaIMage():
    global stampa_parametri, canvas, pygame_image, current_image

    # Costruisci il comando come stringa
    comando = f"""python sdtextimage.py --modelpath "{MODELS.get()}" --lora "{lora}" --scale_l 0.7 --scale_ip 0.5 --prompt "{text.get('1.0', tk.END).strip()}" --negative "poorly drawn face, amateur, filter, panties, hand, hands, ugly" --ipadapter "{pathfileref}" --steps {steps.get()} --cfg {cfg.get()}"""
    
    # Funzione da eseguire nel thread
    def run_command():
        global stampa_parametri, canvas, pygame_image, current_image
        try:
            stampa_parametri = False
            print("Avvio generazione immagine...")
            os.system(comando)
            
            # Verifica che l'immagine sia stata creata
            if not os.path.exists("./sdImage.png"):
                print("Errore: immagine non generata")
                stampa_parametri = True
                return
            
            # Carica l'immagine generata
            generated_img = Image.open("./sdImage.png")
            
            # Ridimensiona mantenendo l'aspect ratio per fittare in 1024x1024
            generated_img.thumbnail((1024, 1024), Image.BICUBIC)
            new_width, new_height = generated_img.size
            
            # Crea un'immagine nera 1024x1024 e centra l'immagine ridimensionata
            canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
            x_offset = (1024 - new_width) // 2
            y_offset = (1024 - new_height) // 2
            canvas.paste(generated_img, (x_offset, y_offset))

            # Converti PIL Image in Pygame Surface
            mode = canvas.mode
            size = canvas.size
            data = canvas.tobytes()

            # Crea surface Pygame dall'immagine
            pygame_image = py.image.fromstring(data, size, mode)
            current_image = pygame_image
            
            print("Immagine generata con successo!")
            # Quando il comando finisce, reimposta la flag
            stampa_parametri = True
            
        except Exception as e:
            print(f"Errore nella generazione: {e}")
            import traceback
            traceback.print_exc()
            stampa_parametri = True  # Reimposta anche in caso di errore
    
    # Avvia il thread
    threading.Thread(target=run_command, daemon=True).start()


# ========== BOTTONE GENERA IMAGE ==========
Text_Image = tk.Button(frame_controls, text="Genera Image", command=SD_generaIMage, font=('Arial', 10, 'bold'))
Text_Image.grid(row=11, column=2, padx=5, pady=5, sticky='ew')


















# Avvia Pygame in un thread separato
pygame_thread = threading.Thread(target=avvia_pygame, daemon=True)
pygame_thread.start()

# Aspetta che Pygame si inizializzi
import time
time.sleep(1)

# Controlla se l'immagine esiste già
print(f"file trovato {Nome}_photogamer.png")
if not os.path.exists(f"{Nome}_photogamer.png"):
    prompt_ita = "una Ragazza seduta per terra sul pavimento di una prigione"
    generation_thread = threading.Thread(
        target=Kontext, 
        args=([path_file, 'prigione.png'], prompt_ita),
        daemon=True
    )
    generation_thread.start()
else:
    # Carica l'immagine esistente
    pil_image = Image.open(f"{Nome}_photogamer.png").convert("RGB")
    
    # Ridimensiona proporzionalmente
    original_width, original_height = pil_image.size
    scale = min(1024 / original_width, 1024 / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    pil_image_resized = pil_image.resize((new_width, new_height), Image.LANCZOS)
    
    # Crea canvas nero e centra l'immagine
    canvas = Image.new('RGB', (1024, 1024), (0, 0, 0))
    x_offset = (1024 - new_width) // 2
    y_offset = (1024 - new_height) // 2
    canvas.paste(pil_image_resized, (x_offset, y_offset))
    
    mode = canvas.mode
    size = canvas.size
    data = canvas.tobytes()
    
    current_image = py.image.fromstring(data, size, mode)

# Avvia il loop Tkinter
window.mainloop()