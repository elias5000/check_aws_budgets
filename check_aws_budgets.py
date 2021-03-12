#!/usr/bin/env python3
"""
check_aws_budgets.py

An Icinga/Nagios plug-in to check budgets in an account

Author: Frank Wittig <frank@e5k.de>
Source: https://github.com/elias5000/check_aws_budgets
"""

import sys
from argparse import ArgumentParser

import boto3
from botocore.exceptions import BotoCoreError, ClientError

STATE_OK = 0
STATE_WARN = 1
STATE_CRIT = 2
STATE_UNKNOWN = 3


def fetch_budget(name):
    """
    Fetch single budget from account
    :param name: budget name
    :return:
    """
    try:
        caller = boto3.client('sts').get_caller_identity()
        client = boto3.client('budgets')
        return client.describe_budget(AccountId=caller['Account'], BudgetName=name)['Budget']
    except (BotoCoreError, ClientError) as err:
        print("UNKNOWN - {}".format(err))
        sys.exit(STATE_UNKNOWN)


def fetch_budgets():
    """
    Fetch all budgets from account
    :return:
    """
    try:
        caller = boto3.client('sts').get_caller_identity()
        client = boto3.client('budgets')
        paginator = client.get_paginator('describe_budgets')
        budgets = []
        for page in paginator.paginate(AccountId=caller['Account']):
            for budget in page['Budgets']:
                budgets.append(budget)
        return budgets

    except BotoCoreError as err:
        print("UNKNOWN - {}".format(err))
        sys.exit(STATE_UNKNOWN)


def get_overspend(budgets):
    """
    Return budgets with overspend flag as dict
    :param budgets: list of budgets
    :return:
    """
    res = {
        True: [],
        False: []
    }
    for budget in budgets:
        name = budget['BudgetName']
        limit = float(budget['BudgetLimit']['Amount'])
        forecast = float(budget['CalculatedSpend']['ForecastedSpend']['Amount'])

        res[forecast > limit].append("{}(fcst:{:.2f};limit:{:.2f})".format(name, forecast, limit))
    return res


def main():
    """ CLI user interface """
    parser = ArgumentParser()
    parser.add_argument('--budget', help='budget name')

    args = parser.parse_args()

    if args.budget:
        budgets = [fetch_budget(args.budget)]
    else:
        budgets = fetch_budgets()

    overspend = get_overspend(budgets)
    if overspend[True]:
        print("Budget forecast exceeds limit: {}".format(', '.join(overspend[True])))
        sys.exit(STATE_CRIT)

    print("Budgets forecast within limit: {}".format(', '.join(overspend[False])))
    sys.exit(STATE_OK)


if __name__ == '__main__':
    main()
