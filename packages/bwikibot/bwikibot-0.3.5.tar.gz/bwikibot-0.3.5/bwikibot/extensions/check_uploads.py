# (C) Code based on code of BotCat (watchcat.py) by Panther (ru.wikipedia)
# Distributed under the terms of the MIT license.

from datetime import timedelta, datetime
import re

from bwikibot.cli import get_wiki, action
from bwikibot.api import datetime2zulu

from . import licenses


debug = False

wait_before_check = timedelta(hours=1, minutes=30)

user_welcome = '{{subst:welcome}}--~~~~\n\n'
problem_images_tag = '<!-- problem images list -->'

user_warning = '''
{{subst:Проблемні зображення}}
%%(images)s
%(tag)s
--~~~~
''' % {'tag': problem_images_tag}

image_issue = '* [[:%(image)s|%(image)s]]: %(summary)s\n'
usertalk_summary = 'Робот: попередження про проблеми з ліцензуванням зображень'
license_summaries= {
    'untagged': {
        'image': '{{subst:nld}}',
        'summary': 'Відсутня правова інформація',
    },
    'no_license': {
        'image': '{{subst:nld}}',
        'summary': 'Нема шаблону ліцензії',
    },
    'no_source': {
        'image': '{{subst:nsd}}',
        'summary': 'Не зазначене джерело',
    },
    'prohibited': {
        'image': '{{subst:nld}}',
        'summary': 'Використана заборонена ліцензія',
    },
    'old': {
        'image': '{{subst:nld}}',
        'summary': 'Використана застаріла ліцензія',
    },
    'no_template': {
        'image': '{{subst:nld}}',
        'summary': 'Ліцензія без шаблону',
    },
}

category_by_date = "Файли з нез'ясованим статусом від %(day)d %(month)s %(year)d"
month_names = [0, 'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']
category_content = "[[Категорія:Файли з нез'ясованим статусом|%(month)d-%(day)02d]]\n"
category_summary = 'Робот: автоматичне створення категорії'

# TODO: check for raw strings
infobox_regex = '\{\{\s*(Зображення|Зображення2)\s*\|.+?\}\}'
source_regex = '\{\{\s*(Зображення|Зображення2).+?Джерело\s*=\s*(?P<src>[^\|\}]+).+?\}\}'
author_regex = '\{\{\s*(Зображення|Зображення2).+?Автор\s*=\s*(?P<auth>[^\|\}]+)[\r\n\|].+?\}\}'
fake_source = '([Аа]втор|[Дд]жерело|[Іі]нтернет|[Ii]nternet|[Нн]евідом[ео]|[Uu]nknown|\?+)'
wikilink_pattern = '\[\[(.+?)\|(.+?)\]\]'
wikilink_replace = '[[1]]'
min_info_length = 8

@action('check_uploads')
def main():
    ''' Check and mark new files for licensing issues,
        and send messages to uploaders.'''
    wiki = get_wiki()
    for upload in get_uploads(wiki):
        check_upload(upload)

def get_uploads(wiki):
    if debug: # faking uploads
        from bwikibot.api import Change
        yield Change(wiki, dict(
            title='Файл:Remainder-pattern1.png',
            timestamp=datetime2zulu(
                datetime.now() - wait_before_check * 2
            ),
            user='BunykBot',
        ))
    else:
        for upload in wiki.logevents(event_type='upload'):
            yield upload

def check_upload(upload):
    if upload.time + wait_before_check > datetime.now():
        return
    print('Checking image {} uploaded at {} by {}'.format(
        upload.page.title,
        datetime2zulu(upload.time),
        upload.user.name,
    ))
    diagnosis = diagnose(upload.page.read())
    if diagnosis:
        print(diagnosis)
        summary = license_summaries[diagnosis]
        mark_image(upload.page, summary) 
        warn(upload.user, upload.page.title, summary['summary'])
    else:
        print('ok')

def mark_image(page, summary):
    check_category(page.wiki)
    page.write(
        page.read() + summary['image'],
        summary['summary']
    )

def check_category(wiki):
    if check_category.created:
        return
    now = datetime.now()
    name = category_by_date % {
        'day': now.day,
        'month': month_names[now.month],
        'year': now.year
    }
    cat = wiki.category(name)
    if not cat.exists():
        cat.write(
            category_content % {
                'day': now.day,
                'month': now.month,
            },
            category_summary
        )
        print('Created', cat)
    check_category.created = True
