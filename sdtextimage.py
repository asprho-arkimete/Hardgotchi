import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import os
from PIL import Image


def sdtextimage(modelpath, prompt, negative, steps, cfg, ip_adapter_path, scale_lora, scale_ip):
    # Carica e prepara l'immagine di riferimento
    imageface = Image.open(ip_adapter_path).convert('RGB').resize((512, 512), Image.BICUBIC)
    
    # Carica il modello
    pipe = StableDiffusionPipeline.from_single_file(
        modelpath, 
        safety_checker=None,
        torch_dtype=torch.bfloat16
    )

    # Configura il sampler DPM++ 2M Karras
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config,
        use_karras_sigmas=True,
        algorithm_type="dpmsolver++"
    )

    # IMPORTANTE: Carica LoRA e IP-Adapter PRIMA di spostare su CUDA
    # Carica LoRA
    pathlora = "./Lora/AnalGapeCreampie-v4.safetensors"
    pipe.load_lora_weights(
        "./Lora",
        weight_name=os.path.basename(pathlora),
        adapter_name="Gape"
    )
    
    # Attiva LoRA con peso
    pipe.set_adapters("Gape", adapter_weights=scale_lora)

    # Carica IP-Adapter
    pipe.load_ip_adapter(
        "h94/IP-Adapter",
        subfolder="models", 
        weight_name="ip-adapter-full-face_sd15.bin"
    )
    
    pipe.set_ip_adapter_scale(scale_ip)

    # Ora sposta su CUDA e abilita ottimizzazioni
    pipe = pipe.to("cuda")
    
    # Ottimizzazioni memoria (NOTA: cpu_offload può rallentare, considera di rimuoverlo se hai VRAM sufficiente)
    # pipe.enable_model_cpu_offload()  # Commentato: contrasta con .to("cuda")
    pipe.enable_vae_slicing()
    
    # Abilita xformers solo se installato
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception as e:
        print(f"xformers non disponibile: {e}")

    # Genera l'immagine
    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        ip_adapter_image=imageface,
        num_inference_steps=steps,
        guidance_scale=cfg,
        width=576,
        height=576
    ).images[0]

    # Ridimensiona e salva
    image = image.resize((1024, 1024), Image.BICUBIC)
    image.save("sdImage.png")
    
    return image

    
def main():
    pathmodel = "./Model/kIOKISCyberrealistic_v10.safetensors"
    
    prompt = """<lora:AnalGapeCreampie-v4:0.8> Anal Gape, a girl lying on the bed legs spread to the up, 
pussy open, Ano spread, brown eyes, blond hair, pubic hair, from front, perfect face"""
    
    negative = """Creampie, poorly drawn face, amateur, filter, panties, hand, hands, ugly"""
    
    ip_adapter_path = "characters/Ilaria.png"
    steps = 40
    cfg = 7.5
    scale_lora = 0.7  # ERRORE CORRETTO: era "0-7" invece di 0.7
    scale_ip = 0.5
    
    sdtextimage(pathmodel, prompt, negative, steps, cfg, ip_adapter_path, scale_lora, scale_ip)
    print("Immagine generata e salvata come sdImage.png")


if __name__ == "__main__":
    main()
