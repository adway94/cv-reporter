from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True))
    ip_raw = Column(String(45))
    ip_hash = Column(String(64))
    country_code = Column(String(2))
    city = Column(String(100))
    user_agent = Column(Text)
    browser = Column(String(100))
    browser_version = Column(String(50))
    os = Column(String(100))
    is_mobile = Column(Boolean)
    is_bot = Column(Boolean)
    path = Column(String(500))
    referrer = Column(Text)
    daily_visitor_hash = Column(String(64))
