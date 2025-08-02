# -*- coding:utf-8 -*-
import json
# from func_timeout import func_set_timeout, FunctionTimedOut

cookies_variable = [
    {'domain': '.learning.hzrs.hangzhou.gov.cn', 'httpOnly': False, 'name': 'Hm_lpvt_de1beef062ce941f1ebcd905eab09f70',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1688612433'},
    {'domain': 'learning.hzrs.hangzhou.gov.cn', 'httpOnly': True, 'name': 'learning', 'path': '/', 'sameSite': 'Lax',
     'secure': False, 'value': '!5E2mh5MgholgvVZlArjSxGGwuW5rG/+q1g4ln4zJOWmjdpVI2uIssCaUgqV8jimyA3184ZzMPRs+kQ=='},
    {'domain': 'learning.hzrs.hangzhou.gov.cn', 'httpOnly': False, 'name': 'SESSID', 'path': '/', 'sameSite': 'Lax',
     'secure': False, 'value': '9o92qomffk03d6qpkqnvs8j1n7'},
    {'domain': '.learning.hzrs.hangzhou.gov.cn', 'expiry': 1720163633, 'httpOnly': False,
     'name': 'Hm_lvt_de1beef062ce941f1ebcd905eab09f70', 'path': '/', 'sameSite': 'Lax', 'secure': False,
     'value': '1688627058,1688627135,1688627262,1688627453'},
    {'domain': 'learning.hzrs.hangzhou.gov.cn', 'httpOnly': False, 'name': '__onlineflag__', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'Y'},
    {'domain': 'learning.hzrs.hangzhou.gov.cn', 'expiry': 1723186358, 'httpOnly': False, 'name': '__loginuser__',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '360222198908170016'},
    {'domain': 'learning.hzrs.hangzhou.gov.cn', 'expiry': 1723186358, 'httpOnly': False, 'name': '__sid__', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '6111319813'}]


# def time_out(func, *args, **kwargs):
#     def wrapper(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#             return result
#         except FunctionTimedOut as e:
#             print(f'timeout: {e}')
#
#     return wrapper


def load_json(file_name):
    try:
        with open(file_name, encoding="utf8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(file_name, encoding="gbk") as f:
            return json.load(f)


def save_json(data, file_name):
    with open(file_name, 'w', encoding="utf8") as f:
        json.dump(data, f)
