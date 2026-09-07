# import os
# import json
# import base64
# from io import BytesIO
# from PIL import Image
# from ollama import generate

# HISTORY_FILE = "story_history.json"
# SAMPLES_DIR = "lora_samples"
# INSTRUCTIONS_FILE = "next_reel_instructions.json"

# def convert_and_resize_image_to_base64(img_path, max_size=448):
#     """
#     Resizes images dynamically to fit safely within vision token constraints.
#     Large resolution images inflate the context window size exponentially.
#     """
#     with Image.open(img_path) as img:
#         img = img.convert("RGB")
#         # Scale image down smoothly if it exceeds max size limit
#         img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG", quality=85)
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')

# # Ensure the folder exists to avoid unexpected crash points
# if not os.path.exists(SAMPLES_DIR):
#     os.makedirs(SAMPLES_DIR)

# # Read current pipeline memory configuration
# past_stories = []
# if os.path.exists(HISTORY_FILE):
#     with open(HISTORY_FILE, "r") as f:
#         try: 
#             past_stories = json.load(f)
#         except json.JSONDecodeError: 
#             pass

# next_chapter_num = len(past_stories) + 1

# # Automatically scan and identify ANY valid image type regardless of format or casing
# image_paths = []
# if os.path.exists(SAMPLES_DIR):
#     for filename in os.listdir(SAMPLES_DIR):
#         full_path = os.path.join(SAMPLES_DIR, filename)
#         if os.path.isdir(full_path):
#             continue
#         try:
#             with Image.open(full_path) as test_img:
#                 test_img.verify()
#             image_paths.append(full_path)
#         except Exception:
#             pass

# if not image_paths:
#     raise FileNotFoundError(
#         f"Could not locate any valid image files inside the '{SAMPLES_DIR}' directory. "
#     )

# # Encode frames into clean, token-efficient visual inputs
# encoded_images = [convert_and_resize_image_to_base64(p) for p in image_paths]

# prompt_text = (
#     f"You are an anime series director. Analyze these attached reference images of a specific character. "
#     f"This character is ALWAYS the main character of our series. Based on their design, clothes, style, and mood, "
#     f"write a completely unique short anime reel storyboard for 'Episode {next_chapter_num}'.\n\n"
#     f"CRITICAL: Do NOT repeat or use themes similar to these past episodes: {past_stories}.\n\n"
#     f"Output your final response strictly as a clean raw JSON object without markdown wrappers or codeblocks. "
#     f"Follow this structural format template exactly:\n"
#     f"{{\n"
#     f"  \"title\": \"Unique Title\",\n"
#     f"  \"prompts\": [\n"
#     f"    \"Stable Diffusion prompt for Frame 1 introducing the main character based on the images\",\n"
#     f"    \"Stable Diffusion prompt for Frame 2 showing an action sequence or setting shift\",\n"
#     f"    \"Stable Diffusion prompt for Frame 3 showing an intense close-up frame resolution\"\n"
#     f"  ]\n"
#     f"}}"
# )

# print(f"🧠 Querying Ollama qwen2.5vl:3b with {len(image_paths)} resized character asset frames...")

# # Expand options context window configuration rule to 16k tokens explicitly
# response = generate(
#     model='qwen2.5vl:3b',
#     prompt=prompt_text,
#     images=encoded_images,
#     options={
#         "num_ctx": 16384  # Increases standard context size threshold to prevent 400 errors
#     }
# )

# output_text = response['response'].strip().strip("```json").strip("```")

# try:
#     story_payload = json.loads(output_text)
# except Exception:
#     story_payload = {
#         "title": f"Anime Chapter Chronicles Vol {next_chapter_num}",
#         "prompts": [line.strip() for line in output_text.split('\n') if len(line.strip()) > 10][:3]
#     }

# # Sync history memory and target execution file
# past_stories.append(story_payload["title"])
# with open(HISTORY_FILE, "w") as f:
#     json.dump(past_stories, f, indent=4)

# with open(INSTRUCTIONS_FILE, "w") as f:
#     json.dump(story_payload, f, indent=4)

# print(f"🎉 Completed Step 1. Prompt instruction file built for title: {story_payload['title']}")











import os
import json
import base64
from io import BytesIO
from PIL import Image
from ollama import generate

HISTORY_FILE = "story_history.json"
SAMPLES_DIR = "lora_samples"
INSTRUCTIONS_FILE = "next_reel_instructions.json"

