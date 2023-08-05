import sys
import os

from bwikibot.api import Wiki
from bwikibot.ui import shift_block
from bwikibot import translator

SESSION_FILE = 'cli.session'

def get_wiki():
    wiki = Wiki('', throttle=0)
    wiki.session_file(SESSION_FILE)
    return wiki

def read_page(*args):
    ''' Print page which's name passed in param to stdout '''
    name = ' '.join(args).strip()
    if not name:
        print('Pass page name as last param')
        return
    wiki = get_wiki()
    print(wiki.page(name).read())

def autocomplete(*args):
    ''' Print list of page names which starts from passed prefix '''
    prefix = ' '.join(args)
    wiki = get_wiki()
    print('\n'.join(
        wiki.opensearch(prefix)
    ))

def login(*args):
    ''' Login to site with domain passed in param '''
    url = ' '.join(args).strip()
    if not url:
        print('you should pass domain like uk.wikipedia.org')
        return
    wiki = Wiki('http://%s/w/api.php' % url, throttle=0)
    wiki.session_file(SESSION_FILE)

def change_endpoint(*args):
    ''' Change endpoing but don't change cookies (for wiki families) '''
    url = ' '.join(args)
    wiki = Wiki('', throttle=0)
    wiki.session_file(SESSION_FILE)
    wiki.endpoint = 'http://%s/w/api.php' % url
    wiki.save(SESSION_FILE)

def logout(ignored_param):
    ''' Delete session file '''
    os.remove(SESSION_FILE)

def write_page(*args):
    ''' Read text from stdio and save to page with name passed in param '''
    name = ' '.join(args)
    wiki = get_wiki()

    text = []
    for line in sys.stdin:
        text.append(line)

    wiki.page(name).write(''.join(text), 'cli editing')

actions = {
    'read': read_page,
    'autocomplete': autocomplete,
    'login': login,
    'endpoint': change_endpoint,
    'logout': logout,
    'write': write_page,
    'translate': translator.main,
}

def run(*argv):
    if len(argv) < 2:
        print('You should pass action:')
        for action, function in actions.items():
            print('{:15s} - {}'.format(
                action,
                shift_block(function.__doc__, 20)
            ))
        return

    actions[argv[1]](*argv[2:])

def main():
    run(*sys.argv)

if __name__=="__main__":
    main()
