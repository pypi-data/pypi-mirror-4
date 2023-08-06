#coding=utf-8
'''
User interface utilities
'''

from __future__ import print_function

from bwikibot.utils import skip_boring_lines

#from mako.template import Template

colors = {
    '-': 91,
    '+': 92,
    '?': 94,
    'red': 91,
    'green': 92,
    'blue': 94,
}

def cprint(*args, **kwargs):
    color = colors.get(kwargs.get('color'), 0)
    if color:
        print('\033[%sm' % color, *(args + ('\033[0m',)))
    else:
        print(*args)

def print_diff(text_a, text_b):
    ''' Print difference between two values '''
    from difflib import ndiff
    a_lines = text_a.splitlines(1)
    b_lines = text_b.splitlines(1)
    diff = ndiff(a_lines, b_lines)

    for line in skip_boring_lines(diff, lambda x: x[0] == ' '):
        cprint(line[:-1], color=line[0])

def ask_y_n(question):
    while True:
        ans = input(question)
        if ans.lower() == 'y':
            return True
        if ans.lower() == 'n':
            return False
        if not ans.strip():
            return ''
        print('дозволені тільки відповіді y/n та порожня')


def shift_block(block, spaces):
    ''' shifts lines of block of text to right '''
    lines = block.splitlines()
    lines = [' ' * spaces + line.strip() for line in lines]
    return '\n'.join(lines).strip()

def link(text):
    print(text)
    if isinstance(text, tuple):
        text = '|'.join(text)
    return '[[{}]]'.format(text) if text else text

def link_list(items, separator=', '):
    if isinstance(items, str):
        items = eval(items)
    return separator.join(map(link, items))

def render(template, **kwargs):
    return Template(template).render(
        link=link,
        link_list=link_list,
        **kwargs
    )
