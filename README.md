# Hardgotchi
Markdown

# ⛓️ Hardgotchi: Simulazione di Sopravvivenza Umanoide

Benvenuto in **Hardgotchi**, un'implacabile simulazione di cura e sopravvivenza focalizzata su un **personaggio Umanoide**. Dimentica gli animaletti digitali; qui la vita (o la morte) del tuo character è decisa dalle tue scelte.

Questo progetto utilizza le reti neurali di **Stable Diffusion** e **Flux** (con **EditImage**) per generare e modificare dinamicamente il tuo personaggio in tempo reale, rendendo ogni giorno una sfida visiva.

Questo progetto utilizza le reti neurali di **Stable Diffusion** e **Flux** (con **EditImage**) per generare e modificare dinamicamente il tuo personaggio Umanoide in tempo reale.

---

## 🚀 Istruzioni per l'Avvio

Segui questi passaggi per iniziare l'installazione e la configurazione.

### 1. Clonazione del Repository

Apri il terminale e clona il progetto:

```bash
git clone [https://github.com/asprho-arkimete/Hardgotchi.git](https://github.com/asprho-arkimete/Hardgotchi.git)
cd Hardgotchi
2. Configurazione dell'Ambiente Virtuale
È fondamentale isolare le dipendenze in un ambiente virtuale (compatibile con Python 3.10):

Bash

# Creazione dell'ambiente virtuale
python 3.10 -m venv VNDKey
# Attivazione (su Windows)
.\VNDKey\Scripts\activate
# Attivazione (su Mac/Linux)
source VNDKey/bin/activate
3. Scaricamento dei Modelli
Prima di eseguire, scarica i modelli necessari:

Modelli Base (Checkpoint): Scarica i file elencati in Model/Modelli_Consigliati.md e inseriscili nella cartella Model.

LoRA: Scarica i file elencati in Lora/Lora_Consigliati.md e inseriscili nella cartella Lora.

4. Inizio del Gioco
Esegui lo script principale:

Bash

python character.py
🎮 Fase di Setup
Al primo avvio, ti verranno richieste le seguenti informazioni:

Crea o Inserisci il Character: Fornisci un'immagine del tuo personaggio. Ti consigliamo di editarla (con strumenti come NanoBana, Rive o un qualsiasi editor fotografico) per ottenere un ritratto o una "foto fototessera" pulita.

Imposta i Parametri: Definisci la difficoltà regolando i temporizzatori per Fame, Sete e Attacco.

Genera l'Ambientazione: Genera l'immagine della "prigione" o della stanza in cui il tuo personaggio sarà rinchiuso per tutta l'esperienza.

🏆 La Sfida
Riuscirai a far sopravvivere il tuo Character per 100 giorni, confinato in una cella di prigione o nella tua ambientazione generata? La sfida di Hardgotchi ha inizio!
