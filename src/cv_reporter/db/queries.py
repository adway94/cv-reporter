from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import Visit
from cv_reporter.config import TIMEZONE


def _window_filter(query, since: datetime, until: datetime):
    return query.filter(Visit.timestamp >= since, Visit.timestamp < until)


def get_daily_stats(session: Session, since: datetime, until: datetime) -> dict:
    base = _window_filter(
        session.query(Visit).filter(Visit.is_bot == False), since, until
    )
    total = base.count()
    unique = base.with_entities(func.count(func.distinct(Visit.daily_visitor_hash))).scalar()
    bots = _window_filter(
        session.query(Visit).filter(Visit.is_bot == True), since, until
    ).count()
    return {"total_visits": total, "unique_visitors": unique, "bots_filtered": bots}


def get_top_paths(session: Session, since: datetime, until: datetime, limit: int = 5) -> list[dict]:
    rows = (
        _window_filter(
            session.query(Visit.path, func.count(Visit.id).label("count"))
            .filter(Visit.is_bot == False),
            since, until,
        )
        .group_by(Visit.path)
        .order_by(func.count(Visit.id).desc())
        .limit(limit)
        .all()
    )
    return [{"path": r.path, "count": r.count} for r in rows]


def get_browser_breakdown(session: Session, since: datetime, until: datetime) -> list[dict]:
    rows = (
        _window_filter(
            session.query(Visit.browser, func.count(Visit.id).label("count"))
            .filter(Visit.is_bot == False),
            since, until,
        )
        .group_by(Visit.browser)
        .order_by(func.count(Visit.id).desc())
        .all()
    )
    return [{"browser": r.browser or "Desconocido", "count": r.count} for r in rows]


def get_os_breakdown(session: Session, since: datetime, until: datetime) -> list[dict]:
    rows = (
        _window_filter(
            session.query(Visit.os, func.count(Visit.id).label("count"))
            .filter(Visit.is_bot == False),
            since, until,
        )
        .group_by(Visit.os)
        .order_by(func.count(Visit.id).desc())
        .all()
    )
    return [{"os": r.os or "Desconocido", "count": r.count} for r in rows]


def get_mobile_ratio(session: Session, since: datetime, until: datetime) -> dict:
    base = _window_filter(
        session.query(Visit).filter(Visit.is_bot == False), since, until
    )
    total = base.count()
    mobile = base.filter(Visit.is_mobile == True).count()
    return {"mobile": mobile, "desktop": total - mobile, "total": total}


def get_hourly_distribution(session: Session, since: datetime, until: datetime) -> list[dict]:
    local_ts = func.timezone(TIMEZONE, Visit.timestamp)
    rows = (
        _window_filter(
            session.query(
                func.extract("hour", local_ts).label("hour"),
                func.count(Visit.id).label("count"),
            ).filter(Visit.is_bot == False),
            since, until,
        )
        .group_by(func.extract("hour", local_ts))
        .order_by(func.extract("hour", local_ts))
        .all()
    )
    return [{"hour": int(r.hour), "count": r.count} for r in rows]


def get_referrer_breakdown(session: Session, since: datetime, until: datetime) -> list[dict]:
    rows = (
        _window_filter(
            session.query(Visit.referrer, func.count(Visit.id).label("count"))
            .filter(Visit.is_bot == False, Visit.referrer.isnot(None)),
            since, until,
        )
        .group_by(Visit.referrer)
        .order_by(func.count(Visit.id).desc())
        .limit(5)
        .all()
    )
    return [{"referrer": r.referrer, "count": r.count} for r in rows]


_SUSPICIOUS_PATTERNS = [
    "%wp-%", "%/wp-%", "%.php%", "%/.env%", "%/.git%",
    "%phpmyadmin%", "%xmlrpc%", "%/admin%", "%/shell%",
    "%/cgi-bin%", "%/setup%", "%/install%", "%/config%",
]


def get_suspicious_paths(session: Session, since: datetime, until: datetime) -> list[dict]:
    from sqlalchemy import or_
    rows = (
        _window_filter(
            session.query(Visit.path, func.count(Visit.id).label("count"))
            .filter(
                Visit.is_bot == False,
                or_(*[Visit.path.ilike(p) for p in _SUSPICIOUS_PATTERNS]),
            ),
            since, until,
        )
        .group_by(Visit.path)
        .order_by(func.count(Visit.id).desc())
        .limit(10)
        .all()
    )
    return [{"path": r.path, "count": r.count} for r in rows]


def collect_all_stats(session: Session, since: datetime, until: datetime) -> dict:
    return {
        "period": {"since": since.isoformat(), "until": until.isoformat()},
        "summary": get_daily_stats(session, since, until),
        "top_paths": get_top_paths(session, since, until),
        "suspicious_paths": get_suspicious_paths(session, since, until),
        "browsers": get_browser_breakdown(session, since, until),
        "os": get_os_breakdown(session, since, until),
        "devices": get_mobile_ratio(session, since, until),
        "hourly": get_hourly_distribution(session, since, until),
        "referrers": get_referrer_breakdown(session, since, until),
    }
