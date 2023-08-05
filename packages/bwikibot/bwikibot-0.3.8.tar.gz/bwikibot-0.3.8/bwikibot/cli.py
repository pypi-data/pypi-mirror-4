from datetime import datetime
import sys
import os

from bwikibot.api import Wiki, datetime2zulu
from bwikibot.ui import shift_block

SESSION_FILE = 'cli.session'

def main():
    run(*sys.argv)

def run(*argv):
    load_extensions()
    if len(argv) < 2:
        print('You should pass action:')
        show_doc(actions)
    else:
        actions[argv[1]](*argv[2:])

    
actions = {}

def action(name):
    ''' Decorator to register function as action '''
    def decorate(f):
        actions[name] = f
        return f
    return decorate

def load_extensions():
    ''' trigger action decorator in extensions '''
    from bwikibot import extensions

def show_doc(actions):
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

def get_wiki():
    wiki = Wiki()
    wiki.session_file(SESSION_FILE)
    return wiki

@action('throttle')
def throttle(delay=None):
    ''' Set or get delay between queries '''
    wiki = get_wiki()
    if not delay:
        print(wiki.throttle)
    else:
        wiki.throttle = float(delay)
        wiki.save(SESSION_FILE)


@action('read')
def read_page(*args):
    ''' Print page which's name passed in param to stdout '''
    name = ' '.join(args).strip()
    if not name:
        print('Pass page name as last param')
        return
    wiki = get_wiki()
    print(wiki.page(name).read())


@action('autocomplete')
def autocomplete(*args):
    ''' Print list of page names which starts from passed prefix '''
    prefix = ' '.join(args)
    wiki = get_wiki()
    print('\n'.join(
        wiki.opensearch(prefix)
    ))

@action('login')
def login():
    ''' Login to site with domain passed in param '''
    try:
        logout()
    except OSError:
        pass
    get_wiki()


@action('endpoint')
def change_endpoint(*args):
    ''' Change endpoing but don't change cookies (for wiki families) '''
    url = ' '.join(args)
    wiki = get_wiki()
    wiki.set_endpoint(url)
    wiki.save(SESSION_FILE)


@action('logout')
def logout():
    ''' Delete session file '''
    os.remove(SESSION_FILE)

@action('write')
def write_page(*args):
    ''' Read text from stdio and save to page with name passed in param '''
    name = ' '.join(args)
    wiki = get_wiki()

    text = []
    for line in sys.stdin:
        text.append(line)

    wiki.page(name).write(''.join(text), 'cli editing')

@action('now')
def get_now():
    ''' Prints current ISO-formatted zulu time '''
    print(datetime2zulu(datetime.utcnow()))
