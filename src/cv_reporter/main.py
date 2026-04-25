import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from cv_reporter.config import DATABASE_URL, REPORT_HOUR, TIMEZONE
from cv_reporter.db.queries import collect_all_stats
from cv_reporter.report.generator import generate_report
from cv_reporter.telegram.sender import send_message

_NO_VISITS_MESSAGES = [
    "📭 Nadie pasó por el CV entre {since} y {until}. Silencio total, como un lunes a las 7am.",
    "🦗 Entre {since} y {until} no vino nadie. Ni un bot curioso. Ni un error 404. Nada.",
    "😴 {since} → {until}: el CV estuvo más solo que perro en veterinaria. Cero visitas.",
    "🏜️ Período {since} → {until} sin visitas. El desierto digital saluda.",
    "👻 Nadie entre {since} y {until}. O el CV está muy bien escondido, o todos están de vacaciones.",
]


def build_window() -> tuple[datetime, datetime]:
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    until = now.replace(hour=REPORT_HOUR, minute=0, second=0, microsecond=0)
    if until > now:
        until -= timedelta(days=1)
    since = until - timedelta(hours=24)
    return since, until


def main():
    since, until = build_window()

    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        stats = collect_all_stats(session, since, until)

    total = stats["summary"]["total_visits"]
    if total == 0:
        since_str = since.strftime("%d/%m %H:%M")
        until_str = until.strftime("%d/%m %H:%M")
        msg = random.choice(_NO_VISITS_MESSAGES).format(since=since_str, until=until_str)
        send_message(msg)
        print(f"Sin visitas. Período: {since} → {until}")
        return

    report = generate_report(stats)
    send_message(report)
    print(f"Reporte enviado. Período: {since} → {until}")


if __name__ == "__main__":
    main()
