import os
import json
import base64
from io import BytesIO
from PIL import Image
from ollama import generate

HISTORY_FILE = "story_history.json"
SAMPLES_DIR = "lora_samples"
INSTRUCTIONS_FILE = "next_reel_instructions.json"

def convert_image_to_base64(img_path):
    with Image.open(img_path) as img:
        buffered = BytesIO()
        img.convert("RGB").save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Ensure the folder exists to avoid unexpected crash points
if not os.path.exists(SAMPLES_DIR):
    os.makedirs(SAMPLES_DIR)

# Read current pipeline memory configuration
past_stories = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        try: 
            past_stories = json.load(f)
        except json.JSONDecodeError: 
            pass

next_chapter_num = len(past_stories) + 1

# Automatically scan and identify ANY valid image type regardless of format or casing
image_paths = []
if os.path.exists(SAMPLES_DIR):
    for filename in os.listdir(SAMPLES_DIR):
        full_path = os.path.join(SAMPLES_DIR, filename)
        # Skip directories
        if os.path.isdir(full_path):
            continue
        try:
            # Attempt to verify if PIL can recognize it as an image asset
            with Image.open(full_path) as test_img:
                test_img.verify()
            image_paths.append(full_path)
        except Exception:
            # Ignore non-image system files like .DS_Store or hidden logs
            pass

if not image_paths:
    raise FileNotFoundError(
        f"Could not locate any valid image files inside the '{SAMPLES_DIR}' directory. "
        f"Please verify files are uploaded. Detected directory contents: {os.listdir(SAMPLES_DIR)}"
    )

# Encode frames into structural vision inputs
encoded_images = [convert_image_to_base64(p) for p in image_paths]

prompt_text = (
    f"You are an anime series director. Analyze these attached reference images of a specific character. "
    f"This character is ALWAYS the main character of our series. Based on their design, clothes, style, and mood, "
    f"write a completely unique short anime reel storyboard for 'Episode {next_chapter_num}'.\n\n"
    f"CRITICAL: Do NOT repeat or use themes similar to these past episodes: {past_stories}.\n\n"
    f"Output your final response strictly as a clean raw JSON object without markdown wrappers or codeblocks. "
    f"Follow this structural format template exactly:\n"
    f"{{\n"
    f"  \"title\": \"Unique Title\",\n"
    f"  \"prompts\": [\n"
    f"    \"Stable Diffusion prompt for Frame 1 introducing the main character based on the images\",\n"
    f"    \"Stable Diffusion prompt for Frame 2 showing an action sequence or setting shift\",\n"
    f"    \"Stable Diffusion prompt for Frame 3 showing an intense close-up frame resolution\"\n"
    f"  ]\n"
    f"}}"
)

print(f"🧠 Querying Ollama qwen2.5vl:3b with {len(image_paths)} valid character asset frames...")
response = generate(
    model='qwen2.5vl:3b',
    prompt=prompt_text,
    images=encoded_images
)

output_text = response['response'].strip().strip("```json").strip("```")

try:
    story_payload = json.loads(output_text)
except Exception:
    # Error protection path to catch unformatted outputs
    story_payload = {
        "title": f"Anime Chapter Chronicles Vol {next_chapter_num}",
        "prompts": [line.strip() for line in output_text.split('\n') if len(line.strip()) > 10][:3]
    }

# Sync history memory and target execution file
past_stories.append(story_payload["title"])
with open(HISTORY_FILE, "w") as f:
    json.dump(past_stories, f, indent=4)

with open(INSTRUCTIONS_FILE, "w") as f:
    json.dump(story_payload, f, indent=4)

print(f"🎉 Completed Step 1. Prompt instruction file built for title: {story_payload['title']}")
