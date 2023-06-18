# expense tracker project

"""
what I want to build is a program that

take in: - the month budget
         - amount withdrawn each time
         - the reason for withdrawal
         - (might add a "user" later)

give out in a .csv file named "current month and year": - the month budget
                                                        - the amount withdrawn
                                                        - the amount left from the budget
                                                        - the reason for withdrawal
                                                        - date of the withdrawal
                                                        - time of the withdrawal

featues to be added:
- The ability to update the month budget in the middle of the month
- the ability to have a full track for the inputs and outputs has been added and removed from the project for the current month(concat everything in one pdf file)
- the ability to custom name the files.
- the ability to include reciept images and checks in the report file.

Exceptions to be added:
- filling a single bar in a two bar window. DONE
- entering a none csv filename in -c mode. DONE
- withdrawing more than the amount left in the budget.  DONE
- using c mode without a filename. DONE
- adding a budget source without a plus sign. Done
- add the ability to save the info in a database to the side of a csv file.

check the rest file for improvements

"""

# imports
from datetime import datetime
import csv
import pandas as pd
import os
import time as tm
import argparse
import re
import sys



def csv_check_existence(filename):

    # filename = f"{filename}.csv"
    if filename not in os.listdir():
        return True
    else:
        return False


def csv_first_entry(file_name, budget, sources):
    # a function to initiate a csv file and write the first line of it
    withdraw = 0
    purpose = "First entry budget source ({})".format(sources)
    dicti = Dictionary()
    dic = dicti.update(budget, withdraw, purpose)
    the_writer(file_name, dic, True)

    return dic[0]["Budget"]


def csv_make_an_entry(file_name, withdraw, purpose):
    # a function to edit the csv file and add withdrawal lines to it
    with open(file_name, "r") as file:
        data = file.readlines()
        lastRow = data[-1]
        l = lastRow.split(",")
        budget = l[2]
    dicti = Dictionary()
    dic = dicti.update(budget, withdraw, purpose)
    the_writer(file_name, dic, False)

    return dic[0]["Withdrawal_purpose"]


def the_writer(file_name, dic, type):
    # a function to write the data generate in the "create_csv_file_for_the_month" and "make_an_entry" into the csv file.
    with open(file_name, "a", newline="") as csvfile:
        headers = [
            "Budget",
            "Withdraw",
            "Amount_left",
            "Withdrawal_purpose",
            "Date",
            "Time",
        ]
        csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
        if type:
            csvwriter.writeheader()
        csvwriter.writerows(dic)
    return True


def csv_budget_update(file_name, new_sources, added_budget):
    # a function to make the necessary edits to the csv file when a budget edit is needed
    x = pd.DataFrame(pd.read_csv(file_name))
    old_sources = re.search("\(([a-zA-Z+ ]*)\)", x.at[0, "Withdrawal_purpose"])
    try:
        x.at[0, "Withdrawal_purpose"] = "First entry budget source({}+{})".format(
            old_sources[1], new_sources
        )
    except TypeError:
        sys.exit("Please, edit the csv file manually to match the correct usage.")

    x.Budget = int(x.Budget[0] )+ int(added_budget)
    x.Amount_left = int(x.Amount_left[0]) + int(added_budget)
    dicti = Dictionary()
    dic = dicti.budg_up(x.iloc[-1, 0], x.iloc[-1, 2], added_budget)
    df = pd.DataFrame(dic, index=["Time"])
    x = pd.concat([x, df], ignore_index=True)
    x.to_csv(file_name, index=False)

    return x.at[0, "Withdrawal_purpose"]

def csv_generate_report(file_name):
    rg.generate_report(file_name)

class Dictionary:
    # a class with the dictionary forms needed in the code above
    def __init__(self):
        self.di = [
            {
                "Budget": 0,
                "Withdraw": 0,
                "Amount_left": 0,
                "Withdrawal_purpose": "",
                "Date": "",
                "Time": "",
            }
        ]
        self.date = datetime.now().strftime("%x")
        self.time = datetime.now().strftime("%X")

    def update(self, budget, withdraw, purpose):
        self.di[0]["Budget"] = budget
        self.di[0]["Withdraw"] = withdraw
        try:
            left = int(budget) - int(withdraw)
        except ValueError:
            sys.exit("Invalid input.")
        if left < 0:
            raise Exception("You do not have that amount left in the budget.")
        self.di[0]["Amount_left"] = str(left)
        self.di[0]["Withdrawal_purpose"] = purpose
        self.di[0]["Date"] = self.date
        self.di[0]["Time"] = self.time

        return self.di

    def budg_up(self, budget, amount_left, added_budget):
        self.di[0]["Budget"] = budget
        self.di[0]["Withdraw"] = 0
        self.di[0]["Amount_left"] = amount_left
        self.di[0]["Withdrawal_purpose"] = f"A budget update ({added_budget}) happened on: "
        self.di[0]["Date"] = self.date
        self.di[0]["Time"] = self.time

        return self.di



