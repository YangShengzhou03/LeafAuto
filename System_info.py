import configparser
import os
import sys
from datetime import timedelta, datetime

import wmi

from common import get_current_time

CONFIG_PATH = '_internal/system_info.ini'
MAX_RETRIES = 5

DEFAULT_VALUES = {
    'version': '4.3',
    'error_sound': 'True',
    'net_time': 'False',
    'auto_update': 'True',
    'close_option': 'True',
    'membership': 'Free',
    'motherboardsn': 'LEAF AUTO',
    'membership_class': '0',
    'language': 'cn',
    'serve_lock': 'False',
    'add_timestep': 10
}


def get_motherboard_serial_number():
    c = wmi.WMI()
    for board_id in c.Win32_BaseBoard():
        return str(board_id.SerialNumber).strip()
    return 'Null'


def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def ensure_config_file_exists():
    global config
    retries = 0
    while retries < MAX_RETRIES:
        if not os.path.exists(CONFIG_PATH):
            create_config_file()
            retries += 1
            continue

        try:
            config = read_config()

            missing_keys = any(not config.has_option('SystemInfo', key) for key in
                               ['membership', 'expiration_time', 'motherboardsn'])
            if missing_keys:
                os.remove(CONFIG_PATH)
                retries += 1
                continue

            membership = config.get('SystemInfo', 'membership', fallback='Free')
            expiration_time_str = config.get('SystemInfo', 'expiration_time', fallback=None)
            motherboard_sn = config.get('SystemInfo', 'motherboardsn', fallback=None)
            current_motherboard_sn = get_motherboard_serial_number()

            if membership != 'Free':
                if expiration_time_str and get_current_time('mix') > datetime.strptime(expiration_time_str,
                                                                                       '%Y-%m-%d %H:%M:%S'):
                    write_key_value('membership', 'Free')
                    write_key_value('motherboardsn', 'LEAF AUTO')
                    write_key_value('membership_class', str(int(read_key_value('membership_class')) + 1))
                    continue

                if current_motherboard_sn is None or (motherboard_sn and motherboard_sn != current_motherboard_sn):
                    os.remove(CONFIG_PATH)
                    retries += 1
                    continue

            return True

        except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            os.remove(CONFIG_PATH)
            retries += 1

    if retries >= MAX_RETRIES:
        sys.exit()


def create_config_file():
    config = configparser.ConfigParser()
    config['SystemInfo'] = {
        'version': '4.3',
        'error_sound': 'True',
        'net_time': 'False',
        'auto_update': 'True',
        'close_option': 'True',
        'expiration_time': (get_current_time('net') + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        'membership': 'Free',
        'motherboardsn': 'LEAF AUTO',
        'membership_class': '0',
        'language': 'cn',
        'serve_lock': 'False',
        'add_timestep': '10'
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)


def read_key_value(key):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    try:
        return config.get('SystemInfo', key, fallback=DEFAULT_VALUES.get(key))
    except configparser.Error as e:
        return DEFAULT_VALUES.get(key)


def write_key_value(key, value):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if not config.has_section('SystemInfo'):
        config.add_section('SystemInfo')
    config.set('SystemInfo', key, value)
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
