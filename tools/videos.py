import hashlib, subprocess
from pathlib import Path
from typing import Optional, Sequence
from dotenv import load_dotenv
from groq import Groq
from agno.media import Video
from tools.transcripts import adicionar, existe, normalizar

load_dotenv(Path(__file__).parent.parent / ".env")
VIDEOS = Path(__file__).parent.parent / "videos"


def _pasta(criador: str) -> Path:
    nome = normalizar(criador)
    if not nome:
        raise ValueError(f"Nome de criador inválido: '{criador}'")
    pasta = VIDEOS / nome
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def salvar_transcricao(video: Path, origem: str = "pasta") -> str:
    """Transcreve um vídeo de videos/<criador>/ e grava no banco (se ainda não estiver lá)."""
    criador = video.parent.name
    if existe(criador, video.name):
        return f"{video.name} já estava transcrito em {criador}."
    audio = video.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vn", "-ac", "1", "-b:a", "64k", audio], check=True)
    try:
        texto = Groq().audio.transcriptions.create(file=(audio.name, audio.read_bytes()), model="whisper-large-v3").text
    finally:
        audio.unlink(missing_ok=True)
    total = adicionar(criador, video.name, texto, origem)
    return f"Adicionado a {criador} como Transcript {total}: {texto.strip()[:200]}..."


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
        return salvar_transcricao(video, origem=link)
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
            resultados.append(salvar_transcricao(video, origem="upload"))
        except Exception as e:
            resultados.append(f"Erro em um dos vídeos: {e}")
    return "\n".join(resultados)
