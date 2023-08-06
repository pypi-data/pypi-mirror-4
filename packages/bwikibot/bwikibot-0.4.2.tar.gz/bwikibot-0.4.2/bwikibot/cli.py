from datetime import datetime
import sys
import os

from bwikibot.api import Wiki, datetime2zulu
from bwikibot.ui import shift_block

SESSION_FILE = 'cli.session'
SECONDARY_SESSION_FILE = 'cli_secondary.session'

def main():
    run(*sys.argv)

def run(*argv):
    load_extensions()
    if len(argv) < 2:
        print('You should pass action:')
        show_doc(actions)
    else:
        action = actions.get(argv[1])
        if action:
            action(*argv[2:])
        else:
            print('Action "%s" not found.' % argv[1])
            print('Available actions: %s' % ', '.join(actions.keys()))
    
actions = {}

def action(name):
    ''' Decorator to register function as action '''
    def decorate(f):
        actions[name] = f
        return f
    return decorate

def load_extensions():
    ''' Trigger action decorator in extensions '''
    from bwikibot import extensions
    from bwikibot.spell import corrector

def show_doc(actions):
    ''' Prints documentation about actions '''
    maxname = max(len(k) for k in actions.keys())
    for action, function in actions.items():
        doc = function.__doc__ or ''.join((
            function.__module__, '.',
            function.__name__, ' has no docstring'
        ))
        print('{:{width}s} - {}'.format(
            action,
            shift_block(doc, maxname + 5),
            width=maxname,
        ))

def get_wiki(session_file=SESSION_FILE):
    wiki = Wiki()
    wiki.session_file(session_file)
    return wiki

def get_secondary_wiki():
    return get_wiki(session_file=SECONDARY_SESSION_FILE)


def throttle(session_file, delay):
    wiki = get_wiki(session_file)
    if not delay:
        print(wiki.throttle)
    else:
        wiki.throttle = float(delay)
        wiki.save(session_file)

@action('throttle')
def throttle1(delay=None):
    ''' Set or get delay between queries.  '''
    throttle(SESSION_FILE, delay)

@action('throttle2')
def throttle2(delay=None):
    ''' Set or get delay between queries for secondary wiki. '''
    throttle(SECONDARY_SESSION_FILE, delay)


def read_page(session_file, *args):
    name = ' '.join(args).strip()
    if not name:
        print('Pass page name as last param')
        return
    wiki = get_wiki(session_file)
    print(wiki.page(name).read())

@action('read')
def read_page1(*args):
    ''' Print page which's name passed in param to stdout '''
    read_page(SESSION_FILE, *args)

@action('read2')
def read_page2(*args):
    ''' Print page from secondary wiki which's name passed in param to stdout '''
    read_page(SECONDARY_SESSION_FILE, *args)

def autocomplete(session_file, *args):
    prefix = ' '.join(args)
    wiki = get_wiki(session_file)
    print('\n'.join(
        wiki.opensearch(prefix)
    ))

@action('autocomplete')
def autocomplete1(*args):
    ''' Print list of page names which starts from passed prefix '''
    autocomplete(SESSION_FILE, *args)

@action('autocomplete2')
def autocomplete1(*args):
    ''' Print list of page names which starts from passed prefix for secondary wiki'''
    autocomplete(SECONDARY_SESSION_FILE, *args)

def login(session_file):
    try:
        os.remove(session_file)
    except OSError:
        pass
    get_wiki(session_file)

@action('login')
def login1():
    ''' Login to primary wiki '''
    login(SESSION_FILE)

@action('login2')
def login2():
    ''' Login to secondary wiki '''
    login(SECONDARY_SESSION_FILE)


@action('logout')
def logout():
    ''' Delete session file '''
    os.remove(SESSION_FILE)

@action('logout2')
def logout2():
    ''' Delete session file '''
    os.remove(SECONDARY_SESSION_FILE)

def write_page(session_file, *args):
    name = ' '.join(args)
    wiki = get_wiki()

    text = []
    for line in sys.stdin:
        text.append(line)

    wiki.page(name).write(''.join(text), 'cli editing')

@action('write')
def write_page1(*args):
    ''' Read text from stdio and save to page with name passed in param '''
    write_page(SESSION_FILE, *args)

@action('write2')
def write_page2(*args):
    ''' Read text from stdio and save to page on secondary wiki with name passed in param '''
    write_page(SECONDARY_SESSION_FILE, *args)

@action('now')
def get_now():
    ''' Prints current ISO-formatted zulu time '''
    print(datetime2zulu(datetime.utcnow()))
