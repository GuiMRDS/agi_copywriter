import json, re
from pathlib import Path

PASTA = Path(__file__).parent.parent / "transcriptions"


def normalizar(criador: str) -> str:
    """Nome de criador seguro para usar em caminhos: "Jeff Nippard" -> "jeffnippard"."""
    return re.sub(r"[^a-z0-9_-]", "", criador.lower())


def _carregar(criador: str) -> list[str] | str:
    arquivo = PASTA / f"{normalizar(criador)}.json"
    if not normalizar(criador) or not arquivo.exists():
        return f"Criador '{criador}' não encontrado. Disponíveis: {', '.join(f.stem for f in PASTA.glob('*.json'))}"
    return [t.strip() for t in json.loads(arquivo.read_text(encoding="utf-8")).values()]


def listar_criadores() -> str:
    """Lista os criadores de conteúdo disponíveis e quantos roteiros cada um tem."""
    return "\n".join(f"- {f.stem} ({len(_carregar(f.stem))} transcripts)" for f in sorted(PASTA.glob("*.json")))


def listar_transcricoes(criador: str) -> str:
    """Lista os roteiros de um criador com número e a primeira frase (o hook). Use para escolher quais ler.

    Args:
        criador: ex: "kallaway". Use os valores de listar_criadores.
    """
    textos = _carregar(criador)
    if isinstance(textos, str):
        return textos
    return "\n".join(f"{i}. {t.split('. ')[0][:150]}" for i, t in enumerate(textos, 1))


def ler_transcricoes(criador: str, numeros: list[int] | None = None) -> str:
    """Retorna as transcrições de um criador. Sem `numeros`, retorna todas.

    Args:
        criador: ex: "kallaway". Use os valores de listar_criadores.
        numeros: números dos roteiros a ler, conforme listar_transcricoes (ex: [1, 3]).
    """
    textos = _carregar(criador)
    if isinstance(textos, str):
        return textos
    escolhidos = numeros or range(1, len(textos) + 1)
    return "\n\n".join(f"Transcript {i}\n{textos[i - 1]}" for i in escolhidos if 1 <= i <= len(textos))


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print(listar_criadores())
    elif len(sys.argv) == 2:
        print(listar_transcricoes(sys.argv[1]))
    else:
        print(ler_transcricoes(sys.argv[1], [int(n) for n in sys.argv[2:]]))
