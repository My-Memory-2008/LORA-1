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











# import os
# import json
# import base64
# from io import BytesIO
# from PIL import Image
# from ollama import generate

# HISTORY_FILE = "story_history.json"
# SAMPLES_DIR = "lora_samples"
# INSTRUCTIONS_FILE = "next_reel_instructions.json"

# def convert_and_resize_image_to_base64(img_path, max_size=512):
#     with Image.open(img_path) as img:
#         img = img.convert("RGB")
#         img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG", quality=90)
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')

# # Check files
# if not os.path.exists(SAMPLES_DIR):
#     os.makedirs(SAMPLES_DIR)

# past_stories = []
# if os.path.exists(HISTORY_FILE):
#     with open(HISTORY_FILE, "r") as f:
#         try: past_stories = json.load(f)
#         except json.JSONDecodeError: pass

# next_chapter_num = len(past_stories) + 1

# # Grab the first available image file inside your lora_samples folder
# image_paths = []
# for filename in os.listdir(SAMPLES_DIR):
#     full_path = os.path.join(SAMPLES_DIR, filename)
#     if os.path.isdir(full_path):
#         continue
#     try:
#         with Image.open(full_path) as test_img:
#             test_img.verify()
#         image_paths.append(full_path)
#     except Exception:
#         pass

# if not image_paths:
#     raise FileNotFoundError(f"Please place exactly one character image inside the '{SAMPLES_DIR}' folder.")

# # Use only the absolute first image found for razor-sharp character analysis
# target_character_image = image_paths[0]
# encoded_image = convert_and_resize_image_to_base64(target_character_image)

# # High-fidelity directional storytelling prompt designed for Stable Diffusion generation
# prompt_text = f"""
# You are an expert anime director and storyboard artist. Analyze the attached reference image of our main character.
# Look at their gender, hair color, facial features, facial expression, and outfit style. They are ALWAYS the central figure.

# Task:
# Write a meaningful, 10-second anime reel sequence split into 4 core sequential scenes.
# Because our pipeline renders at 8 frames per second (FPS), your job is to output exactly 80 prompts in total (20 continuous progressive sub-prompts for each of the 4 main scenes) so that the final video shows smooth, meaningful movement without sudden jumps.

# Ensure the theme avoids anything mentioned in our history log: {past_stories}.

# You MUST output your final answer strictly as a clean, raw JSON object with NO markdown, NO triple backticks (```), and NO additional conversational text. 

# Follow this exact structural template:
# {{
#   "title": "Anime Chronicles Episode {next_chapter_num}",
#   "prompts": [
#     "Scene 1 Start (Frame 1): 1girl/1boy [describe character physical features from image], standing in an open meadow, wind blowing their hair, looking up at a cloudy sky, anime style, masterpiece",
#     "Scene 1 Progress (Frame 2): 1girl/1boy [describe features], in a meadow, slowly turning their head towards the camera, gentle wind, shifting background clouds, anime style",
#     "...(continue listing progressive movements frame-by-frame up to Frame 80)..."
#   ]
# }}
# """

# print(f"🧠 Analyzing main character image: {os.path.basename(target_character_image)}")
# print(f"🎬 Composing an 80-frame (10 second at 8 FPS) progressive storyboard sequence via Qwen2.5-VL...")

# response = generate(
#     model='qwen2.5vl:3b',
#     prompt=prompt_text,
#     images=[encoded_image],
#     options={
#         "num_ctx": 16384,
#         "temperature": 0.7
#     }
# )

# output_text = response['response'].strip()

# # Stripping common markdown wrappers just in case the model inserts them out of habit
# if output_text.startswith("```"):
#     output_text = output_text.split("\n", 1)[1]
# if output_text.endswith("```"):
#     output_text = output_text.rsplit("\n", 1)[0]
# output_text = output_text.strip("```json").strip("```").strip()

# try:
#     story_payload = json.loads(output_text)
#     # Ensure it parsed clean and contains valid list formatting
#     if not isinstance(story_payload.get("prompts"), list):
#         raise ValueError("Prompts element must be a valid array list structure.")
# except Exception:
#     print("⚠️ JSON layout formatting anomaly detected from AI. Triggering robust structural fallback extraction...")
#     # Clean fallback layout generation so your script NEVER crashes out on the GitHub Actions side
#     lines = [line.strip().replace('"', '').strip(',') for line in output_text.split('\n') if len(line.strip()) > 15]
#     story_payload = {
#         "title": f"Anime Saga Chapter Vol {next_chapter_num}",
#         "prompts": lines[:80] if len(lines) >= 80 else lines + [f"Main character action continuation frame, anime style, masterpiece"] * (80 - len(lines))
#     }

