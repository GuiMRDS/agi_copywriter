import hashlib, json, re, subprocess
from pathlib import Path
from typing import Optional, Sequence
from dotenv import load_dotenv
from groq import Groq
from agno.media import Video

load_dotenv(Path(__file__).parent.parent / ".env")
VIDEOS = Path(__file__).parent.parent / "videos"
TRANSCRICOES = Path(__file__).parent.parent / "transcriptions"


def _pasta(criador: str) -> Path:
    nome = re.sub(r"[^a-z0-9_-]", "", criador.strip().lower().replace(" ", ""))
    if not nome:
        raise ValueError(f"Nome de criador inválido: '{criador}'")
    pasta = VIDEOS / nome
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def salvar_transcricao(video: Path) -> str:
    """Transcreve um vídeo de videos/<criador>/ e adiciona em transcriptions/<criador>.json (se ainda não estiver lá)."""
    arquivo = TRANSCRICOES / f"{video.parent.name}.json"
    dados = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    if video.name in dados:
        return f"{video.name} já estava transcrito em {video.parent.name}."
    audio = video.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vn", "-ac", "1", "-b:a", "64k", audio], check=True)
    try:
        dados[video.name] = Groq().audio.transcriptions.create(file=(audio.name, audio.read_bytes()), model="whisper-large-v3").text.strip()
    finally:
        audio.unlink(missing_ok=True)
    TRANSCRICOES.mkdir(exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"Adicionado a {video.parent.name} como Transcript {len(dados)}: {dados[video.name][:200]}..."


def adicionar_video_por_link(criador: str, link: str) -> str:
    """Baixa um vídeo (Reels, TikTok, YouTube Shorts...) pelo link, transcreve e adiciona aos exemplos do criador.

    Args:
        criador: ex: "kallaway". Pode ser um criador novo.
        link: URL do vídeo.
    """
    import yt_dlp

    try:
        opcoes = {"outtmpl": str(_pasta(criador) / "%(id)s.%(ext)s"), "format": "best[ext=mp4]/best", "quiet": True, "noprogress": True}
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            video = Path(ydl.prepare_filename(ydl.extract_info(link)))
        return salvar_transcricao(video)
    except Exception as e:
        return f"Não consegui adicionar o vídeo: {e}"


def adicionar_videos_enviados(criador: str, videos: Optional[Sequence[Video]] = None) -> str:
    """Transcreve os vídeos que o usuário anexou no chat e adiciona aos exemplos do criador.

    Args:
        criador: ex: "kallaway". Pode ser um criador novo.
    """
    if not videos:
        return "Nenhum vídeo anexado. Peça para o usuário anexar o arquivo de vídeo na mensagem."
    resultados = []
    for v in videos:
        try:
            conteudo = v.get_content_bytes()
            video = _pasta(criador) / f"{hashlib.sha1(conteudo).hexdigest()[:16]}.{v.format or 'mp4'}"
            if not video.exists():
                video.write_bytes(conteudo)
            resultados.append(salvar_transcricao(video))
        except Exception as e:
            resultados.append(f"Erro em um dos vídeos: {e}")
    return "\n".join(resultados)
