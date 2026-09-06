import os
import gc
import json
import torch
from PIL import Image
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

HISTORY_FILE = "story_history.json"
SAMPLES_DIR = "lora_samples"
INSTRUCTIONS_FILE = "next_reel_instructions.json"

# ==========================================
# STEP 1: LOAD REEL HISTORY (MEMORY LAYER)
# ==========================================
def load_story_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_story_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# ==========================================
# STEP 2: LOAD QWEN2.5-VL-3B LOGIC (LOW RAM)
# ==========================================
def generate_story_with_vision():
    past_stories = load_story_history()
    next_chapter_num = len(past_stories) + 1
    
    # Locate PNG files in your repository
    image_paths = [os.path.join(SAMPLES_DIR, f) for f in os.listdir(SAMPLES_DIR) if f.lower().endswith('.png')]
    
    if not image_paths:
        raise FileNotFoundError(f"No PNG images found in the '{SAMPLES_DIR}' folder. Please commit images first!")

    print(f"🔍 Found {len(image_paths)} LoRA reference images. Loading Qwen2.5-VL-3B-Instruct...")

    # Load Model with strict memory limits for free GitHub Actions Runner (<7GB RAM)
    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    
    processor = AutoProcessor.from_pretrained(model_id)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.float32, # CPU friendly precision
        device_map="cpu",           # Force execution completely onto system RAM
        low_cpu_mem_usage=True      # Optimization to prevent RAM spikes during load
    )

    # Load your images into memory
    loaded_images = [Image.open(img_path).convert("RGB") for img_path in image_paths]

    # Create a prompt telling the model that this specific character is ALWAYS the main character
    prompt_text = (
        f"You are an anime series director. Analyze these attached reference images of a specific character. "
        f"This character is ALWAYS the main character of our series. Based on their design, clothes, style, and mood, "
        f"write a completely unique, highly descriptive short anime reel storyboard for 'Episode {next_chapter_num}'.\n\n"
        f"CRITICAL: Do NOT repeat or use themes similar to these past episodes: {past_stories}.\n\n"
        f"Output your final response strictly as a clean JSON object. Do not include markdown codeblocks around the JSON. "
        f"Follow this exact format structure:\n"
        f"{{\n"
        f"  \"title\": \"A short creative title for this unique sequence\",\n"
        f"  \"prompts\": [\n"
        f"    \"Detailed Stable Diffusion prompt for Frame 1 introducing the main character, describing actions and background elements based on the images\",\n"
        f"    \"Detailed Stable Diffusion prompt for Frame 2 showing a structural action progression or scene change\",\n"
        f"    \"Detailed Stable Diffusion prompt for Frame 3 showing a dramatic or expressive close-up resolution\"\n"
        f"  ]\n"
        f"}}"
    )

    # Prepare inputs for the multi-modal model
    # We pass the text prompt along with the array of loaded images
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                *[{"type": "image", "image": img} for img in loaded_images]
            ]
        }
    ]

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=loaded_images, padding=True, return_tensors="pt")

    print("🧠 Qwen AI is analyzing images and composing the sequence story...")
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=512)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

    # Clean potential formatting wrapper quirks out of the raw response string
    output_text = output_text.strip().strip("```json").strip("```")
    
    try:
        story_payload = json.loads(output_text)
        print(f"🎬 New Story Successfully Penned: {story_payload['title']}")
    except Exception as e:
        print(f"⚠️ Failed parsing strict JSON layout from AI. Falling back to structured extraction. Raw output: {output_text}")
        # Secure fallback structure if model outputs loose text layout
        story_payload = {
            "title": f"Anime Chapter Chronicles Vol {next_chapter_num}",
            "prompts": [line.strip() for line in output_text.split('\n') if len(line.strip()) > 10][:4]
        }

    # Update persistent memory log
    past_stories.append(story_payload["title"])
    save_story_history(past_stories)

    # Save output data target layout for Kaggle to execute next
    with open(INSTRUCTIONS_FILE, "w") as f:
        json.dump(story_payload, f, indent=4)

    # Explicit memory wiping sequence
    del model, processor, inputs, generated_ids
    gc.collect()

if __name__ == "__main__":
    generate_story_with_vision()
