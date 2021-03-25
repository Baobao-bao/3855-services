from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class StockOpenPrice(Base):
    """stock open price"""

    __tablename__ = "stock_open_price"

    id = Column(Integer, primary_key = True)
    stock_code = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Integer,nullable=True)

    def __init__(self, stock_code, open_price,date):
        """ Initializes a stock open price reading """
        self.stock_code = stock_code
        self.open_price = open_price
        self.date = date

    def to_dict(self):
        """ Dictionary Representation of a stock open price reading """
        dict = {}
        dict['id'] = self.id
        dict['stock_code'] = self.stock_code
        dict['open_price'] = self.open_price
        dict['date'] = self.date

        return dict
