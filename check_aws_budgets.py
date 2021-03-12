#!/usr/bin/env python3
"""
check_aws_budgets.py

An Icinga/Nagios plug-in to check budgets in an account

Author: Frank Wittig <frank@e5k.de>
Source: https://github.com/elias5000/check_aws_budgets
"""

import sys

import boto3
from botocore.exceptions import BotoCoreError

STATE_OK = 0
STATE_WARN = 1
STATE_CRIT = 2
STATE_UNKNOWN = 3


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


def get_overspend():
    """
    Return budgets with overspend flag as dict
    :return:
    """
    res = {}
    for budget in fetch_budgets():
        name = budget['BudgetName']
        limit = float(budget['BudgetLimit']['Amount'])
        forecast = float(budget['CalculatedSpend']['ForecastedSpend']['Amount'])

        res["{}(fcst:{:.2f};limit:{:.2f})".format(name, forecast, limit)] = forecast > limit
    return res


if __name__ == '__main__':
    overspend = get_overspend()
    if [o for o in overspend.values() if o]:
        print("Budget forecasts exceed limit: {}".format(', '.join(overspend.keys())))
        sys.exit(STATE_CRIT)

    print("All budgets within limit: {}".format(', '.join(overspend.keys())))
    sys.exit(STATE_OK)
