# encoding:utf-8
# auxiliary functions for casher


import csv
import os


def import_csv(file):
    with open(file, 'r') as f:
        csv_reader = csv.reader(f, delimiter=';')
        for row in csv_reader:
            yield row
    return None


if __name__ == '__main__':
    print('*' * 125)
    file = os.path.expanduser('~/Desktop/Python - my projects/casher/Expenses.csv')
    print(f'File: {file}')
    res = list(import_csv(file))
    for r in res:
        print(r)
    print('Done!')
