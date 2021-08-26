import string
import random
from django.core import signing
import binascii
import os
from datetime import datetime


def prepare_string_upper(string):
    return string.upper()


def prepare_string_title(string):
    return string.title()


def get_or_none(model, **kwargs):
    try:
        result = model.objects.get(**kwargs)
        return result
    except:
        return None


def is_password_secure(password):
    allowed = string.punctuation + string.ascii_letters + string.digits
    rules = [
        lambda s: all(x in allowed for x in s),
        lambda s: len(s) >= 8,
    ]
    return all(rule(password) for rule in rules)


def generate_phone_secret():
    t = string.digits
    secret = random.sample(t, 6)
    return "".join(secret)


def generate_user_secret(user_id):
    value = signing.dumps(
        {'user_id': user_id}
    )
    print(value)
    return value


def parse_secret(sign):
    try:
        value = signing.loads(
            sign
        ).get('user_id')
    except Exception as e:
        value = False
    return value


def is_valid_user(model, pk, request):
    if pk:
        user = model.objects.get(pk=pk)
    else:
        user = []
    return \
        (
                request.user == user or request.user.is_superuser or request.user.role == 'operator'
        )


def generate_registration_token():
    return binascii.hexlify(os.urandom(20)).decode()

def columns(type):
    if type == 'users':
        return ['email', 'phone_number', 'created_at', 'name', 'user_plan']
    if type == 'suppliers':
        return ['email', 'name', 'phone_number', 'callout_radius', 'location', 'services', 'created_at', 'cells', 'stars', 'accreditations']
    return False

def generate_users(users_data, row_num, fields, rows, worksheet):
    for data in users_data:
        row_num += 1
        row = []

        for field in data:
            if field in fields:
                if field == 'created_at':
                    date_old = data[field].split('T')
                    date = datetime.strptime(date_old[0], '%Y-%m-%d').strftime('%d/%m/%Y')
                    row.append(date)
                elif field == 'user_plan':
                    if data[field] is not None:
                        row.append(data[field]['plan']['name'])
                    else:
                        row.append('None')
                else:
                    row.append(data[field])
        rows.append(row)

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

def generate_suppliers(users_data, row_num, fields, rows, worksheet):
    for data in users_data:
        row_num += 1
        row = []

        for field in data:
            if field in fields:
                if field == 'location':
                    row.append(data[field]['address'])
                elif field == 'services':
                    str = ''
                    for s in data[field]:
                        if len(str) != 0:
                            str += f', {s["name"]}'
                        else:
                            str += f'{s["name"]} '
                    row.append(str)
                elif field == 'cells':
                    str = ''
                    for c in data[field]:
                        if len(str) != 0:
                            str += f', {c["name"]}'
                        else:
                            str += f'{c["name"]} '
                    row.append(str)
                elif field == 'accreditations':
                    str = ''
                    for a in data[field]:
                        if len(str) != 0:
                            str += f', {a["name"]}'
                        else:
                            str += f'{a["name"]} '
                    row.append(str)
                else:
                    if field == 'created_at':
                        date_old = data[field].split('T')
                        date = datetime.strptime(date_old[0], '%Y-%m-%d').strftime('%d/%m/%Y')
                        row.append(date)
                    else:
                        row.append(data[field])
        rows.append(row)

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value


def nearest(items):
    now = datetime.now()
    for item in items:
        for field in ['action_start', 'action_end']:
            if (item[field] is not None) and (item[field] != ''):
                item[field] = datetime.strptime(item[field], '%Y-%m-%dT%H:%M:%S.%f')
    old = [x for x in items if condition_old(x, now)]
    current = [x for x in items if condition_current(x, now)]
    next = [x for x in items if condition_next(x, now)]
    if len(current) > 0:
        address = current[0]
    else:
        if len(next) > 0:
            address = next[0]
        else:
            if len(old) > 0:
                address = old[len(old) - 1]
            else:
                address = {'action_start': '', 'action_end': ''}
    return address
    # if len(array) > 1:
    #     return min(array, key=lambda x: abs(x['date_time'] - datetime.now()))
    # else:
    #     return None


def condition_old(x, now):
    return x['action_start'] < now and x['action_end'] < now


def condition_current(x, now):
    return x['action_start'] < now and x['action_end'] > now


def condition_next(x, now):
    return x['action_start'] > now and x['action_end'] > now
