import json, subprocess
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
out = Path("transcriptions"); out.mkdir(exist_ok=True)

for creator in Path("videos").iterdir():
    if not creator.is_dir(): continue
    result = {}
    for video in sorted(creator.glob("*.mp4")):
        audio = video.with_suffix(".mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vn", "-ac", "1", "-b:a", "64k", audio], check=True)
        result[video.name] = client.audio.transcriptions.create(file=(audio.name, audio.read_bytes()), model="whisper-large-v3").text
        audio.unlink()
        print(creator.name, video.name)
    (out / f"{creator.name}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
