import argparse
import torch
from diffusers.utils import load_image, check_min_version
from diffusers import FluxPriorReduxPipeline, FluxFillPipeline
from diffusers import FluxTransformer2DModel
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize
import numpy as np
from torchvision import transforms

def run_inference(
    model,
    lora,
    prompt,
    image_path,
    mask_path,
    garment_path,
    num_steps=50,
    guidance_scale=30,
    seed=42,
    pipe=None
):
    bfl_repo = "black-forest-labs/FLUX.1-dev"
    dtype = torch.bfloat16
    
    # Build pipeline
    if pipe is None:
        try:
            transformer = FluxTransformer2DModel.from_pretrained(
                model,
                torch_dtype=dtype
            )
            print(f"Model transformer caricato da: {model}")
        except Exception as error:
            print(f"Errore nel caricamento del modello da pretrained: {error}")
            print("Tentativo di caricamento come singolo file...")
            transformer = FluxTransformer2DModel.from_single_file(
                f"./Model//{model}",
                torch_dtype=dtype
            )
            print(f"Model transformer caricato da file singolo: {model}")

        quantize(transformer, weights=qfloat8)
        freeze(transformer)

        text_encoder_2 = T5EncoderModel.from_pretrained(
            bfl_repo, 
            subfolder="text_encoder_2", 
            torch_dtype=dtype
        )
        quantize(text_encoder_2, weights=qfloat8)
        freeze(text_encoder_2)
        
        pipe = FluxFillPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=dtype
        )

        pipe.load_lora_weights(f"./Lora//{lora}", adapter_name="lora")
        pipe.set_adapters(["lora"], adapter_weights=[0.80])

        pipe.transformer = transformer
        pipe.text_encoder_2 = text_encoder_2

        pipe.to('cuda')
        pipe.enable_model_cpu_offload()

    else:
        pipe.to("cuda")
        pipe.transformer.to(torch.bfloat16)

    # Add transform
    image_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])

    mask_transform = transforms.Compose([
        transforms.ToTensor()
    ])

    # Load images - l'input definisce le dimensioni target
    image = load_image(image_path).convert("RGB")
    dim_target = image.size  # (width, height) - es. (1024, 1024)
    
    mask = load_image(mask_path).convert("RGB")
    garment = load_image(garment_path).convert("RGB")

    print(f"Dimensioni originali - Input: {image.size}, Mask: {mask.size}, Garment: {garment.size}")
    
    # Verifica e ridimensiona mask se necessario
    if mask.size != dim_target:
        print(f"ATTENZIONE: Mask ridimensionata da {mask.size} a {dim_target}")
        mask = mask.resize(dim_target)
    
    # Ridimensiona garment alle dimensioni target
    if garment.size != dim_target:
        print(f"Garment ridimensionato da {garment.size} a {dim_target}")
        garment = garment.resize(dim_target)
    
    print(f"Dimensioni finali uniformi: {dim_target[0]}x{dim_target[1]}")

    # Transform images
    image_tensor = image_transform(image)
    mask_tensor = mask_transform(mask)[:1]
    garment_tensor = image_transform(garment)

    # Verifica che i tensor abbiano le stesse dimensioni
    print(f"Shape tensors - Image: {image_tensor.shape}, Garment: {garment_tensor.shape}, Mask: {mask_tensor.shape}")

    # Create concatenated images
    inpaint_image = torch.cat([garment_tensor, image_tensor], dim=2)
    garment_mask = torch.zeros_like(mask_tensor)
    extended_mask = torch.cat([garment_mask, mask_tensor], dim=2)

    generator = torch.Generator(device="cuda").manual_seed(seed)
    
    result = pipe(
        height=dim_target[1],
        width=dim_target[0] * 2,
        image=inpaint_image,
        mask_image=extended_mask,
        num_inference_steps=num_steps,
        generator=generator,
        max_sequence_length=512,
        guidance_scale=guidance_scale,
        prompt=prompt,
    ).images[0]

    # Split and save results
    width = dim_target[0]
    height = dim_target[1]
    
    garment_result = result.crop((0, 0, width, height))
    tryon_result = result.crop((width, 0, width * 2, height))

    print(f"Risultato finale salvato con dimensioni: {width}x{height}")

    return garment_result, tryon_result

def main():
    parser = argparse.ArgumentParser(description='Run FLUX virtual try-on inference')
    parser.add_argument('--model', required=True, help='Model transformer path in Model directory')
    parser.add_argument('--lora', required=True, help='LoRA weights path in Lora directory')
    parser.add_argument('--prompt', required=True, help='Prompt in English')
    parser.add_argument('--image', required=True, help='Path to the model image (defines target dimensions)')
    parser.add_argument('--mask', required=True, help='Path to the agnostic mask (will be resized to match input)')
    parser.add_argument('--garment', required=True, help='Path to the garment image (will be resized to match input)')
    parser.add_argument('--output_garment', default='flux_inpaint_garment.png', help='Output path for garment result')
    parser.add_argument('--output_tryon', default='flux_inpaint_tryon.png', help='Output path for try-on result')
    parser.add_argument('--steps', type=int, default=50, help='Number of inference steps')
    parser.add_argument('--guidance_scale', type=float, default=30, help='Guidance scale')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')

    args = parser.parse_args()

    check_min_version("0.30.2")

    garment_result, tryon_result = run_inference(
        model=args.model,
        lora=args.lora,
        prompt=args.prompt,
        image_path=args.image,
        mask_path=args.mask,
        garment_path=args.garment,
        num_steps=args.steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
    )

    output_tryon_path = args.output_tryon
    tryon_result.save(output_tryon_path)
    print(f"\n✓ Successfully saved try-on image to: {output_tryon_path}")
    
    # Opzionale: salva anche il garment result se specificato
    if args.output_garment:
        garment_result.save(args.output_garment)
        print(f"✓ Successfully saved garment image to: {args.output_garment}")

if __name__ == "__main__":
    main()