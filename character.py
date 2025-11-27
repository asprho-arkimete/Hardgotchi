from concurrent.futures import thread
from multiprocessing.sharedctypes import Value
from optparse import Values
from sqlite3 import Row
import tkinter as tk
from tkinter import ttk
from regex import F
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pyperclip
import os
import shutil
from datetime import datetime
import webbrowser
import subprocess
import platform

new_image = False
path = None
path_originale = None  # Path dell'immagine originale prima di Nano Banana
photo = None  # Variabile globale per mantenere il riferimento all'immagine
browser_process = None  # Processo del browser

from tkinter import messagebox

def chiudi_browser():
    """Chiude il browser aperto per Nano Banana"""
    global browser_process
    
    try:
        sistema = platform.system()
        
        if sistema == "Windows":
            # Su Windows, chiudi Edge
            subprocess.run([
                'taskkill', '/F', '/IM', 'msedge.exe'
            ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            print("Browser Edge chiuso (Windows)")
            
        elif sistema == "Darwin":  # macOS
            # Su macOS usa AppleScript per chiudere la finestra
            script = '''
            tell application "Safari"
                close (every window whose name contains "AI Studio")
            end tell
            tell application "Google Chrome"
                close (every window whose name contains "AI Studio")
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            print("Browser chiuso (macOS)")
            
        elif sistema == "Linux":
            # Su Linux, trova e chiudi i processi del browser
            subprocess.run([
                'pkill', '-f', 'aistudio.google.com'
            ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            print("Browser chiuso (Linux)")
            
    except Exception as e:
        print(f"Nota: Non è stato possibile chiudere automaticamente il browser: {e}")

def trova_e_salva_immagine():
    """Trova l'immagine più recente da Nano Banana e la salva"""
    global path, path_originale, photo, frame, new_image, browser_process,Combo
    
    try:
        # Crea la cartella characters se non esiste
        os.makedirs("characters", exist_ok=True)
        
        # Percorso della cartella Downloads
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Trova tutte le immagini di Nano Banana
        images_nano = []
        for filename in os.listdir(downloads_path):
                full_path = os.path.join(downloads_path, filename)
                # Ottieni la data di modifica del file
                mod_time = os.path.getmtime(full_path)
                images_nano.append((full_path, mod_time))
        
        if not images_nano:
            messagebox.showwarning("Attenzione", "Nessuna immagine di Nano Banana trovata nei Downloads!")
            return
        
        # Ordina per data e prendi la più recente
        images_nano.sort(key=lambda x: x[1], reverse=True)
        immagine_recente = images_nano[0][0]
        
        # Ottieni il nome dal campo di testo
        nome_personaggio = nome.get("1.0", "end-1c").strip()
        
        # Se il nome è vuoto, usa un timestamp
        if not nome_personaggio:
            nome_personaggio = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Percorso di destinazione
        destinazione = os.path.join("characters", f"{nome_personaggio}.png")
        
        # Copia il file
        shutil.copy2(immagine_recente, destinazione)
        print(f"Immagine salvata: {destinazione}")

        # Salva il path di destinazione in un file di testo
        path_file = os.path.join("characters", f"{nome_personaggio}.txt")
        with open(path_file, 'w', encoding='utf-8') as f:
            f.write(destinazione)
            print(f"Path salvato: {destinazione}")
        print(f"Path salvato in: {path_file}")

        # Aggiorna il path e carica l'immagine nel canvas
        path = destinazione
        carica_immagine_canvas(path)
        
        # Aggiorna la combobox dopo aver salvato una nuova immagine
        cerca_images_characters()
        
        new_image = False

        # Chiudi il browser di Nano Banana
        chiudi_browser()
        print("Tentativo di chiusura browser completato")
        
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvare l'immagine: {e}")
        print(f"Errore: {e}")

def carica_immagine_canvas(image_path):
    """Carica un'immagine nel canvas"""
    global photo, frame
    
    try:
        # Carica l'immagine
        img = Image.open(image_path)
        
        # Ridimensiona l'immagine mantenendo le proporzioni
        canvas_width = 212
        canvas_height = 212
        
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        img = img.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        frame.delete("all")
        frame.create_image(106, 106, image=photo)
        print(f"Immagine caricata nel canvas: {image_path}")
        
    except Exception as e:
        print(f"Errore nel caricamento dell'immagine: {e}")

def drag_drop(event):
    global path, path_originale, frame, photo, new_image, browser_process
    # Ottieni il percorso del file trascinato
    path = event.data
    # Rimuovi le parentesi graffe se presenti (Windows)
    if path.startswith('{') and path.endswith('}'):
        path = path[1:-1]
    
    # SALVA IL PATH ORIGINALE
    path_originale = path
    print(f"Path originale memorizzato: {path_originale}")
    
    try:
        carica_immagine_canvas(path)
        
        # MessageBox con due pulsanti Yes/No
        risp = messagebox.askyesno(
            "Edita con Reve", 
            "Vuoi editare con Reve?\n\nPrompt: ingrandisci il viso, mantieni la coerenza del soggetto e crea una foto tessera del primo piano frontale del viso del soggetto, mantenendo le coerenze del viso"
        )
        
        if risp:  # risp è True se l'utente clicca Yes
            webbrowser.open("https://app.reve.com/home")
            print("Apertura Reve...")
            # Copia il testo negli appunti
            pyperclip.copy("ingrandisci il viso, mantieni la coerenza del soggetto e crea una foto tessera del primo piano frontale del viso del soggetto, mantenendo le coerenze del viso")
            
            # Imposta il flag per cercare la nuova immagine
            new_image = True
        else:
            # Se l'utente sceglie NO, salva subito l'immagine originale
            print("Salvataggio immagine originale senza Nano Banana...")
            
            # Crea la cartella characters se non esiste
            os.makedirs("characters", exist_ok=True)
            
            # Ottieni il nome dal campo di testo
            nome_personaggio = nome.get("1.0", "end-1c").strip()
            
            # Se il nome è vuoto, usa il nome del file originale senza estensione
            if not nome_personaggio:
                nome_personaggio = os.path.splitext(os.path.basename(path_originale))[0]
                print(f"Nome vuoto, uso il nome del file: {nome_personaggio}")
            
            # Estensione del file originale
            estensione = os.path.splitext(path_originale)[1]
            
            # Percorso di destinazione
            destinazione = os.path.join("characters", f"{nome_personaggio}{estensione}")
            
            # Copia il file
            shutil.copy2(path_originale, destinazione)
            print(f"Immagine originale salvata: {destinazione}")
            
            # Salva il path di destinazione in un file di testo
            path_file = os.path.join("characters", f"{nome_personaggio}.txt")
            with open(path_file, 'w', encoding='utf-8') as f:
                f.write(destinazione)
                print(f"Path salvato: {destinazione}")
            print(f"Path salvato in: {path_file}")
            
            # Aggiorna la combobox
            cerca_images_characters()
           
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel caricamento dell'immagine: {e}")
        print(f"Errore: {e}")

def cerca_images_characters():
    """Cerca tutte le immagini nella cartella characters e aggiorna la combobox"""
    global Combo
    
    # Crea la cartella characters se non esiste
    os.makedirs("characters", exist_ok=True)
    
    # Lista per memorizzare i nomi delle immagini
    images = []
    
    try:
        # Cerca tutti i file nella cartella characters
        for img in os.listdir("./characters"):
            # Controlla se il file è un'immagine (jpg o png)
            if img.endswith('.jpg') or img.endswith('.png'):
                images.append(img)
        
        # Aggiorna i valori della combobox
        Combo['values'] = images
        
        print(f"Trovate {len(images)} immagini: {images}")
        
    except Exception as e:
        print(f"Errore nella ricerca delle immagini: {e}")

def on_combobox_select(event):
    """Carica l'immagine selezionata dalla combobox"""
    selected = Combo.get()
    print(f"INdice: {Combo.current() }")
    if selected:
        image_path = os.path.join('characters', selected)
        carica_immagine_canvas(image_path)

# Usa TkinterDnD invece di tk.Tk()
window = TkinterDnD.Tk()
window.title("select character")
window.geometry("500x700")
window.resizable(False,False)

frame1 = tk.Frame(window)
frame1.grid(row=0, column=0)

frame = tk.Canvas(frame1, width=212, height=212, bg='red')
# Registra il canvas per il drag and drop
frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', drag_drop)
frame.grid(row=0, column=0)

lab_nome = tk.Label(frame1, text="Nome Personaggio")
lab_nome.grid(row=1, column=1)
nome = tk.Text(frame1, width=15, height=1)
nome.grid(row=2, column=1)

# Pulsante per cercare e salvare l'immagine da Nano Banana
buttonSalva = tk.Button(frame1, text='Salva da Reve', command=trova_e_salva_immagine)
buttonSalva.grid(row=2, column=0)

# Combobox per selezionare le immagini salvate
Combo = ttk.Combobox(frame1, state='readonly')
Combo.grid(row=0, column=1, sticky='ne')
Combo.bind('<<ComboboxSelected>>', on_combobox_select)
# Aggiorna la lista quando si clicca sulla freccia della combobox
Combo.bind('<Button-1>', lambda e: cerca_images_characters())
cerca_images_characters()
Combo.current(0)

import torch
from diffusers import FluxTransformer2DModel, FluxPipeline
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize
from deep_translator import GoogleTranslator
from diffusers import StableDiffusionPipeline
import tkinter as tk
from tkinter import ttk
import os
# plotter.py
from PIL import Image
import matplotlib.pyplot as plt

def viewImage(filename):
    """Visualizza un'immagine dato il percorso del file"""
    try:
        img = Image.open(filename)
        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title(f"Immagine: {filename}")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Errore nel caricamento dell'immagine: {e}")

def F_Generasfondo():
    print("Genera sfondo")
    global Combo, model, text
    indice = Combo.current() + 1
    print(f"indice {indice}")
    
    # Traduzione del prompt
    prompt_text = text.get('1.0', tk.END).strip()
    prompt = GoogleTranslator(source='it', target='en').translate(prompt_text)
    print(f"prompt: {prompt}")

    model_name = model.get()
    
    if 'f_' in model_name.lower() or 'flux' in model_name.lower():
        print("Genera con Flux")
        
        bfl_repo = "black-forest-labs/FLUX.1-dev"
        dtype = torch.bfloat16

        # Carica e quantizza il transformer
        print("Caricamento transformer...")
        transformer = FluxTransformer2DModel.from_pretrained(
            bfl_repo, 
            subfolder="transformer", 
            torch_dtype=dtype
        )
        quantize(transformer, weights=qfloat8)
        freeze(transformer)

        # Carica e quantizza il text encoder
        print("Caricamento text encoder...")
        text_encoder_2 = T5EncoderModel.from_pretrained(
            bfl_repo, 
            subfolder="text_encoder_2", 
            torch_dtype=dtype
        )
        quantize(text_encoder_2, weights=qfloat8)
        freeze(text_encoder_2)

        # Crea la pipeline
        print("Creazione pipeline...")
        pipe = FluxPipeline.from_pretrained(
            bfl_repo, 
            transformer=None, 
            text_encoder_2=None, 
            torch_dtype=dtype
        )
        
        pipe.transformer = transformer
        pipe.text_encoder_2 = text_encoder_2

        pipe.enable_model_cpu_offload()

        # Genera l'immagine
        print("Generazione immagine in corso...")
        out = pipe(
            prompt=prompt,
            guidance_scale=6,
            height=1024,
            width=1024,
            num_inference_steps=30,
            max_sequence_length=256,
        ).images[0]
        
        # Salva l'immagine
        output_filename=None
        if indice>1:
            output_filename = f"prigione{indice}.png"
        else:
            output_filename = f"prigione.png"
        out.save(output_filename)
        print(f"Immagine salvata: {output_filename}")
        viewImage(output_filename)
        
    else:
        print("Stable Diffusion Pipeline")
        if model_name and model_name != 'flux-dev':
            # Cerca prima .safetensors, poi .ckpt
            model_path_safetensors = os.path.join('./Model', f"{model_name}.safetensors")
            model_path_ckpt = os.path.join('./Model', f"{model_name}.ckpt")
            
            if os.path.exists(model_path_safetensors):
                print(f"Caricamento modello: {model_path_safetensors}")
                pipe = StableDiffusionPipeline.from_single_file(
                    model_path_safetensors,
                    safety_checker=None,
                    use_safetensors=True,
                    torch_dtype=torch.float16
                )
            elif os.path.exists(model_path_ckpt):
                print(f"Caricamento modello: {model_path_ckpt}")
                pipe = StableDiffusionPipeline.from_single_file(
                    model_path_ckpt,
                    safety_checker=None,
                    torch_dtype=torch.float16
                )
            else:
                print(f"Modello non trovato, uso modello default")
                pipe = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    safety_checker=None,
                    torch_dtype=torch.float16
                )
        else:
            print("Caricamento modello default...")
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                safety_checker=None,
                torch_dtype=torch.float16
            )

        pipe = pipe.to("cuda")

        # Ottimizzazioni per memoria
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        
        # Ottimizzazioni per memoria
        pipe.enable_model_cpu_offload()

        # Genera l'immagine
        print("Generazione immagine in corso...")
        image = pipe(
            prompt=prompt,
            negative_prompt='bad quality, blurry, distorted, deformed, ugly, poorly drawn',
            num_inference_steps=100,   
            guidance_scale=7.5,
            width=1024,
            height=1024
        ).images[0]
        
         # Salva l'immagine
        output_filename=None
        if indice>1:
            output_filename = f"prigione{indice}.png"
        else:
            output_filename = f"prigione.png"
        image.save(output_filename)
        print(f"Immagine salvata: {output_filename}")
        viewImage(output_filename)


# Interfaccia grafica
frame_sfond = tk.Frame(window)
frame_sfond.grid(row=2, column=0)

import threading
def avvia_generazione():
    genera_sfondo.config(state='disabled', text='Generazione...')
    
    def genera_e_ripristina():
        F_Generasfondo()
        genera_sfondo.config(state='normal', text='Genera sfondo')
    
    thread = threading.Thread(target=genera_e_ripristina)
    thread.daemon = True
    thread.start()

genera_sfondo = tk.Button(frame_sfond, text="Genera sfondo", command=avvia_generazione)
genera_sfondo.grid(row=0, column=0, sticky='nw')


text = tk.Text(frame_sfond, width=25, height=8)
text.grid(row=0, column=1, sticky='nw')
p = """Interno dettagliato di un'antica cella di prigione medievale, muri in pietra grezza e scura con muschio, pavimento in lastre di pietra consumate, catene arrugginite appese alla parete, una piccola finestra con spesse sbarre di ferro attraverso cui filtrano raggi di luce solare che creano drammatici contrasti di luce e ombra, atmosfera cupa e claustrofobica, fotorealistica, altamente dettagliata, illuminazione cinematografica, 8k"""
text.insert('1.0', p)

def models(event=None):
    global model
    model['values'] = ['flux-dev'] + [os.path.basename(m).split('.')[0] for m in os.listdir('./Model') if m.endswith('.safetensors') or m.endswith('.ckpt')]

model = ttk.Combobox(frame_sfond)
model.grid(row=0, column=2, sticky='nw')
model.bind('<Button-1>', models)

# Popola i valori iniziali e seleziona il primo
models()  # Chiama la funzione per popolare i valori
model.current(0)  # Seleziona flux-dev di default

def Gioca():
    import os
    global Combo
    """Salva il personaggio selezionato e avvia il gioco"""
    selected = Combo.get()
    
    if not selected:
        messagebox.showwarning("Attenzione", "Seleziona un personaggio dalla lista!")
        return
    
    try:
        # Ottieni l'indice della selezione
        indice = Combo.current()
        print(f"Indice selezionato: {indice}")
        
        # Copia il file .txt del personaggio selezionato in select.txt
        nome_file = os.path.splitext(selected)[0]
        path_txt = os.path.join('characters', f'{nome_file}.txt')
        
        if not os.path.exists(path_txt):
            messagebox.showerror("Errore", f"File {nome_file}.txt non trovato!")
            return
        
        # Leggi il contenuto del file originale
        with open(path_txt, 'r', encoding='utf-8') as f:
            contenuto = f.read()
        
        # Rimuovi select.txt se esiste
        if os.path.exists('select.txt'):
            os.remove('select.txt')
        
        # Scrivi il contenuto + indice nel nuovo select.txt
        with open('select.txt', 'w', encoding='utf-8') as f:
            f.write(contenuto)
            f.write(f"\nindice:{indice};")
        
        print(f"Personaggio salvato: {path_txt} -> select.txt con indice {indice}")
        
        # Avvia il gioco
        print("Avvio del gioco...")
        window.destroy()  # Chiude la finestra di selezione
        os.system("python C_game.py")
        
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nell'avvio del gioco: {e}")
        print(f"Errore: {e}")


buttonGame = tk.Button(frame_sfond, text='Gioca', command=Gioca)
buttonGame.grid(row=2, column=1, sticky='nw')  # Corretto: sticky non stick

def memorizza_imp(event=None):
    try:
        # Leggi il personaggio selezionato
        selected = Combo.get()
        if not selected:
            print("Nessun personaggio selezionato")
            return
        
        # Rimuovi l'estensione .png da selected per ottenere il nome base
        nome_base = os.path.splitext(selected)[0]
        
        # Costruisci il path del file .txt
        character_file = os.path.join('characters', f'{nome_base}.txt')
        
        print(f"Lettura file: {character_file}")
        
         
        
        # Leggi il file del personaggio per ottenere il path dell'immagine
        with open(character_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()  # Es: "characters/Nicole.png"
        
        print(f"Path immagine letto: {first_line}")
        
        # Estrai il nome del file senza estensione dal path
        # Es: "characters/Nicole.png" -> "Nicole"
        nome_file = os.path.splitext(os.path.basename(first_line))[0]
        save_file = f"{nome_file}_save.txt"
        
        print(f"File save identificato: {save_file}")
        
        # Calcola i nuovi intervalli in millisecondi
        fame_ore = int(Fame.get().replace('ORA', '').replace('ORE', '').strip())
        sete_ore = int(Sete.get().replace('ORA', '').replace('ORE', '').strip())
        attacco_min = int(intervallo_attacco.get().replace('min', '').strip())
        
        fame_ms = fame_ore * 60 * 60 * 1000
        sete_ms = sete_ore * 60 * 60 * 1000
        attacco_ms = attacco_min * 60 * 1000
        
        # Salva le impostazioni in impo.txt
        with open('impo.txt', 'w', encoding='utf-8') as f:
            f.write(f'fame:{fame_ms};\n')
            f.write(f'sete:{sete_ms};\n')
            f.write(f'attacco:{attacco_ms};\n')
        
        print(f"✅ impo.txt salvato")
        
        # Aggiorna il file save del personaggio se esiste
        if os.path.exists(save_file):
            print(f"Aggiornamento {save_file}...")
            
            # Leggi il file save esistente
            with open(save_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Aggiorna i valori nel file
            updated_lines = []
            for line in lines:
                line_stripped = line.strip()
                
                if line_stripped.startswith('last_fame_update:'):
                    old_value = int(line_stripped.split(':')[1])
                    new_value = 0 if old_value > fame_ms else old_value
                    updated_lines.append(f'last_fame_update:{new_value}\n')
                    if old_value != new_value:
                        print(f"  Fame reset: {old_value} -> {new_value}")
                    
                elif line_stripped.startswith('last_sete_update:'):
                    old_value = int(line_stripped.split(':')[1])
                    new_value = 0 if old_value > sete_ms else old_value
                    updated_lines.append(f'last_sete_update:{new_value}\n')
                    if old_value != new_value:
                        print(f"  Sete reset: {old_value} -> {new_value}")
                    
                elif line_stripped.startswith('contaTDattaco:'):
                    old_value = int(line_stripped.split(':')[1])
                    new_value = 0 if old_value > attacco_ms else old_value
                    updated_lines.append(f'contaTDattaco:{new_value}\n')
                    if old_value != new_value:
                        print(f"  Attacco reset: {old_value} -> {new_value}")
                    
                else:
                    updated_lines.append(line)
            
            # Scrivi il file aggiornato
            with open(save_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            print(f"✅ {save_file} aggiornato")
        else:
            print(f"⚠️ File save {save_file} non esiste ancora (verrà creato al primo gioco)")
        
        print(f"✅ Impostazioni: Fame={fame_ore}h, Sete={sete_ore}h, Attacco={attacco_min}min")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
# Fame
tk.Label(frame_sfond, text="Fame:").grid(row=4, column=0, sticky='e', padx=5)
Fame = ttk.Combobox(frame_sfond, values=[f'{i} ORA' if i == 1 else f'{i} ORE' for i in range(1, 11)], width=15, state='readonly')
Fame.grid(row=4, column=1, sticky='w', pady=5)
Fame.current(0)
Fame.bind('<<ComboboxSelected>>', memorizza_imp)

# Sete
tk.Label(frame_sfond, text="Sete:").grid(row=5, column=0, sticky='e', padx=5)
Sete = ttk.Combobox(frame_sfond, values=[f'{i} ORA' if i == 1 else f'{i} ORE' for i in range(1, 7)], width=15, state='readonly')
Sete.grid(row=5, column=1, sticky='w', pady=5)
Sete.current(0)
Sete.bind('<<ComboboxSelected>>', memorizza_imp)

# Intervallo attacco
tk.Label(frame_sfond, text="Intervallo attacco:").grid(row=6, column=0, sticky='e', padx=5)
intervallo_attacco = ttk.Combobox(frame_sfond, values=[f'{i} min' for i in range(10, 121, 10)], width=15, state='readonly')
intervallo_attacco.grid(row=6, column=1, sticky='w', pady=5)
intervallo_attacco.current(0)
intervallo_attacco.bind('<<ComboboxSelected>>', memorizza_imp)

# Salva le impostazioni iniziali
memorizza_imp()






# Carica le immagini all'avvio
cerca_images_characters()

window.mainloop()