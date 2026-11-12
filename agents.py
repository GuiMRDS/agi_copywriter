import warnings
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.groq import Groq
from agno.tools.tavily import TavilyTools
from agno.os import AgentOS
from tools.transcripts import listar_criadores, listar_transcricoes, ler_transcricoes
from tools.videos import adicionar_video_por_link, adicionar_videos_enviados

load_dotenv()
warnings.filterwarnings("ignore", message="Duplicate Operation ID")  # bug interno do agno, inofensivo
db = SqliteDb(db_file="tmp/agno.db")


agent = Agent(
    name="Copywriter",
    model=Groq(id="openai/gpt-oss-120b"),
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    max_tool_calls_from_history=0,  # não reenvia resultados de ferramentas antigas (limite de 8k TPM da Groq)
    tools=[TavilyTools(max_tokens=1000, search_depth="basic"), listar_criadores, listar_transcricoes, ler_transcricoes,
           adicionar_video_por_link, adicionar_videos_enviados],
    send_media_to_model=False,  # vídeos anexados vão só para as ferramentas, não para o modelo
    store_media=False,  # não guarda os vídeos no banco (eles já ficam em videos/)
    instructions=Path("prompt/copywrite.md").read_text(encoding="utf-8"),
    markdown=True,
)

agent_os = AgentOS(agents=[agent], db=db)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="agents:app", reload=True)
