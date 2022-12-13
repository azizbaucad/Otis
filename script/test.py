import yaml
from datetime import datetime, date
import datetime as dt
def configuration(key):
    with open('config.yaml') as parameters:
        dict = yaml.safe_load(parameters)
        key = dict[key]
        if key is not None and key != "":
            return key
        else:
            return "ErrorKey: Key is Null"

if __name__ == '__main__':
    date_str = '13-12-2022 08:42:00'
    date_str2 = '2022-12-13 08:42:00'
    print(f'Date STr: {date_str, type(date_str)}')
    #date_start = dt.datetime.strptime(date_str2, '%Y-%m-%d %H:%M:%S')
    date_start = dt.datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
    print('-----------')
    print(f'Date Start format: {date_start, type(date_start)}')

