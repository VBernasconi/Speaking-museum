import os
import cv2
import argparse
import asyncio
import tempfile
import subprocess
import soundfile as sf
import numpy as np
import moviepy.editor as mp
from deepface import DeepFace
from kokoro import KPipeline

# ------------------------- CONFIG -------------------------

# Default image folder
IMAGE_FOLDER = "images"
OUTPUT_FACES = "output_faces"
OUTPUT_AUDIO = "output_audio"
OUTPUT_ANIMATION = "output_animation"
OUTPUT_VIDEO = "output_video"
OUTPUT_TEXT = "output_text"

for F in [OUTPUT_FACES, OUTPUT_AUDIO, OUTPUT_ANIMATION, OUTPUT_VIDEO, OUTPUT_TEXT]:
    os.makedirs(F, exist_ok=True)

HALLO_SCRIPT = os.path.join(os.getcwd(), "hallo", "scripts", "inference.py")

pipeline = KPipeline(lang_code="a")

# ------------------------- UTILITIES -------------------------

def safe_read(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def safe_write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def file_ok(path, min_size=500):
    return path and os.path.exists(path) and os.path.getsize(path) > min_size

# ------------------------- FACE DETECTION -------------------------

def detect_face(img_path):
    try:
        faces = DeepFace.extract_faces(img_path, detector_backend="mtcnn", enforce_detection=False)
        if not faces:
            return None
        f = faces[0]["facial_area"]
        return int(f["x"]), int(f["y"]), int(f["w"]), int(f["h"])
    except:
        return None

def crop_face_and_gender(image, bbox, base_name):
    x, y, w, h = bbox
    crop = image[y:y+h, x:x+w]

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, crop)
    a = DeepFace.analyze(tmp.name, actions=["gender"], enforce_detection=False)
    gender = a[0]["dominant_gender"]

    out_name = f"{base_name}_face.jpg"
    out_path = os.path.join(OUTPUT_FACES, out_name)
    cv2.imwrite(out_path, crop)
    return out_name, gender

# ------------------------- TEXT SPLITTING -------------------------

def split_text(text, max_chars=280):
    if len(text) <= max_chars:
        return [text]
    mid = len(text) // 2
    split = text.rfind(".", 0, mid)
    if split == -1:
        split = mid
    return [text[:split].strip(), text[split:].strip()]

# ------------------------- AUDIO GENERATION -------------------------

def generate_audio(text, gender, base_name):
    voice = "am_adam" if gender.lower().startswith("m") else "af_alloy"
    out_path = os.path.join(OUTPUT_AUDIO, f"{base_name}.wav")
    generator = pipeline(text, voice=voice)
    last_audio = None
    for _, _, audio in generator:
        last_audio = audio
    if last_audio is None:
        print("❌ Audio generation failed")
        return None
    sf.write(out_path, last_audio, 24000)
    return out_path

# ------------------------- HALLO ANIMATION -------------------------

def animate_face(face_file, audio_file, part_index):
    out_name = f"{os.path.splitext(face_file)[0]}_anim_part_{part_index}.mp4"
    out_path = os.path.join(OUTPUT_ANIMATION, out_name)

    cmd = [
        "python", HALLO_SCRIPT,
        "--source_image", f"../{OUTPUT_FACES}/{face_file}",
        "--driving_audio", f"../{audio_file}",
        "--output", f"../{out_path}",
        "--pose_weight", "0.5",
        "--face_weight", "1.0",
        "--lip_weight", "1.2",
        "--face_expand_ratio", "1.2",
        "--checkpoint", "None"
    ]

    cwd = os.getcwd()
    try:
        os.chdir("hallo")
        r = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.chdir(cwd)

    if r.returncode != 0:
        print("❌ Hallo failed:", r.stderr)
        return None
    return out_path

# ------------------------- MERGE ANIMATION WITH IMAGE -------------------------

def merge_face(animation_path, audio_path, img_path, bbox, part_index, base_name):
    if not file_ok(animation_path):
        return None
    img = cv2.imread(img_path)
    if img is None:
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    x, y, w, h = bbox
    cap = cv2.VideoCapture(animation_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    frames = []

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        resized = cv2.resize(frame, (w, h))
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        c = img.copy()
        c[y:y+h, x:x+w] = resized
        frames.append(c)
    cap.release()

    if not frames:
        return None

    clip = mp.ImageSequenceClip(frames, fps=fps)
    if file_ok(audio_path, 100):
        clip = clip.set_audio(mp.AudioFileClip(audio_path))

    out_path = os.path.join(OUTPUT_VIDEO, f"{base_name}_merged_part_{part_index}.mp4")
    clip.write_videofile(out_path, codec="libx264", audio_codec="aac")
    return out_path

# ------------------------- CONCATENATE FINAL VIDEO -------------------------

def concatenate_videos(parts, final_path):
    valid = [p for p in parts if file_ok(p)]
    if not valid:
        print("❌ No valid video parts to concatenate")
        return None
    else:
        print("Concatenating together:")
        for v in valid:
            print(v)
    clips = [mp.VideoFileClip(v) for v in valid]
    final = mp.concatenate_videoclips(clips, method="compose")
    final.write_videofile(final_path, codec="libx264", audio_codec="aac")
    return final_path

# ------------------------- MAIN PIPELINE -------------------------

async def process_image(img_file, desc_folder):
    global IMAGE_FOLDER
    base = os.path.splitext(img_file)[0]
    img_path = os.path.join(IMAGE_FOLDER, img_file)
    text_path = os.path.join(desc_folder, base + ".txt")
    text = safe_read(text_path)
    if not text:
        print(f"⚠️ Missing text for {base}")
        return
    print(f"\n🚀 Processing {base}")
    bbox = detect_face(img_path)
    if not bbox:
        print(f"❌ No face detected in {base}")
        return
    image = cv2.imread(img_path)
    face_file, gender = crop_face_and_gender(image, bbox, base)
    parts = split_text(text)
    merged_parts = []

    for idx, chunk in enumerate(parts, 1):
        chunk_txt = os.path.join(OUTPUT_TEXT, f"{base}_chunk_{idx}.txt")
        safe_write(chunk_txt, chunk)
        audio_path = generate_audio(chunk, gender, f"{base}_audio_{idx}")
        if not audio_path:
            continue
        anim_path = animate_face(face_file, audio_path, idx)
        if not anim_path:
            continue
        merged_path = merge_face(anim_path, audio_path, img_path, bbox, idx, base)
        if merged_path:
            merged_parts.append(merged_path)

    if merged_parts:
        final_path = os.path.join(OUTPUT_VIDEO, f"{base}_FINAL.mp4")
        concatenate_videos(merged_parts, final_path)

# ------------------------- MAIN ENTRYPOINT -------------------------

def main(args):
    global IMAGE_FOLDER
    if args.image_folder:
        IMAGE_FOLDER = args.image_folder
    print(f"📂 Using image folder: {IMAGE_FOLDER}")
    for f in os.listdir(IMAGE_FOLDER):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            asyncio.run(process_image(f, args.desc))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face animation pipeline (no Ollama)")
    parser.add_argument("--image_folder", required=False, help="Path to folder with images.")
    parser.add_argument("--desc", required=True, help="Folder with description .txt files.")
    args = parser.parse_args()
    main(args)
