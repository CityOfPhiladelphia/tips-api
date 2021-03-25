'''
This file contains the code that makes the API call to the TIPS web service.
Note that this was file has been structured to also work as an AWS Lambda
or Serverless function, if those become deployment options in the future.
(They are not currently possible due to connectivity and security issues.)
'''

import datetime
import json
import os
import re
import requests
import xmltodict

def make_error_response(account_num, status, message):
    body = {
        'query': {
            'accountNum': account_num,
        },
        'message': message,
    }

    return {
        'body': json.dumps(body),
        'statusCode': status,
    }

# util to camel case an upper kebab-case string (e.g. 'PROPERTY-INFO')
# thanks to https://stackoverflow.com/a/19053800/676001
def to_camel_case(upper_kebab_str):
    components = upper_kebab_str.lower().split('-')
    return components[0] + ''.join(x.title() for x in components[1:])

# takes a dict with upper-kebab keys and camel-cases them
def camel_case_dict_keys(d):
    return {to_camel_case(k): v for (k, v) in d.items()}

# helper to guess whether the last two digits of a year belong to the 90s or
# 2000s
def infer_full_year(suffix):
    # check for good input
    if suffix is None or len(suffix) < 1:
        return None

    # no way to do this with 100% certainty. just need to replace this app
    # before 2050 :)
    full_year = None

    if int(suffix) < 50:
        full_year = '20{}'.format(suffix)
    else:
        full_year = '19{}'.format(suffix)

    return int(full_year)

# takes a MM/DD/YYYY date and converts it to a python datetime object
def datetime_from_string(date_str):
    return datetime.datetime.strptime(date_str, '%m/%d/%Y')
    
# this takes a tips response dictionary and cleans up the formatting
def format_data(raw_data):
    data = raw_data['Output']

    from pprint import pprint

    # format property info
    property_info = camel_case_dict_keys(data['PROPERTY-INFO'])
    property_info['address'] = property_info.pop('propertyAddress')

    # handle year objects (these represent tax balances per year)
    years = []
    
    # The "to" number in the range must be increased by 1 each year. 
    # TODO: refactor to go off of response keys instead of a constant max range. 
    for i in range(1, 41):
        # ensure index is always two digits
        i_padded = '0{}'.format(i) if i < 10 else i

        year_key = 'TAX-YEAR{}-BR'.format(i)
        year_data = data[year_key]

        # form full year
        year_suffix_key = 'S-TAX-YEAR-YEAR-{}'.format(i_padded)
        year_suffix = year_data[year_suffix_key]
        year = infer_full_year(year_suffix)

        # don't push any years beyond the current year
        current_year = datetime.datetime.now().year

        # if year is None or current_year < year:
        if year is None:
            break

        # Software AG api appears to start returning data for next year on Dec. 1
        # TIPS RTTAN452 uses year 2034 as MISC placeholder
        if current_year + 1 < year and year != 2034:
            break

        year_data_formatted = {
            'year': year,
            'principal': float(year_data['S-PRINCIPAL-BAL-YEAR-{}'.format(i_padded)]),
            'interest': float(year_data['S-INTEREST-BAL-YEAR-{}'.format(i_padded)]),
            'penalty': float(year_data['S-PENALTY-BAL-YEAR-{}'.format(i_padded)]),
            'other': float(year_data['S-OTHER-CHG-BAL-YEAR-{}'.format(i_padded)]),
            'total': float(year_data['S-TOTAL-BALANCE-YEAR-{}'.format(i_padded)]),
            'lienNum': year_data['LIEN-NUMBER-YEAR-{}'.format(i_padded)],
            'solicitor': year_data['ATTORNEY-YEAR-{}'.format(i_padded)],
            'status': year_data['CASE-STATUS-YEAR-{}'.format(i_padded)],
        }
        years.append(year_data_formatted)

    # convert dates to datetime objects
    penalty_calc_date = property_info['penaltyCalcDate']
    penalty_calc_date_datetime = datetime_from_string(penalty_calc_date)
    property_info['penaltyCalcDate'] = penalty_calc_date_datetime

    posted_date = data['PAYMENTS-POSTED-THRU']
    posted_date_datetime = datetime_from_string(posted_date)

    # form response
    data_formatted = {
        'accountNum': data['BRT-NO'],
        'property': property_info,
        'lastPaymentPostedDate': posted_date_datetime,
        'years': years
    }

    return data_formatted

# main entry point
def get_account(event, context):
    params = event.get('pathParameters', {})
    account_num = params.get('account_num')

    # validate search input
    if account_num is None or not re.match('\d{9}', account_num):
        return make_error_response(account_num, 400, 'Invalid account number')

    # prepare and fire request
    params = {'BRT-NO': account_num}

    # get tips url from environment variables
    url = os.environ['TIPS_URL']

    # make request
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        return make_error_response(account_num, 500, 'Error connecting to TIPS API')

    if response.status_code == 404:
        return make_error_response(account_num, 404, 'Account not found')

    # parse xml to python dictionary
    xml = response.text
    data = xmltodict.parse(xml)

    # format data (this cleans up field names and removes unnecessary or unused
    # fields)
    data_formatted = format_data(data)

    # construct response
    body = {
        'query': {
            'accountNum': account_num,
        },
        'data': data_formatted,
    }

    return body
