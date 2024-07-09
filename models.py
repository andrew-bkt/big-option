from sqlalchemy import Column, Integer, Float, DateTime, String, UniqueConstraint
from pydantic import BaseModel
from datetime import datetime
from database import Base

class OptionData(Base):
    __tablename__ = 'option_data'

    symbol = Column(String, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    volume = Column(Integer)
    vwap = Column(Float)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    transactions = Column(Integer)

    __table_args__ = (UniqueConstraint('symbol', 'timestamp', name='uix_1'),)

class OptionDataRequest(BaseModel):
    symbol: str
    multiplier: int
    timespan: str
    from_date: str
    to_date: str

class OptionDataResponse(BaseModel):
    symbol: str
    timestamp: datetime
    volume: int
    vwap: float
    open: float
    close: float
    high: float
    low: float
    transactions: int