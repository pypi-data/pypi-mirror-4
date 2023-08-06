#coding=utf-8

from __future__ import division
from __future__ import unicode_literals

import re
import sys
from datetime import datetime


def skip_boring_lines(lines, is_boring, max_count=4, ellipsis='...'):
    boring_buf = []
    for line in lines:
        if is_boring(line):
            boring_buf.append(line)
        else:
            if len(boring_buf) <= max_count:
                for boring_line in boring_buf:
                    yield boring_line
            else:
                for boring_line in boring_buf[:max_count // 2]:
                    yield boring_line
                yield ellipsis
                for boring_line in boring_buf[-max_count // 2:]:
                    yield boring_line
            boring_buf = []
            yield line
    for line in boring_buf[:max_count]:
        yield line
    if len(boring_buf) > max_count:
        yield ellipsis

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
    ''' Returns datetime '''
    match = re.match('(\d\d):(\d\d), (\d+) (\w+) (\d{4}) \(UTC\)', timestamp, flags=re.U)
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

def on_2():
    return sys.version_info.major == 2

ON_2 = on_2()
