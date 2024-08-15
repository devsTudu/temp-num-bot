import os
import datetime

## Using sqlalchemy for Database

from sqlalchemy import create_engine, Column, Integer, Float,ForeignKey, Date, Text, TIMESTAMP
from sqlalchemy.orm import sessionmaker,declarative_base
# from telegram.bot import logger

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_info'
    userid = Column(Integer, primary_key=True)
    balance = Column(Float, default=0.0)
    datejoined = Column(Date, default=datetime.date.today())

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('user_info.userid'))
    transaction_detail = Column(Text)
    transaction_date = Column(TIMESTAMP, default=datetime.datetime.now())
    amount_credited = Column(Float)

class Service(Base):
    __tablename__ = 'services'
    service_id = Column(Integer, primary_key=True)
    service_name = Column(Text, unique=True)
    price = Column(Float)
    service_code = Column(Text, unique=True)

class UserDatabase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_user(self, userid):
        user = User(userid=userid)
        self.session.add(user)
        self.session.commit()

    def get_user_transactions(self, user_id):
        return self.session.query(Transaction).filter_by(userid=user_id).all()

    def check_user_exists(self, user_id):
        return self.session.query(User).filter_by(userid=user_id).first() is not None

    def get_user_balance(self, user_id):
        user = self.session.query(User).filter_by(userid=user_id).first()
        if not user:
            self.add_user(user_id)
            return 0.0
        return user.balance
    def recharge_balance(self, user_id, amount):
      user = self.session.query(User).filter_by(userid=user_id).first()
      if not user:
        logger.log(3,f"New user {user_id} found to recharge, registering as new user")
        user = self.add_user(userid)
      user.balance += amount 
      transaction = Transaction(userid=user_id, transaction_detail="Main Recharge", amount_credited=amount)
      self.session.add(transaction)
      self.session.commit()
    
    def record_order(self, user_id, prod_detail, amount):
      user = self.session.query(User).filter_by(userid=user_id).first()
      if not user:
          raise ValueError(f"User with ID {user_id} not found")
      if user.balance < amount:
          raise ValueError("Insufficient balance")
      user.balance -= amount
      transaction = Transaction(userid=user_id, transaction_detail=prod_detail, amount_credited=-amount)
      self.session.add(transaction)
      self.session.commit()

    def close(self):
        self.session.close()

user_db = UserDatabase("sqlite:///user.db")