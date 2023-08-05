import re
from datetime import datetime

months = [
    'нульня',
    'січня',
    'лютого',
    'березня',
    'квітня',
    'травня',
    'липня',
    'серпня',
    'вересня',
    'жовтня',
    'листопада',
    'листопада',
    'грудня'
]

months_nums = {name: num for num, name in enumerate(months)}

def parse_signature_time(timestamp):
    ''' Returns datetime
        >>> parse_signature_time('23:54, 13 листопада 2012 (UTC)')
        datetime.datetime(2012, 11, 13, 23, 54)
    '''
    match = re.match('(\d\d):(\d\d), (\d+) (\w+) (\d{4}) \(UTC\)', timestamp)
    if not match:
        return
    groups = match.groups()

    return datetime(
        hour=int(groups[0]),
        minute=int(groups[1]),
        day=int(groups[2]),
        month=months_nums[groups[3]],
        year=int(groups[4])
    )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
