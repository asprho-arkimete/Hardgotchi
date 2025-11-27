import requests
import base64
import json
import os # Importa os per controllare l'esistenza del file

# --- CONFIGURAZIONE ---
REVE_API_KEY = "papi.3fe50374-d037-4327-900f-e09d2f622c4d.4hd9rVkcSVRujNE-gATnYcgAzOOqExwp" # **SOSTITUISCI QUI LA TUA CHIAVE API**
API_ENDPOINT = "https://api.reve.com/v1/image/edit"
# Definisci il percorso dell'immagine (assicurati che esista!)
image_path = "./photogamer.png"
OUTPUT_FILENAME = "edited_image_reve.png"

# --- FUNZIONE DI CONVERSIONE ---
def image_to_base64(image_path):
    """Converte un file immagine locale in una stringa Base64."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Il file non è stato trovato: {image_path}")
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# --- PREPARAZIONE DEI DATI ---
try:
    image_base64 = image_to_base64(image_path)
except FileNotFoundError as e:
    print(f"Errore: {e}")
    exit()

# Set up headers
headers = {
    "Authorization": f"Bearer {REVE_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Set up request payload
payload = {
    "edit_instruction": "cambia il colore della maglietta bianca in giallo",
    "reference_image": image_base64, # Conferma il nome del campo di input
    "version": "latest"
}

# --- 4. ESECUZIONE DELLA RICHIESTA E SALVATAGGIO ---
print(f"Invio della richiesta di modifica a {API_ENDPOINT}...")

try:
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status() # Solleva un HTTPError per risposte errate

    # Parse the response
    result = response.json()
    print(f"Request ID: {result.get('request_id')}")
    print(f"Credits used: {result.get('credits_used')}")
    print(f"Credits remaining: {result.get('credits_remaining')}")

    if result.get('content_violation'):
        print("❌ Attenzione: Rilevata violazione delle politiche sui contenuti.")
    else:
        print("✅ Immagine modificata con successo!")
        
        # Salva l'immagine decodificando il Base64 dal campo 'image'
        output_base64 = result.get('image')
        
        if output_base64:
            try:
                image_data = base64.b64decode(output_base64)
                with open(OUTPUT_FILENAME, "wb") as f:
                    f.write(image_data)
                print(f"💾 L'immagine modificata è stata salvata come '{OUTPUT_FILENAME}'")
            except Exception as e:
                print(f"❌ Errore durante la decodifica/salvataggio del file: {e}")
        else:
            print("⚠️ Il campo 'image' contenente i dati Base64 di output non è stato trovato nella risposta.")


except requests.exceptions.HTTPError as errh:
    print(f"\n❌ ERRORE HTTP ({response.status_code}): {errh}")
    print(f"Messaggio di errore del server: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"\n❌ Errore di connessione o generico: {e}")
except json.JSONDecodeError as e:
    print(f"❌ Impossibile analizzare la risposta JSON: {e}")