# # Save memory history and the instruction blueprint file for Kaggle
# past_stories.append(story_payload["title"])
# with open(HISTORY_FILE, "w") as f:
#     json.dump(past_stories, f, indent=4)

# with open(INSTRUCTIONS_FILE, "w") as f:
#     json.dump(story_payload, f, indent=4)

# print(f"🎉 Success! 'next_reel_instructions.json' successfully saved with {len(story_payload['prompts'])} structural image rendering prompts.")
















# import os
# import json
# import base64
# from io import BytesIO
# from PIL import Image
# from ollama import generate

# HISTORY_FILE = "story_history.json"
# SAMPLES_DIR = "lora_samples"
# INSTRUCTIONS_FILE = "next_reel_instructions.json"

# def convert_and_resize_image_to_base64(img_path, max_size=512):
#     with Image.open(img_path) as img:
#         img = img.convert("RGB")
#         img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG", quality=90)
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')

# # Ensure directories exist
# if not os.path.exists(SAMPLES_DIR):
#     os.makedirs(SAMPLES_DIR)

# # Read current pipeline history memory
# past_episodes = []
# if os.path.exists(HISTORY_FILE):
#     with open(HISTORY_FILE, "r") as f:
#         try: 
#             past_episodes = json.load(f)
#         except json.JSONDecodeError: 
#             pass

# next_chapter_num = len(past_episodes) + 1

# # Grab the first available image inside the folder
# image_paths = []
# for filename in os.listdir(SAMPLES_DIR):
#     full_path = os.path.join(SAMPLES_DIR, filename)
#     if os.path.isdir(full_path):
#         continue
#     try:
#         with Image.open(full_path) as test_img:
#             test_img.verify()
#         image_paths.append(full_path)
#     except Exception:
#         pass

# if not image_paths:
#     raise FileNotFoundError(f"Please place exactly one main character image inside the '{SAMPLES_DIR}' folder.")

# target_character_image = image_paths[0]
# encoded_image = convert_and_resize_image_to_base64(target_character_image)

# # 🌟 FIXED: Safe list conversion logic handles both old raw strings and new objects 🌟
# past_titles = []
# past_summaries = []

# for ep in past_episodes:
#     if isinstance(ep, dict):
#         past_titles.append(ep.get("title", ""))
#         past_summaries.append(ep.get("summary", ""))
#     elif isinstance(ep, str):
#         # Gracefully handle residual legacy text items from the prior script versions
#         past_titles.append(ep)
#         past_summaries.append("Legacy recorded episode run.")

# # Clear instructions telling the AI who the character is, what the trigger terms are, and how to structure memory
# prompt_text = f"""
# You are an expert anime director. Analyze the attached reference image of our main character. 
# The character is Yae Miko from Genshin Impact. She is the absolute main character of our story reel.
# When generating image prompts, always include her core descriptive trigger keywords: "yae_miko, 1girl, pink hair, fox ears, purple eyes, hair ornament, japanese clothes, shrine maiden outfit".

# Task:
# Write a meaningful, logical short anime reel storyboard for 'Episode {next_chapter_num}'.
# The video plays at 8 frames per second (FPS) and must run for exactly 10 seconds. You must output exactly 80 total progressive prompts (representing frame 1 to frame 80) mapping smooth micro-movements, scene progressions, and facial expressions so the story makes logical sense over 10 seconds.

# Ensure the story theme and events are completely different from past runs:
# Past Titles: {past_titles}
# Past Summaries: {past_summaries}

# You MUST output your final answer strictly as a clean, raw JSON object with NO markdown codeblocks, NO triple backticks (```), and NO conversational text.

# Follow this structural format exactly:
# {{
#   "title": "Anime Chronicles Episode {next_chapter_num}",
#   "summary": "Write a detailed single-paragraph summary of what happens in this 10-second story scene so a human can easily read the history.",
#   "prompts": [
#     "yae_miko, 1girl, pink hair, fox ears, purple eyes, hair ornament, japanese clothes, standing in a grand shrine courtyard, looking up thoughtfully at falling cherry blossom petals, wind blowing hair, masterpiece, anime style",
#     "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, in shrine courtyard, slowly turning head toward camera with an enigmatic smile, petals floating, masterpiece, anime style",
#     "...(continue mapping progressive frame adjustments up to frame 80)..."
#   ]
# }}
# """

# print(f"🧠 Analyzing main character image: {os.path.basename(target_character_image)} as Yae Miko...")
# print(f"🎬 Generating 80 progressive frames and story summary via Qwen2.5-VL...")

