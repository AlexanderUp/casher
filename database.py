# encoding:utf-8
# database module for casher

import sqlalchemy
import os


from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker


import casher_database_model as dbm
import config


mapper(dbm.Expense, dbm.expenses)
mapper(dbm.Article, dbm.articles)
mapper(dbm.Group, dbm.groups)


class Database():

    def __init__(self, path):
        self.path = os.path.join(path, 'casher_db.sqlite3')
        self.engine = create_engine('sqlite:///' + self.path)
        dbm.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __repr__(self):
        return f'<Database ({self.path})>'


if __name__ == '__main__':
    print('*' * 125)
    config = config.Config()
    path = config.CASHER_PATH
    print(f'Path: {path}')
    db = Database(path)
    print(db)
    print('***** Done! *****')
