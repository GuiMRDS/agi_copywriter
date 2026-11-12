import json, re, sqlite3
from pathlib import Path

RAIZ = Path(__file__).parent.parent
BANCO = RAIZ / "data" / "transcricoes.db"


def normalizar(criador: str) -> str:
    """Nome de criador seguro para usar em caminhos: "Jeff Nippard" -> "jeffnippard"."""
    return re.sub(r"[^a-z0-9_-]", "", criador.lower())


def conectar() -> sqlite3.Connection:
    BANCO.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(BANCO)
    con.execute("""CREATE TABLE IF NOT EXISTS transcricoes (
        id INTEGER PRIMARY KEY,
        criador TEXT NOT NULL,
        video TEXT NOT NULL,
        origem TEXT,
        texto TEXT NOT NULL,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (criador, video))""")
    return con


def existe(criador: str, video: str) -> bool:
    with conectar() as con:
        return con.execute("SELECT 1 FROM transcricoes WHERE criador = ? AND video = ?", (normalizar(criador), video)).fetchone() is not None


def adicionar(criador: str, video: str, texto: str, origem: str = "pasta") -> int:
    """Grava uma transcrição no banco e retorna quantas o criador tem."""
    with conectar() as con:
        con.execute("INSERT OR IGNORE INTO transcricoes (criador, video, origem, texto) VALUES (?, ?, ?, ?)", (normalizar(criador), video, origem, texto.strip()))
        return con.execute("SELECT COUNT(*) FROM transcricoes WHERE criador = ?", (normalizar(criador),)).fetchone()[0]


def importar_json(pasta: Path = RAIZ / "transcriptions") -> int:
    """Importa os antigos transcriptions/<criador>.json para o banco. Retorna quantas transcrições eram novas."""
    novas = 0
    for arquivo in pasta.glob("*.json"):
        for video, texto in json.loads(arquivo.read_text(encoding="utf-8")).items():
            if not existe(arquivo.stem, video):
                adicionar(arquivo.stem, video, texto)
                novas += 1
    return novas


def _carregar(criador: str) -> list[str] | str:
    with conectar() as con:
        textos = [t for (t,) in con.execute("SELECT texto FROM transcricoes WHERE criador = ? ORDER BY id", (normalizar(criador),))]
        if not textos:
            disponiveis = ", ".join(c for (c,) in con.execute("SELECT DISTINCT criador FROM transcricoes ORDER BY criador"))
            return f"Criador '{criador}' não encontrado. Disponíveis: {disponiveis or 'nenhum'}"
    return textos


def listar_criadores() -> str:
    """Lista os criadores de conteúdo disponíveis e quantos roteiros cada um tem."""
    with conectar() as con:
        linhas = con.execute("SELECT criador, COUNT(*) FROM transcricoes GROUP BY criador ORDER BY criador").fetchall()
    return "\n".join(f"- {c} ({n} transcripts)" for c, n in linhas) or "Nenhum criador cadastrado ainda."


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
