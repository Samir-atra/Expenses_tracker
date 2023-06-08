"""
create functions for:
    - creating the database if not exists
    - creating a table with the month date if not exists
    - make an entry to the table 
    - table updater for new budget
    - generating a pdf report
    - build a gui for the project.
    - check the queries quality and safty
"""

from flask import Flask, g
import sqlite3
from datetime import datetime
import os
import time as tm
import argparse
import re
import sys
import utils.Gui as Gui
import utils.report_generator as rg 
import csv




Database = "budgeting.db"

db = sqlite3.connect(Database)

month = datetime.now().strftime("%B_%Y")

date = datetime.now().strftime("%x")
time = datetime.now().strftime("%X")

cursor = db.cursor()



def db_check_existence(filename):

    check_exictance_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{filename}';"

    check_query = cursor.execute(check_exictance_query)

    db.commit()

    fetch = cursor.fetchall()

    if fetch == []:
        return True
    else:
        return False



def db_first_entry(filename, budget, sources):

    create_table_query = f"CREATE TABLE IF NOT EXISTS {month} (Id INTEGER PRIMARY KEY AUTOINCREMENT, Budget INTEGER, Withdraw INTEGER, Amount_left INTEGER, Withdrawal_purpose TEXT, Date TEXT, Time TEXT)"

    create_table = cursor.execute(create_table_query)

    db.commit()

    budget = int(budget)

    sources = sources

    init_entry_query = f"INSERT INTO {month} (Budget, Withdraw, Amount_left, Withdrawal_purpose, Date, Time) VALUES (?, 0, ?, ?, ?, ?);"

    init_entry_args = (budget, budget, f"First entry budget source(s): {sources}", date, time)

    init_entry = cursor.execute(init_entry_query, init_entry_args)

    db.commit()
    


def db_make_an_entry(file_name, withdraw, purpose):


    make_an_entry_query = f"INSERT INTO {month} (Budget, Withdraw, Amount_left, Withdrawal_purpose, Date, Time) VALUES (?, ?, ?, ?, ?, ?)"

    cursor.execute(f"SELECT * FROM {month}")

    fetch =  cursor.fetchall()

    budget = fetch[-1][3]
    
    withdraw = withdraw

    left = int(budget) - int(withdraw)

    withdrawal_purpose = purpose

    make_an_entry_args = (budget, withdraw, left, withdrawal_purpose, date, time)

    make_an_entry = cursor.execute(make_an_entry_query, make_an_entry_args)

    db.commit()



def db_budget_update(filename, new_sources, added_budget):
    

    added_budget = int(added_budget)

    count_query = f"SELECT COUNT(*) FROM {month};"

    cursor.execute(count_query)

    fetch =  cursor.fetchall()

    count_fetch = fetch[0][0]

    for row in range(count_fetch):

        cursor.execute(f"SELECT * FROM {month}")

        fetch =  cursor.fetchall()

        old_budget = fetch[row][1]
        old_left = fetch[row][3]
        old_purpose = str(fetch[0][4])

        new_budget = added_budget + old_budget
        new_left = added_budget + old_left
        new_purpose = old_purpose + "+" + new_sources

        if row == 0:
            update_query = f"UPDATE {month} SET Budget = ?, Amount_left = ?, Withdrawal_purpose = ? WHERE id = {row+1};"
            update_args = (new_budget, new_left, new_purpose)
        else:
            update_query = f"UPDATE {month} SET Budget = ?, Amount_left = ? WHERE id = {row+1};"
            update_args = (new_budget, new_left)

        cursor.execute(update_query, update_args)

        db.commit()

    make_an_entry_query = f"INSERT INTO {month} (Budget, Withdraw, Amount_left, Withdrawal_purpose, Date, Time) VALUES (?, ?, ?, ?, ?, ?)"

    cursor.execute(f"SELECT * FROM {month}")

    fetch =  cursor.fetchall()

    budget = fetch[-1][3]

    withdraw = 0

    left = budget

    withdrawal_purpose = f"A budget update ({added_budget}) happened on:"

    make_an_entry_args = (budget, withdraw, left, withdrawal_purpose, date, time)

    make_an_entry = cursor.execute(make_an_entry_query, make_an_entry_args)

    db.commit()



def db_generate_report(filename):

    count_query = f"SELECT * FROM {month};"

    cursor.execute(count_query)

    fetch =  cursor.fetchall()

    with open(f"{month}.csv", "a", newline="") as csvfile:
        headers = [
            "Budget",
            "Withdraw",
            "Amount_left",
            "Withdrawal_purpose",
            "Date",
            "Time",
        ]

        csv_out=csv.writer(csvfile)
        csv_out.writerow(headers)
        for row in fetch:
            csv_out.writerow(row)
 
    rg.generate_report(f"{month}.csv")


