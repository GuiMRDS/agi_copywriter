# AGI Copywriter

Agente de IA que escreve roteiros de **Reels** imitando o estilo de criadores de conteúdo.
Ele pesquisa o assunto na web, estuda as transcrições dos vídeos do criador escolhido e propõe hooks e roteiros com o mesmo tom, ritmo e vocabulário.

## Como funciona

```
videos/<criador>/*.mp4 ──► transcripter.py ──► data/transcricoes.db (SQLite)
                          (ffmpeg + Whisper)              │
                                                          ▼
                       usuário ◄──► agent-ui ◄──► agents.py (Agno + Groq)
                                                   ├─ Tavily (pesquisa web)
                                                   └─ tools/transcripts.py
```

O fluxo do agente (definido em `prompt/copywrite.md`):

1. **Pesquisa**: busca fatos e dados curiosos sobre o tema e apresenta um relatório com fontes.
2. **Criador**: lista os criadores disponíveis e pergunta qual estilo modelar.
3. **Hooks**: lê os roteiros do criador e sugere pelo menos 10 hooks.
4. **Roteiro**: escreve o Reels (150 a 250 palavras, em inglês) com o hook escolhido.

## Requisitos

- Python 3.13+ e [uv](https://docs.astral.sh/uv/)
- [ffmpeg](https://ffmpeg.org/) no PATH (só para gerar transcrições)
- Node.js (para o front-end)
- Chaves de API: [Groq](https://console.groq.com/keys) e [Tavily](https://app.tavily.com)

## Instalação

```bash
uv sync
```

Crie um arquivo `.env` na raiz:

```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
```

## Uso

### 1. Gerar transcrições

> As pastas `videos/` e `data/` **não são versionadas**: o conteúdo pertence aos criadores e fica só na sua máquina. Use vídeos que você tem direito de usar.

Coloque os vídeos em `videos/<nome-do-criador>/` e rode:

```bash
uv run transcripter.py
```

Ele transcreve só os vídeos novos (os que ainda não estão no banco). Na primeira vez, também importa os antigos `transcriptions/*.json`, se existirem.

As transcrições ficam no banco SQLite `data/transcricoes.db`, tabela `transcricoes` (`criador`, `video`, `origem`, `texto`, `criado_em`). A coluna `origem` indica de onde veio o vídeo: `pasta`, `upload` ou o link.

Também dá para adicionar vídeos **pelo chat**, sem mexer em pastas:

- **Link**: cole o link do Reels, TikTok ou YouTube Shorts e diga o criador ("adicione este vídeo ao kallaway: https://...").
- **Arquivo**: anexe o vídeo pelo botão 📎 do `agent-ui` e diga o criador.

O vídeo é salvo em `videos/<criador>/`, transcrito e adicionado aos exemplos. Se o criador não existir, ele é criado.

### 2. Subir o agente

```bash
uv run agents.py
```

O AgentOS sobe em `http://localhost:7777`. Para a interface de chat:

```bash
cd agent-ui
npm install
npm run dev
```

Acesse `http://localhost:3000` e conecte ao endpoint `localhost:7777`.

### 3. Consultar transcrições pelo terminal

```bash
uv run tools/transcripts.py              # lista os criadores
uv run tools/transcripts.py kallaway     # lista os roteiros do criador (número + hook)
uv run tools/transcripts.py kallaway 1 3 # lê os roteiros 1 e 3
```

## Ferramentas do agente

| Ferramenta | O que faz |
|---|---|
| `listar_criadores()` | Lista os criadores disponíveis e quantos roteiros cada um tem |
| `listar_transcricoes(criador)` | Lista os roteiros de um criador com número e hook |
| `ler_transcricoes(criador, numeros)` | Retorna as transcrições escolhidas (ou todas) em `Transcript N` |
| `adicionar_video_por_link(criador, link)` | Baixa o vídeo (yt-dlp), transcreve e adiciona ao criador |
| `adicionar_videos_enviados(criador)` | Transcreve os vídeos anexados no chat e adiciona ao criador |
| Tavily | Pesquisa na web |

## Estrutura

```
agents.py             # agente + AgentOS
prompt/copywrite.md   # instruções do agente
tools/transcripts.py  # ferramentas de leitura das transcrições
tools/videos.py       # transcrição de vídeos e ferramentas para adicionar vídeos
transcripter.py       # transcreve os vídeos novos de videos/
data/                 # banco de transcrições (ignorado pelo git)
videos/               # vídeos de origem
agent-ui/             # front-end (Next.js)
tmp/                  # banco do agente (ignorado pelo git)
```

## Créditos

A interface em `agent-ui/` é baseada no [Agent UI](https://github.com/agno-agi/agent-ui) da [Agno](https://agno.com) (licença MIT, ver `agent-ui/LICENSE`), com um botão para anexar vídeos no chat.

## Limitações

Links do Instagram às vezes exigem login para baixar. TikTok e YouTube Shorts costumam funcionar direto.

O plano gratuito da Groq limita o `openai/gpt-oss-120b` a **8.000 tokens por minuto**. Por isso o agente usa buscas curtas no Tavily, não reenvia resultados de ferramentas no histórico e pode ler só os roteiros escolhidos. Para uso mais intenso, use o Dev Tier da Groq ou troque o modelo em `agents.py`.
