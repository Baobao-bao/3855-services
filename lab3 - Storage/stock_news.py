from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class StockNews(Base):
    """stock news"""

    __tablename__ = "stock_news"

    id = Column(Integer, primary_key = True)
    stock_code = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    news = Column(String(1000),nullable=False)
    source = Column(String(20),nullable=False)

    def __init__(self, stock_code, news, source, date):
        """ Initializes a stock open price reading """
        self.stock_code = stock_code
        self.news = news
        self.source = source
        self.date = date

    def to_dict(self):
        """ Dictionary Representation of a stock open price reading """
        dict = {}
        dict['id'] = self.id
        dict['stock_code'] = self.stock_code
        dict['news'] = self.news
        dict['source'] = self.source
        dict['date'] = self.date

        return dict