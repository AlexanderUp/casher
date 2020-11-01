# encoding:utf-8
# database model for casher


from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime


from datetime import datetime


GROUPS = {
            '1':'Products',
            '2':'Gas',
            '3':'Wildberries',
            '4':'Soft',
            '5':'Medicine',
            '6':'Service',
         }


metadata = MetaData()


expenses = Table('expenses', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('gpoup_id', Integer, nullable=False),
                  Column('article_id', Integer, nullable=False),
                  Column('price', Float, nullable=False),
                  Column('memo', String),
                  Column('created', DateTime, default=datetime.now),
                  Column('updated', DateTime, default=datetime.now, onupdate=datetime.now),
                  )

articles = Table('articles', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('name', String, nullable=False, unique=True),
                 )

groups = Table('groups', metadata,
               Column('id', Integer, primary_key=True),
               Column('group_name', String, nullable=False, unique=True),
               )


class Expense():

    def __init__(self, group_id, name_id, price, memo=None):
        self.group_id = group_id
        self.name_id = name_id
        self.price = price
        self.memo = memo

    def __repr__(self):
        return f'<Expence ({self.group_id}, {self.name_id}, {self.price})>'

    def __str__(self):
        return f'<Expence ({self.group_id}, {self.name_id}, {self.price})>'


class Article():

    def __init__(self, article_name):
        self.article_name = name

    def __repr__(self):
        return f'<Article ({self.article_name})>'

    def __str__(self):
        return f'<Article ({self.article_name})>'


class Group():

    def __init__(self, group_name):
        self.group_name = group_name

    def __repr__(self):
        return f'<Expense Group ({self.group_name})>'

    def __str__(self):
        return f'<Expense Group ({self.group_name})>'
