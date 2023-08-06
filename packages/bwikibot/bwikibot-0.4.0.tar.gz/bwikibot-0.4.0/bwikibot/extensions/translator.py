import argparse
from pprint import pprint
import sys

from bwikibot.api import Wiki
from bwikibot import lexer
from bwikibot.cli import action

parser = argparse.ArgumentParser(
    description='Get some text and print another'
)

parser.add_argument(
    '-f', dest='from_lang', default="en",
    help='language to translate from'
)
parser.add_argument(
    '-t', dest='to_lang', default="uk",
    help='language to translate to'
)

traslate_page_name = None

@action('translate')
def main(*argv):
    ''' Automate translation of wikitext from one language to another
        -f from_lang (for example 'en')
        -t to lang (for example 'uk')
    '''
    global traslate_page_name
    args = parser.parse_args(argv)

    wiki = Wiki('http://%s.wikipedia.org/w/api.php' % args.from_lang)
    traslate_page_name = get_translate_page_name(wiki, args)
    for line in sys.stdin:
        if line.strip():
            print(translate(line[:-1]))
        else:
            print()

def get_translate_page_name(wiki, args):
    def traslate_page_name(name):
        page = wiki.page(name)
        for i in range(5): # follow 5 redirects max
            redirect = page.redirect()
            if not redirect:
                break
            else:
                page = redirect
        return page.interwikis().get(args.to_lang, name)
    return traslate_page_name

def save_case(text, translation):
    if text[0].islower():
        return translation[0].lower() + translation[1:]
    else:
        return translation

def translate_segment(text):
    res = save_case(text, traslate_page_name(text))
    return res

def translate(text):
    tokens = lexer.tokenize(text)
    res = []
    for token in tokens:
        if token[0] == lexer.LINK:
            trans = translate_segment(token[1])
            full = token[1] == token[2] and ':' in token[1]
            token = token[0], trans, trans if full else token[2]
        res.append(lexer.token_text(token))
    return ''.join(res)
