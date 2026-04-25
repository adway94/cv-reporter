import json
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from cv_reporter.config import NVIDIA_API_KEY, NVIDIA_MODEL

_SYSTEM_PROMPT = """Sos un analista de datos que genera informes ejecutivos en español rioplatense.
Recibís estadísticas de visitas de un CV digital personal y generás un resumen claro, conciso y útil.

Reglas:
- Escribí en español rioplatense (vos, che, etc.)
- Máximo 300 palabras
- Destacá lo más llamativo (picos de tráfico, páginas más visitadas, dispositivos)
- Si hay pocos datos, decilo sin dramatizar
- No uses listas largas, preferí párrafos cortos
- Usá emojis con moderación para hacer el mensaje más legible en Telegram
- Terminá con una observación breve o curiosidad de los datos"""

_HUMAN_PROMPT = """Estas son las estadísticas del período {period}:

{stats_json}

Generá el informe diario."""


def generate_report(stats: dict) -> str:
    llm = ChatNVIDIA(
        model=NVIDIA_MODEL,
        api_key=NVIDIA_API_KEY,
        temperature=0.6,
        top_p=0.9,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ])

    chain = prompt | llm | StrOutputParser()

    period = stats.get("period", {})
    period_str = f"{period.get('since', '?')} → {period.get('until', '?')}"

    return chain.invoke({
        "period": period_str,
        "stats_json": json.dumps(stats, ensure_ascii=False, indent=2),
    })
