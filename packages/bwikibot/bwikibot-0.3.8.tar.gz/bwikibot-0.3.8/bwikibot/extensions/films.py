from collections import defaultdict

from bwikibot.ui import render

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