check_category.created = False

def warn(user, image, problem):
    images = image_issue % {'image': image, 'summary': problem}
    talkpage = user.talkpage()
    talktext = talkpage.read() or user_welcome
    # check if user was warned
    pos = talktext.rfind(problem_images_tag)
    if pos >= 0:
        # check if there was new topics in talk
        pos2 = talktext.rfind('=', pos)
        if pos2 >= 0:
            # if where was - add full message to the end
            talktext += user_warning % {'images': images}
        else:
            # add new lines to old messages
            talktext = talktext[:pos] + images + talktext[pos:]
    else:
        # first warning
        talktext += user_warning % {'images': images}
    talkpage.write(talktext, usertalk_summary)
    print ('User warned: ' + user.name)

def get_regexp(text, flags=0, add_brackets=True):
    # Turn newlines to "|"
    text = re.sub('\s*[\n]+?', '|', text)

    if add_brackets:
        text = '\{\{\s*(Шаблон:)?\s*(' + text + ')\s*\}\}'
    return re.compile(text, flags)

self_licenses = get_regexp(licenses.self_licenses)
free_licenses = get_regexp(licenses.free_licenses)
unfree_licenses = get_regexp(licenses.unfree_licenses)
unfree_licenses_source = get_regexp(licenses.unfree_licenses_source, re.DOTALL)
old_licenses = get_regexp(licenses.old_licenses)
prohibited_licenses = get_regexp(licenses.prohibited_licenses)
warnings = get_regexp(licenses.warnings)
no_template = get_regexp(licenses.no_template, 0, False)

infobox = re.compile(infobox_regex, re.DOTALL)
source = re.compile(source_regex, re.DOTALL)
author = re.compile(author_regex, re.DOTALL)
fake = re.compile(fake_source, re.DOTALL)
comment = re.compile(r'<!\-\-.*?\-\->', re.DOTALL)
wikilink = re.compile(wikilink_pattern)

def diagnose(text_to_check):
    text = text_to_check.strip()
    #Удаляем из текста комментарии
    text = comment.sub('', text).strip()
    if not text:
        return 'untagged'

    #Упрощаем вики-ссылки, чтобы символ "|" не мешал обработке полей шаблонов
    text = wikilink.sub(wikilink_replace, text)
    #Ищем вхождение каждого класса лицензий
    isSelf = self_licenses.search(text)
    isFree = free_licenses.search(text)
    isUnfree = unfree_licenses.search(text)
    isUnfreeSource = unfree_licenses_source.search(text)
    isOld = old_licenses.search(text)
    isProhibited = prohibited_licenses.search(text)
    isWarn = warnings.search(text)
    isNoTemplate = no_template.search(text)
    if (isSelf or isWarn):
        #Лицензия self или изображение уже отмечено
        return False
    elif (isProhibited):
        #Запрещенная лицензия
        return 'prohibited'
    elif (isOld and not isFree and not isUnfreeSource and not isUnfree):
        #Устаревшая лицензия
        return 'old'
    elif (isFree or isUnfreeSource):
        #Есть лицензия, требующая указания источника
        #Есть шаблон описания?
        isInfobox = infobox.search(text)
        #В этом шаблоне заполненен источник?
        isSource = source.findall(text)
        #В этом шаблоне заполненен автор?
        isAuthor = author.search(text)
        if (isInfobox):
            if (isSource):
                srcTxt = ''
                for part in isSource:
                    srcTxt += part[1]
                #Удаляем из поля "источник" стандартные липовые фразы
                srcTxt = fake.sub('', srcTxt).strip()
            else:
                srcTxt = ''
            if (isAuthor):
                authTxt = isAuthor.group('auth')
                #Удаляем из поля "автор" стандартные липовые фразы
                authTxt = fake.sub('', authTxt).strip()
            else:
                authTxt = ''
            srcComplex = srcTxt + authTxt
        else:
            #Удаляем из текста шаблоны и все заголовки
            srcComplex = re.sub('\{\{.+?\}\}', '', text)
            srcComplex = re.sub('=+.+?=+', '', srcComplex).strip()
        #Если в итоге ничего не осталось, то считаем, что источника нет
        if (len(srcComplex) <= min_info_length):
            return 'no_source'
    elif (isUnfree):
        return False
    else:
        if (isNoTemplate):
            #Лицензия без шаблона
            return 'no_template'
        else:
            return 'no_license'

    return False
