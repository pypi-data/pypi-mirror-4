#coding=utf-8
from collections import defaultdict
import os
import sys

from mwparserfromhell import parse as parse_markup

from bwikibot.cli import get_wiki, get_secondary_wiki, action
from bwikibot.ui import render

class ImportException(Exception):
    def __init__(self, msg):
        self.msg = msg

@action('import_poster')
def import_poster(film_name, source='en'):
    ''' Імпортувати постер для статті, і додати його в шаблон фільму.
        Перший параметр - назва статті фільму.
        другий - джерело. url або мовний код. Якщо мовний код - автора та 
    '''
    wiki = get_wiki()
    try:
        image_name, author, source = download_poster_to_tmp(wiki, source, film_name)
        upload_poster_to_dest_wiki(wiki, film_name, source, author, image_name)
        add_poster_to_infobox(
            wiki.page(film_name).resolve_redirect(),
            image_name
        )
        os.remove('tmp')
    except ImportException as e:
        print(e.msg)

def download_poster_to_tmp(wiki, source, film_name):
    image_name, author = None, None
    if source in ('en', 'ru', 'de', 'fr'):
        sfilm_name = (wiki
            .page(film_name)
            .resolve_redirect()
            .interwikis().get(source)
        )
        if not sfilm_name:
            raise ImportException("Вибачте, не знайдено інтервікі до %s" % film_name)

        swiki = wiki.get_unified_login_to('%s.wikipedia.org' % source)
        image_name, author = download_poster_from_source_wiki(swiki, sfilm_name)
        source = 'http://{lang}.wikipedia.org/wiki/File:{image_name}'.format(
            lang=source, image_name = image_name
        )
    else:
        try:
            headers, content = wiki.http.request(source)
        except:
            raise ImportException("Не можу завантажити %s" % source)
        with open('tmp', 'wb') as f:
            f.write(content)
    image_name = image_name or input('Назва файлу для картинки:')
    author = author or input('Автор:')
    return image_name, author, source

def download_poster_from_source_wiki(swiki, sfilm_name):
    sfp = swiki.page(sfilm_name).resolve_redirect()
    image = None
    for template in parse_markup(sfp.read()).filter_templates():
        tn = str(template.name).strip().lower().replace('_', ' ')
        if (tn.startswith('infobox') and tn.endswith('film')):
            image = template.get('image')
            distributor = template.get('distributor')
    image_name = str(image.value).strip() if image else ''
    if not image_name:
        raise ImportException('Зображення не знайдене на сторінці %s' % sfilm_name)

    image = swiki.file(image_name)
    image.download('tmp')

    distributor = str(distributor.value).strip() if distributor else ''
    return image_name, distributor

def upload_poster_to_dest_wiki(wiki, film_name, source, author, image_name):
    dfp = wiki.page(film_name)
    fp = wiki.file(image_name)
    if fp.exists():
        raise ImportException('Зображення "%s" вже існує' % image_name)

    description = '''{{{{Зображення
|Назва={film_name}
|Опис=Постер фільму "[[{film_name}]]"
|Автор={author}
|Джерело={source}
|Час створення=
|Ліцензія=нижче
}}}}
{{{{subst:Постер з ОДВ|{film_name}}}}}'''.format(
        film_name=film_name,
        author=author,
        source=source
    )
    fp.upload('tmp', 'Автоматичний імпорт постера', description)

def add_poster_to_infobox(page, poster):
    include = '[[Файл:%s|200px]]' % poster
    markup = parse_markup(page.read())
    for t in markup.filter_templates():
        if str(t.name).strip().lower() == 'фільм':
            t.add('плакат',
                include,  
                force_nonconformity=True
            )
    page.write(str(markup), 'Додав постер фільму')


template = r"""
{{Фільм
| українська назва  = ${title_uk}
| оригінальна назва = ${title}
| плакат            = [[${poster_file}|200px]]
| режисер           = ${director|link}
| продюсер          = ${producer|link}
| сценарист         = ${written_by|link}
| актори            = ${actors|link_list}
| кінокомпанія      = ${distributors|link_list}
| країна            = ${countries|link_list}
| рік               = ${year}
| мова              = ${languages|link_list}
| тривалість        = ${running_minutes} хв.
| кошторис          = ${budget}
| касові збори      = ${box_office}
| ідентифікатор     = ${imdb_id}
}}
'''${title_uk}''' ({{lang-${lang_code}|${title}}}) - фільм.

== В ролях ==
% for actor in actors:
* ${actor|link}
% endfor

== Посилання ==
% if imdb_id:
* {{Imdb title|${imdb_id}|${title}}} 
% endif

${link_list(categories, separator='\n')}

${interwikis}
"""

info = defaultdict(lambda :'',
    title_uk='Хмарний Атлас',
    title='Cloud Atlas',
    poster_file='Файл:example.jpg',
    director='director',
    producer='producer',
    written_by='сценарист',
    actors=['Том Хенкс', 'Холлі Бері'],
    distributors=['Warner brothers'],
    countries=['США'],
    year=2012,
    languages=[('Англійська мова', 'Англійська')],
    running_minutes=172,
    budget='102000000',
    box_office='102 млн.',
    imdb_id=1371111,
    lang_code='en',
    categories=['Категорія:Фільми {}'.format(2012),],
    interwikis='[[en:Cloud Atlas]]',
)

if __name__ == '__main__':
    print(render(template, **info))