def convert_and_resize_image_to_base64(img_path, max_size=512):
    with Image.open(img_path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=90)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Check files
if not os.path.exists(SAMPLES_DIR):
    os.makedirs(SAMPLES_DIR)

past_stories = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        try: past_stories = json.load(f)
        except json.JSONDecodeError: pass

next_chapter_num = len(past_stories) + 1

# Grab the first available image file inside your lora_samples folder
image_paths = []
for filename in os.listdir(SAMPLES_DIR):
    full_path = os.path.join(SAMPLES_DIR, filename)
    if os.path.isdir(full_path):
        continue
    try:
        with Image.open(full_path) as test_img:
            test_img.verify()
        image_paths.append(full_path)
    except Exception:
        pass

if not image_paths:
    raise FileNotFoundError(f"Please place exactly one character image inside the '{SAMPLES_DIR}' folder.")

# Use only the absolute first image found for razor-sharp character analysis
target_character_image = image_paths[0]
encoded_image = convert_and_resize_image_to_base64(target_character_image)

# High-fidelity directional storytelling prompt designed for Stable Diffusion generation
prompt_text = f"""
You are an expert anime director and storyboard artist. Analyze the attached reference image of our main character.
Look at their gender, hair color, facial features, facial expression, and outfit style. They are ALWAYS the central figure.

Task:
Write a meaningful, 10-second anime reel sequence split into 4 core sequential scenes.
Because our pipeline renders at 8 frames per second (FPS), your job is to output exactly 80 prompts in total (20 continuous progressive sub-prompts for each of the 4 main scenes) so that the final video shows smooth, meaningful movement without sudden jumps.

Ensure the theme avoids anything mentioned in our history log: {past_stories}.

You MUST output your final answer strictly as a clean, raw JSON object with NO markdown, NO triple backticks (```), and NO additional conversational text. 

Follow this exact structural template:
{{
  "title": "Anime Chronicles Episode {next_chapter_num}",
  "prompts": [
    "Scene 1 Start (Frame 1): 1girl/1boy [describe character physical features from image], standing in an open meadow, wind blowing their hair, looking up at a cloudy sky, anime style, masterpiece",
    "Scene 1 Progress (Frame 2): 1girl/1boy [describe features], in a meadow, slowly turning their head towards the camera, gentle wind, shifting background clouds, anime style",
    "...(continue listing progressive movements frame-by-frame up to Frame 80)..."
  ]
}}
"""

print(f"🧠 Analyzing main character image: {os.path.basename(target_character_image)}")
print(f"🎬 Composing an 80-frame (10 second at 8 FPS) progressive storyboard sequence via Qwen2.5-VL...")

response = generate(
    model='qwen2.5vl:3b',
    prompt=prompt_text,
    images=[encoded_image],
    options={
        "num_ctx": 16384,
        "temperature": 0.7
    }
)

output_text = response['response'].strip()

# Stripping common markdown wrappers just in case the model inserts them out of habit
if output_text.startswith("```"):
    output_text = output_text.split("\n", 1)[1]
if output_text.endswith("```"):
    output_text = output_text.rsplit("\n", 1)[0]
output_text = output_text.strip("```json").strip("```").strip()

try:
    story_payload = json.loads(output_text)
    # Ensure it parsed clean and contains valid list formatting
    if not isinstance(story_payload.get("prompts"), list):
        raise ValueError("Prompts element must be a valid array list structure.")
except Exception:
    print("⚠️ JSON layout formatting anomaly detected from AI. Triggering robust structural fallback extraction...")
    # Clean fallback layout generation so your script NEVER crashes out on the GitHub Actions side
    lines = [line.strip().replace('"', '').strip(',') for line in output_text.split('\n') if len(line.strip()) > 15]
    story_payload = {
        "title": f"Anime Saga Chapter Vol {next_chapter_num}",
        "prompts": lines[:80] if len(lines) >= 80 else lines + [f"Main character action continuation frame, anime style, masterpiece"] * (80 - len(lines))
    }

# Save memory history and the instruction blueprint file for Kaggle
past_stories.append(story_payload["title"])
with open(HISTORY_FILE, "w") as f:
    json.dump(past_stories, f, indent=4)

with open(INSTRUCTIONS_FILE, "w") as f:
    json.dump(story_payload, f, indent=4)

print(f"🎉 Success! 'next_reel_instructions.json' successfully saved with {len(story_payload['prompts'])} structural image rendering prompts.")
