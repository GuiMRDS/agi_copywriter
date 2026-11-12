from tools.videos import VIDEOS, salvar_transcricao

# Transcreve só os vídeos que ainda não estão em transcriptions/<criador>.json
for video in sorted(VIDEOS.glob("*/*")):
    if video.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
        print(salvar_transcricao(video).split(":")[0])
