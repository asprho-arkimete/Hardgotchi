import torch
from diffusers import FluxPipeline
from diffusers import FluxTransformer2DModel 
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize
from PIL import Image
import random
import os
from deep_translator import GoogleTranslator


def F_generaIMage(pathfileref, model, lora, steps, cfg, text, seed, lora_strength=0.9):
    
    try:
        bfl_repo = "black-forest-labs/FLUX.1-dev"
        dtype = torch.bfloat16

        print("Caricamento modello in corso...")
        
        # Carica la pipeline PRIMA
        pipe = FluxPipeline.from_pretrained(bfl_repo, torch_dtype=dtype)

        transformer = FluxTransformer2DModel.from_single_file(
            f"./Model/{model}.safetensors", 
            torch_dtype=dtype
        )
        text_encoder_2 = T5EncoderModel.from_pretrained(
            bfl_repo, 
            subfolder="text_encoder_2", 
            torch_dtype=dtype
        )
        
        # Quantizza il transformer e text encoder della pipeline
        quantize(transformer, weights=qfloat8)
        freeze(transformer)
        
        quantize(text_encoder_2, weights=qfloat8)
        freeze(text_encoder_2)
        
        # Carica IP Adapter se c'è un'immagine di riferimento
        ip_adapter_image = None
        if pathfileref is not None and pathfileref != "":
            print("Caricamento IP Adapter...")
            pipe.load_ip_adapter(
                "XLabs-AI/flux-ip-adapter-v2",
                weight_name="ip_adapter.safetensors",
                image_encoder_pretrained_model_name_or_path="SG161222/Verus_Vision_1.0b"
            )
            pipe.set_ip_adapter_scale(1.0)
            
            # Carica l'immagine di riferimento
            ip_adapter_image = Image.open(pathfileref)

        # Carica LoRA se selezionato
        if lora and lora != "":
            print(f"Caricamento LoRA: {lora}")
            
            # Aggiungi estensione se manca
            lora_filename = lora if lora.endswith('.safetensors') else f"{lora}.safetensors"
            
            print(f"File LoRA: {lora_filename}")
            
            # Verifica che il file esista
            full_path = f"./Lora/{lora_filename}"
            if not os.path.exists(full_path):
                print(f"ERRORE: File LoRA non trovato: {full_path}")
            else:
                try:
                    # Carica il LoRA
                    pipe.load_lora_weights(
                        "./Lora",
                        weight_name=lora_filename,
                        adapter_name="lora1"
                    )
                    
                    # Attiva il LoRA con lo strength specificato (0.9 consigliato)
                    pipe.set_adapters("lora1", adapter_weights=lora_strength)
                    pipe.fuse_lora(adapter_names=["lora1"], lora_scale=1.0)
                    
                    print(f"✓ LoRA caricato con successo (strength: {lora_strength})")
                    
                except Exception as lora_error:
                    print(f"Errore caricamento LoRA: {lora_error}")
                    import traceback
                    traceback.print_exc()
          
        # Assegna transformer e text encoder PRIMA di enable_model_cpu_offload
        pipe.transformer = transformer
        pipe.text_encoder_2 = text_encoder_2
        
        # Abilita CPU offload per risparmiare memoria
        pipe.enable_model_cpu_offload()
        
        # Imposta il seed per la riproducibilità
        generator = torch.Generator(device="cpu").manual_seed(seed)
        
        # Traduci il prompt (già ricevuto come parametro)
        prompt = text
        
        print(f"\nGenerazione immagine in corso...")
        print(f"Prompt: {prompt}")
        print(f"Steps: {int(steps)}")
        print(f"Guidance Scale: {cfg}")
        print(f"Seed: {seed}")
        print(f"LoRA Strength: {lora_strength}")
        
        # Genera l'immagine
        generation_kwargs = {
            "prompt": prompt,
            "guidance_scale": float(cfg),
            "height": 1024,
            "width": 768,
            "num_inference_steps": int(steps),
            "max_sequence_length": 256,
            "generator": generator,
        }
        
        # Aggiungi l'immagine IP adapter se presente
        if ip_adapter_image is not None:
            generation_kwargs["ip_adapter_image"] = ip_adapter_image
        
        out = pipe(**generation_kwargs).images[0]
        
        # Salva l'immagine con il seed nel nome
        output_path = f"image_generate.png"
        out.save(output_path)
        print(f"\n✓ Immagine salvata in: {output_path}")
        
        
    except Exception as e:
        print(f"Errore durante la generazione: {e}")
        import traceback
        traceback.print_exc()


# Main execution
text = "A girl with legs lifted high, asshole dilated,hairy pussy"
text = GoogleTranslator(source='it', target='en').translate(text)
print(f"Prompt eng: {text}")

pathfileref = None
lora = "NSFW Anal Gape 2"
model = "fluxUncensoredFemale_v10"

# PARAMETRI CORRETTI PER FLUX + QUESTO LORA
seed = 2579264284  # Fisso per test ripetibili
steps = 28  # 20-30 è ottimale per FLUX
cfg = 3.5  # 1-3.5 è il range corretto per FLUX
lora_strength = 1.5  # Aumentato per effetto più forte (prova 0.9-1.2)

F_generaIMage(pathfileref, model, lora, steps, cfg, text, seed, lora_strength)