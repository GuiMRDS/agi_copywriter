# AGENTS.md

Instruções para agentes de IA (Claude Code, Codex, Cursor etc.) que trabalham neste repositório.

## Visão geral

Agente copywriter que escreve roteiros de Reels imitando o estilo de criadores de conteúdo.
O pipeline tem duas partes:

1. **`transcripter.py`**: percorre `videos/<criador>/` e transcreve só os vídeos novos (ffmpeg + Whisper da Groq), gravando no SQLite `data/transcricoes.db` (tabela `transcricoes`: `criador`, `video`, `origem`, `texto`, `criado_em`, único por `criador`+`video`). A lógica fica em `tools/videos.py` (`salvar_transcricao`) e o acesso ao banco em `tools/transcripts.py` (`conectar`, `adicionar`, `existe`, `importar_json`).
2. **`agents.py`**: agente Agno servido pelo AgentOS (`localhost:7777`), que pesquisa na web e usa as transcrições como referência de estilo. O front-end fica em `agent-ui/`.

## Estrutura

| Caminho | Função |
|---|---|
| `agents.py` | Define o agente (modelo, ferramentas, banco) e o AgentOS |
| `prompt/copywrite.md` | Instruções (system prompt) do agente |
| `tools/transcripts.py` | Ferramentas de leitura: `listar_criadores`, `listar_transcricoes`, `ler_transcricoes` |
| `tools/videos.py` | `salvar_transcricao` e as ferramentas `adicionar_video_por_link` (yt-dlp) e `adicionar_videos_enviados` (anexos do chat) |
| `transcripter.py` | Transcreve os vídeos novos de `videos/` |
| `data/transcricoes.db` | Banco de transcrições, atualizado pelo `transcripter.py` e pelo chat. **Ignorado pelo git** (texto de terceiros) |
| `videos/` | Vídeos de origem, uma pasta por criador. **Ignorado pelo git** (direitos autorais) |
| `agent-ui/` | Front-end Next.js do Agno (projeto separado, com seu próprio `package.json`). Tem botão de anexar vídeo em `src/components/chat/ChatArea/ChatInput/ChatInput.tsx`, que envia os arquivos no campo `files` |
| `tmp/` | Storage do agente (`tmp/agno.db`: sessões, histórico, memórias). Ignorado pelo git |

## Comandos

```bash
uv sync                                  # instala dependências
uv run transcripter.py                   # gera/atualiza transcrições (requer ffmpeg no PATH)
uv run agents.py                         # sobe o AgentOS em localhost:7777
uv run tools/transcripts.py              # lista criadores
uv run tools/transcripts.py kallaway     # lista roteiros de um criador
uv run tools/transcripts.py kallaway 1 3 # lê roteiros específicos
cd agent-ui && npm install && npm run dev  # front-end em localhost:3000
```

No Windows, defina `PYTHONIOENCODING=utf-8` se o terminal der erro ao imprimir caracteres especiais.

## Variáveis de ambiente (`.env`)

- `GROQ_API_KEY`: modelo do agente e Whisper.
- `TAVILY_API_KEY`: pesquisa na web.

**Nunca** faça commit do `.env` nem imprima o valor das chaves.

## Regras e cuidados

- **Limite de tokens da Groq (plano gratuito): 8.000 TPM** no `openai/gpt-oss-120b`. Toda mudança precisa manter o contexto pequeno:
  - não aumente `max_tokens` do Tavily (hoje 1000) nem `num_history_runs` (hoje 3) sem necessidade;
  - mantenha `max_tool_calls_from_history=0`;
  - prefira `ler_transcricoes(criador, numeros=[...])` a ler todas as transcrições de uma vez.
- Ferramentas do agente são funções Python simples: a **docstring e os type hints viram o schema** que o modelo vê. Mantenha docstrings curtas, com exemplos de valores reais nos `Args`.
- Ferramentas devem devolver `str` e retornar mensagens de erro úteis (ex: listar os criadores válidos) em vez de lançar exceções.
- O caminho das transcrições é relativo ao arquivo (`Path(__file__)`), não ao diretório atual. Mantenha assim.
- O prompt do agente está em português, mas os roteiros e hooks são gerados **em inglês** (regra do `prompt/copywrite.md`).
- Para adicionar um criador: crie `videos/<nome>/`, coloque os `.mp4` e rode `uv run transcripter.py`, ou adicione pelo chat (link ou anexo).
- Vídeos anexados chegam às ferramentas pelo parâmetro `videos: Optional[Sequence[Video]]`, que o Agno injeta e não aparece no schema. O agente usa `send_media_to_model=False` (o modelo não vê os vídeos, só as ferramentas) e `store_media=False` (os vídeos não vão para o banco).
- Vídeos anexados são salvos com o hash do conteúdo como nome. Assim, enviar o mesmo vídeo de novo não duplica a transcrição.
- Nome de criador é normalizado por `normalizar()` em `tools/transcripts.py` (minúsculas, só `a-z0-9_-`). Use essa mesma função em qualquer código que monte caminhos a partir do nome, tanto para ler quanto para salvar.
- **Nunca** faça commit de `videos/`, `data/` ou `transcriptions/`: é conteúdo de outros criadores.
- Avisos conhecidos e inofensivos: `Duplicate Operation ID` (bug do Agno, silenciado no `agents.py`) e `404 Session ... not found` ao abrir um chat novo na UI.
