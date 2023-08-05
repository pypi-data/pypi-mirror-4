# (C) Code based on code of BotCat (watchcat.py) by Panther (ru.wikipedia)
# Distributed under the terms of the MIT license.

from datetime import timedelta, datetime
import re
import sys

from bwikibot.cli import get_wiki, action
from bwikibot.api import datetime2zulu, zulu2datetime, WikiError
from bwikibot.api import Change

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
min_info_length = 8

@action('check_uploads')
def main(start_from, limit):
    ''' Check and mark new files for licensing issues,
        and send messages to uploaders.'''
    wiki = get_wiki()
    for upload in get_uploads(wiki, start_from):
        check_upload(upload, int(limit))

def get_uploads(wiki, start):
    if debug: # faking uploads
        yield Change(wiki, dict(
            title='Файл:Remainder-pattern1.png',
            timestamp=datetime2zulu(
                datetime.utcnow() - wait_before_check * 2
            ),
            user='BunykBot',
        ))
    else:
        start = zulu2datetime(start) if start else None
        for upload in wiki.logevents(
                event_type='upload', start=start,
                direction='newer',
        ):
            yield upload

counter = 0

def check_upload(upload, limit):
    global counter
    if upload.time + wait_before_check > datetime.utcnow():
        return
    print('Checking image {} uploaded at {} by {}'.format(
        upload.page.title,
        datetime2zulu(upload.time),
        upload.user.name,
    ))
    if not upload.page.exists():
        print('already deleted')
        return
    redirect = upload.page.redirect()
    if redirect:
        print('Redirect to:', redirect.title)
        return
    diagnosis = diagnose(upload.page.read())
    if diagnosis:
        print(diagnosis)
        summary = license_summaries[diagnosis]
        mark_image(upload.page, summary) 
        warn(upload.user, upload.page.title, summary['summary'])
        counter += 1
        if counter > limit:
            sys.exit(0)
    else:
        print('ok')

def mark_image(page, summary):
    check_category(page.wiki)
    try:
        page.write(
            (page.read() or '') + summary['image'],
            summary['summary']
        )
    except WikiError as e:
        print('Cannot mark image because of', e)

def check_category(wiki):
    if check_category.created:
        return
    now = datetime.utcnow()
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
    try:
        talkpage.write(talktext, usertalk_summary)
        print('User warned: ' + user.name)
    except Exception as e:
        print('User {} not warned because of {}'.format(user.name, e))

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

def simplify_wikilinks(text):
    ''' remove '|' characters '''
    return re.sub(r'\[\[(.+?)\|(.+?)\]\]', '[[1]]', text)

def diagnose(text_to_check):
    if not text_to_check:
        return 'untagged'
    text = text_to_check.strip()
    # remove comments
    text = comment.sub('', text).strip()
    if not text:
        return 'untagged'

    text = simplify_wikilinks(text)

    # searching for licenses
    is_self = self_licenses.search(text)
    is_free = free_licenses.search(text)
    is_unfree_source = unfree_licenses_source.search(text)
    is_warn = warnings.search(text) # already marked

    if is_self or is_warn:
        return False
    elif prohibited_licenses.search(text):
        return 'prohibited'
    elif is_free or is_unfree_source:
        # license need source
        if not has_source(text):
            return 'no_source'
    elif unfree_licenses.search(text):
        return False
    elif old_licenses.search(text):
        return 'old'
    else:
        if no_template.search(text):
            #Лицензия без шаблона
            return 'no_template'
        else:
            return 'no_license'

    return False

def has_source(text):
    #В этом шаблоне заполненен источник?
    is_source = source.findall(text)
    #В этом шаблоне заполненен автор?
    is_author = author.search(text)
    if infobox.search(text):
        if is_source:
            src_txt = ''
            for part in is_source:
                src_txt += part[1]
            #Удаляем из поля "источник" стандартные липовые фразы
            src_txt = fake.sub('', src_txt).strip()
        else:
            src_txt = ''
        if is_author:
            auth_txt = is_author.group('auth')
            #Удаляем из поля "автор" стандартные липовые фразы
            auth_txt = fake.sub('', auth_txt).strip()
        else:
            auth_txt = ''
        src_complex = src_txt + auth_txt
    else:
        #Удаляем из текста шаблоны и все заголовки
        src_complex = re.sub('\{\{.+?\}\}', '', text)
        src_complex = re.sub('=+.+?=+', '', src_complex).strip()
    #Если в итоге ничего не осталось, то считаем, что источника нет
    return len(src_complex) > min_info_length