# response = generate(
#     model='qwen2.5vl:3b',
#     prompt=prompt_text,
#     images=[encoded_image],
#     options={
#         "num_ctx": 16384,
#         "temperature": 0.7
#     }
# )

# output_text = response['response'].strip()

# # Strip any unexpected markdown formatting
# if output_text.startswith("```"):
#     output_text = output_text.split("\n", 1)[1]
# if output_text.endswith("```"):
#     output_text = output_text.rsplit("\n", 1)[0]
# output_text = output_text.strip("```json").strip("```").strip()

# try:
#     story_payload = json.loads(output_text)
#     if not isinstance(story_payload.get("prompts"), list):
#         raise ValueError("Prompts element must be a valid array list structure.")
# except Exception:
#     print("⚠️ JSON layout formatting anomaly detected from AI. Triggering robust structural fallback extraction...")
#     lines = [line.strip().replace('"', '').strip(',') for line in output_text.split('\n') if len(line.strip()) > 15]
#     story_payload = {
#         "title": f"Anime Saga Chapter Vol {next_chapter_num}",
#         "summary": "Yae Miko reflects deeply in a beautiful, changing environment as energy manifests around her.",
#         "prompts": lines[:80] if len(lines) >= 80 else lines + [f"yae_miko, 1girl, pink hair, fox ears, japanese clothes, continuing action frame, masterpiece, anime style"] * (80 - len(lines))
#     }

# # Save human-readable structural metadata into the history tracking log
# history_entry = {
#     "episode": next_chapter_num,
#     "title": story_payload.get("title", f"Episode {next_chapter_num}"),
#     "summary": story_payload.get("summary", "A beautiful narrative sequence featuring Yae Miko.")
# }
# past_episodes.append(history_entry)

# with open(HISTORY_FILE, "w") as f:
#     json.dump(past_episodes, f, indent=4)

# # Save the raw prompt instructions separate for the Kaggle engine run step
# with open(INSTRUCTIONS_FILE, "w") as f:
#     json.dump(story_payload, f, indent=4)

# print(f"🎉 Success! Story details logged. 'next_reel_instructions.json' successfully saved with {len(story_payload['prompts'])} prompts.")














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

# Ensure directories exist
if not os.path.exists(SAMPLES_DIR):
    os.makedirs(SAMPLES_DIR)

# Read current pipeline history memory
past_episodes = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        try: 
            past_episodes = json.load(f)
        except json.JSONDecodeError: 
            pass

next_chapter_num = len(past_episodes) + 1

# Grab the first available image inside the folder
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
    raise FileNotFoundError(f"Please place exactly one main character image inside the '{SAMPLES_DIR}' folder.")

target_character_image = image_paths[0]
encoded_image = convert_and_resize_image_to_base64(target_character_image)

# Safe list conversion logic handles both old raw strings and new objects
past_titles = []
past_summaries = []
for ep in past_episodes:
    if isinstance(ep, dict):
        past_titles.append(ep.get("title", ""))
        past_summaries.append(ep.get("summary", ""))
    elif isinstance(ep, str):
        past_titles.append(ep)
        past_summaries.append("Legacy recorded episode run.")

# Ask the model for 10 highly distinct, second-by-second beats
prompt_text = f"""
You are an expert anime director. Analyze the attached reference image of our main character. 
The character is Yae Miko from Genshin Impact. She is the absolute main character of our story reel.
When generating image prompts, always include her core descriptive trigger keywords: "yae_miko, 1girl, pink hair, fox ears, purple eyes, hair ornament, japanese clothes, shrine maiden outfit".

Task:
Write a meaningful, logical 10-second short anime reel storyboard for 'Episode {next_chapter_num}'.
You must output exactly 10 detailed key scene prompts—one prompt representing each single second of the video. Describe the environment, lighting, and explicit action changes for each second.

Ensure the story theme and events are completely different from past runs:
Past Titles: {past_titles}
Past Summaries: {past_summaries}

You MUST output your final answer strictly as a clean, raw JSON object with NO markdown codeblocks, NO triple backticks (```), and NO conversational text.

Follow this structural format exactly:
{{
  "title": "Anime Chronicles Episode {next_chapter_num}",
  "summary": "Write a detailed single-paragraph summary of what happens in this 10-second story scene so a human can easily read the history.",
  "key_seconds": [
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, hair ornament, japanese clothes, standing in a grand shrine courtyard, looking up thoughtfully at falling cherry blossom petals, wind blowing hair, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, slowly turning head toward camera with an enigmatic smile, petals floating, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, raising her hand to catch a glowing electro talisman, energy crackling around her fingers, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, talisman glowing brightly, eyes narrowing with confidence, magical aura expansion, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, close up focus on her smile, ancient sacred sakura tree glowing in the background, night sky falling, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, walking gracefully toward the sacred tree, fox spirits appearing as soft lights, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, turning back over her shoulder, waving her hand gently, inviting look, twilight sky, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, floating fox spirits gathering around her, dynamic magical lighting, pink and purple hues, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, closing her eyes peacefully, energy gently fading back into the air, calm expression, masterpiece, anime style",
    "yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, opening eyes looking directly at camera, slight smirk, beautiful cinematic shot, final scene, masterpiece, anime style"
  ]
}}
"""

