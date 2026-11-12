from tools.transcripts import importar_json
from tools.videos import VIDEOS, salvar_transcricao

# Importa os antigos transcriptions/*.json (se existirem) para o banco data/transcricoes.db
print(f"{importar_json()} transcrições importadas dos JSON")

# Transcreve só os vídeos de videos/<criador>/ que ainda não estão no banco
for video in sorted(VIDEOS.glob("*/*")):
    if video.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
        print(salvar_transcricao(video).split(":")[0])
