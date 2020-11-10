# encoding:utf-8
# database module for casher

import sqlalchemy
import os
import datetime
import argparse
import matplotlib.pyplot as plt


from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker


import casher_database_model as dbm
import config

from aux import import_csv


mapper(dbm.Expense, dbm.expenses)
mapper(dbm.Article, dbm.articles)
mapper(dbm.Group, dbm.groups)


class Casher():

    def __init__(self, path):
        self.path = os.path.join(path, 'casher_db.sqlite3')
        self.engine = create_engine('sqlite:///' + self.path)
        dbm.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _import_groups_from_csv(self, file):
        groups = [x[2] for x in import_csv(file)]
        for g in sorted(set(groups)):
            group = dbm.Group(g)
            self.session.add(group)
            try:
                self.session.commit()
            except sqlalchemy.exc.SQLAlchemyError as err:
                print('Integrity Error!', group)
                print(err)
                continue
            else:
                print(f'Added: {group}')
        print('<<<< Groups updated! >>>>')
        return None

    def _import_purchases_from_csv(self, file):
        purchases = [x for x in import_csv(file)]
        for purchase in purchases:
            date_ = purchase[0].split('.')
            date = datetime.datetime(int(date_[-1]), int(date_[-2]), int(date_[-3]))
            price = purchase[1]
            price = price.replace(',', '.')
            price = float(price)
            group = self.session.query(dbm.Group).filter(dbm.Group.group_name==purchase[2]).first()
            print(f'Group: {purchase[2]} ({group.id})')
            try:
                memo = purchase[3]
            except IndexError as err:
                memo = None
            expense = dbm.Expense(date, group.id, price, memo)
            print(expense)
            print(f'Date: {date}, price: {price}, group_id: {group.id}, group: {purchase[2]}, memo: {memo}')
            self.session.add(expense)
            try:
                self.session.commit()
            except sqlalchemy.exc.SQLAlchemyError as err:
                print('SQLAlchemyError occured!', err)
                self.session.rollback()
        print('<<<< Purchases processed! >>>>')
        return None

    def add_purchase(self):
        pass

    def _get_date(self, year, month):
        return '.'.join((str(year), str(month)))

    def get_expense_sum_by_group(self):
        groups = self.session.query(dbm.Group).all()
        keys = [(group.id, group.group_name) for group in groups]
        purchases = dict.fromkeys(keys, 0)
        for group in groups:
            result = self.session.query(dbm.Expense).filter(dbm.Expense.group_id==group.id).all()
            total = 0
            for res in result:
                total += res.price
            purchases[(group.id, group.group_name)] = total
        return purchases

    def get_expense_sum_by_month(self):
        expenses = self.session.query(dbm.Expense).all()
        monthes = set((expense.date.year, expense.date.month) for expense in expenses)
        monthes = [self._get_date(month[0], month[1]) for month in monthes]
        purchases = dict.fromkeys(monthes, 0)
        for expense in expenses:
            expense_date = self._get_date(expense.date.year, expense.date.month)
            purchases[expense_date] += expense.price
        return purchases

    def print_expense_sum_by_group(self):
        purchases = self.get_expense_sum_by_group()
        purchase_list = [purchase for purchase in purchases.items()]
        purchase_list.sort(key=lambda x: x[1], reverse=True)
        for purchase in purchase_list:
            print(f'Group: #{purchase[0][0]:>3} - {purchase[0][1]:<20} - Total sum: {purchase[1]:>10.2f}')
        return None

    def print_expense_sum_by_month(self):
        purchases = self.get_expense_sum_by_month()
        for key in purchases.keys():
            print(f'Month: {key:=<7}=> total expenses: {purchases[key]:>10.2f};')
        return None

    def plot(self, values, labels, chart_label):
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title(f'Total expense by {chart_label}')
        plt.show()
        return None

    def plot_by_group(self):
        purchases = self.get_expense_sum_by_group()
        groups = [value for value in purchases.keys()]
        sums = [purchases[group] for group in groups]
        self.plot(sums, groups, 'group')
        return None

    def plot_by_month(self):
        purchases = self.get_expense_sum_by_month()
        monthes = [value for value in purchases.keys()]
        sums = [purchases[month] for month in monthes]
        self.plot(sums, monthes, 'month')
        return None

    def plot_by_monthes_and_groups(self):
        purchases = self.session.query(dbm.Expense).all()
        dates = set((purchase.date.year, purchase.date.month) for purchase in purchases)
        keys = [self._get_date(*date) for date in dates]
        print(keys)

        groups_query = self.session.query(dbm.Group).all()
        groups = {group.id:group.group_name for group in groups_query}

        for date in dates:
            monthly_purchases = [purchase for purchase in purchases if purchase.date.year==date[0] and purchase.date.month==date[1]]
            monthly_result = dict.fromkeys(groups.values(), 0)
            for purchase in monthly_purchases:
                monthly_result[groups[purchase.group_id]] += purchase.price
            print(f'***** Date: {self._get_date(*date)} *****')
            for res in monthly_result.items():
                print(f'Group: {res[0]:<20} - Total: {res[1]:>10.2f}')

            labels = [key for key in monthly_result.keys()]
            labels.sort()
            sums = [monthly_result[label] for label in labels]
            self.plot(sums, labels, date)
        return None

    def close_db(self):
        self.session.close()
        return None

    def __repr__(self):
        return f'<Database ({self.path})>'


if __name__ == '__main__':
    print('*' * 125)
    config = config.Config()
    path = config.CASHER_PATH

    parser = argparse.ArgumentParser(description='Expense calculator.')
    parser.add_argument('-m', '--monthes', action='store_true', help='Calculate sum of expenses grouped by monthes.')
    parser.add_argument('-g', '--groups', action='store_true', help='Calculate sum of expenses grouped by groups.')
    parser.add_argument('-u', '--update', action='store_true', help='Update database with new expense entries.')
    parser.add_argument('-p', '--plot', action='store_true', help='Plot expenses grouped by monthes and groups.')
    parser.add_argument('--plot-verbose', action='store_true', help='Plot monthly expenses grouped by groups.')
    args = parser.parse_args()

    casher = Casher(path)
    print(casher)

    if args.monthes:
        print('Calculating total expenses grouped by monthes...')
        casher.print_expense_sum_by_month()
    elif args.groups:
        print('Calculating total expenses grouped by categories...')
        casher.print_expense_sum_by_group()
    elif args.plot:
        casher.plot_by_group()
        casher.plot_by_month()
    elif args.plot_verbose:
        casher.plot_by_monthes_and_groups()
    elif args.update:
        print('Reading data from csv-file...')
        file = config.CSV_FILE
        casher._import_groups_from_csv(file)
        casher._import_purchases_from_csv(file)
    else:
        print('Unknown option!')

    print('***** Done! *****')