print(f"🧠 Analyzing main character image: {os.path.basename(target_character_image)} as Yae Miko...")
print(f"🎬 Generating 10 second-by-second story beats via Qwen2.5-VL...")

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

# Strip any unexpected markdown formatting
if output_text.startswith("```"):
    output_text = output_text.split("\n", 1)[1] if "\n" in output_text else output_text
if output_text.endswith("```"):
    output_text = output_text.rsplit("\n", 1)[0] if "\n" in output_text else output_text
output_text = output_text.strip("```json").strip("```").strip()

try:
    story_payload = json.loads(output_text)
    key_beats = story_payload.get("key_seconds", [])
    if not isinstance(key_beats, list) or len(key_beats) < 5:
        raise ValueError("Invalid array list structure generated.")
except Exception:
    print("⚠️ JSON layout formatting anomaly detected. Triggering structural line extraction...")
    lines = [line.strip().replace('"', '').strip(',') for line in output_text.split('\n') if len(line.strip()) > 20]
    key_beats = lines[:10]
    story_payload = {
        "title": f"Anime Saga Chapter Vol {next_chapter_num}",
        "summary": "Yae Miko channels spiritual energies and controls talismans around the Grand Narukami Shrine.",
    }

# Ensure we have exactly 10 core beats to scale from
if len(key_beats) < 10:
    # If the AI under-generated, fill remaining slots with baseline descriptive continuations
    padding_needed = 10 - len(key_beats)
    key_beats += [f"yae_miko, 1girl, pink hair, fox ears, purple eyes, japanese clothes, shrine maiden outfit, continuing action scene, cinematic lighting, masterpiece, anime style"] * padding_needed

# ==========================================
# STEP 3: PROGRAMMATIC 8 FPS SCALING ENGINE
# ==========================================
print("⚡ Programmatic Scaling Engine: Expanding 10 story seconds into 80 smooth continuous frames...")
final_80_prompts = []

# Frame-by-frame direction modifiers to simulate continuous camera shifts and actions
# 8 variations per second to loop seamlessly
micro_modifiers = [
    "subtle camera zoom in, clothing flowing",
    "slight head tilt, eyes tracking movement",
    "hair drifting softly, micro expression shift",
    "camera slowly panning right, dynamic wind animation",
    "subtle hand movement, lighting shimmer effect",
    "camera zooming out gently, background particle movement",
    "blinking eyes slowly, soft shadow adjustment",
    "camera angle tilting upwards slightly, focus deepening"
]

# Loop through each of the 10 seconds, creating 8 progressive frames for each second
for second_idx, base_prompt in enumerate(key_beats[:10]):
    for frame_idx in range(8):
        modifier = micro_modifiers[frame_idx]
        # Clean potential end tags to attach modifier beautifully
        clean_base = base_prompt.replace(", masterpiece, anime style", "").replace(", anime style, masterpiece", "")
        full_frame_prompt = f"{clean_base}, {modifier}, masterpiece, anime style"
        final_80_prompts.append(full_frame_prompt)

# Build unified output dataset
final_instructions = {
    "title": story_payload.get("title", f"Episode {next_chapter_num}"),
    "summary": story_payload.get("summary", "A narrative sequence featuring Yae Miko."),
    "prompts": final_80_prompts
}

# Save human-readable structural metadata into the history tracking log
history_entry = {
    "episode": next_chapter_num,
    "title": final_instructions["title"],
    "summary": final_instructions["summary"]
}
past_episodes.append(history_entry)

with open(HISTORY_FILE, "w") as f:
    json.dump(past_episodes, f, indent=4)

# Save the full 80-prompt package for the Kaggle image generator
with open(INSTRUCTIONS_FILE, "w") as f:
    json.dump(final_instructions, f, indent=4)

print(f"🎉 Success! 'next_reel_instructions.json' successfully saved with exactly {len(final_80_prompts)} highly detailed, animated frame prompts!")
