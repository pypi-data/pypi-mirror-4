#coding=utf8
from datetime import timedelta, datetime
import sys

from mwparserfromhell import parse as parse_markup

from bwikibot.cli import get_wiki, action
from bwikibot.api import datetime2zulu, zulu2datetime, WikiError
from bwikibot.ui import cprint

@action('check_uploads')
def main(start_from, limit):
    ''' Check and mark new files for licensing issues,
        and send messages to uploaders.'''
    wiki = get_wiki()
    if start_from in ('old', 'new'):
        start_from = get_bot_param(wiki, 'BunykBot', start_from + ' start')
    UploadChecker(wiki, start_from, limit)

class UploadChecker:
    def __init__(self, wiki, start_from, limit):
        self.limit = int(limit)
        self.wiki = wiki
        self.marked_counter = 0
        for upload in self.get_uploads(start_from):
            self.check_upload(upload)

    def get_uploads(self, start):
        start = zulu2datetime(start) if start else None
        for upload in self.wiki.logevents(
                event_type='upload', start=start,
                direction='newer',
        ):
            yield upload

    def check_upload(self, upload):
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
        diagnosis = self.diagnose(upload.page)
        cprint('diagnosis:', diagnosis, color='red')
        return 
        if diagnosis:
            summary = license_summaries[diagnosis]
            warn(upload.user, upload.page.title, summary['summary'])
            mark_image(upload.page, summary) 
            self.marked_counter += 1
            if self.marked_counter >= self.limit:
                save_and_exit(datetime2zulu(upload.time))
        else:
            print('ok')

    def diagnose(self, page_to_check):
        '''
            False - ok
            'fair_use': 'Потребує обгрунтування добропорядного користування',
            'author': 'Для нього зазначений автор і джерело, однак нема підтвердження того, що автор цього твору дозволяє ліцензувати цей файл на зазначених умовах'
            'untagged': 'Відсутня правова інформація',
            'no_template': 'Нема шаблону ліцензії',
            'no_source': 'Не зазначене джерело',
        '''
        wikicode = parse_markup(page_to_check.read())
        image_template = None
        fair_use_template = None
        need_source = False
        not_need_source = False
        for template in wikicode.filter_templates(recursive=True):
            t_name = str(template.name).strip()
            t_page = self.wiki.page('Шаблон:' + t_name).resolve_redirect()
            t_name = t_page.title.split(':')[1]
            print(t_name)
            if t_name == 'Зображення': 
                image_template = template
            elif t_name == 'Обґрунтування добропорядного використання':
                fair_use_template = template
            else:
                cprint(t_page.title, color='green')
                for cat in t_page.categories():
                    ct = str(cat.title)
                    print('\t', ct)
                    if ct == warnings_cat:
                        return False
                    if ct == need_source_cat:
                        need_source = True
                    if ct == not_need_source_cat:
                        not_need_source = True

        if not image_template:
            return 'untagged'
        else:
            if need_source:
                source = image_template.get('Джерело').value
                source = fake.sub('', str(source)).strip()
                if source:
                    return False
                else:
                    return 'no_source'
            else:
                if not_need_source:
                    return False
                else:
                    return 'no_template'

last_read_value = None
def get_bot_param(wiki, bot_name, name):
    global last_read_value
    last_read_value = (wiki, bot_name, name)
    res = wiki.page('%s:%s/%s' % (
        wiki.USER_NS_NAME, bot_name, name
    )).read()
    print('%s/%s = %s' % (bot_name, name, res))
    return res

def set_bot_param(wiki, bot_name, name, value):
    wiki.page('%s:%s/%s' % (
        wiki.USER_NS_NAME, bot_name, name
    )).write(value, 'Записуємо зроблене')

def save_and_exit(value):
    if last_read_value:
        set_bot_param(*(last_read_value + (value, )))
    sys.exit(0)


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
        'summary': 'Нема шаблону ліцензії',
    },
}

category_by_date = "Файли з нез'ясованим статусом від %(day)d %(month)s %(year)d"
month_names = [0, 'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']
category_content = "[[Категорія:Файли з нез'ясованим статусом|%(month)d-%(day)02d]]\n"
category_summary = 'Робот: автоматичне створення категорії'


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

warnings_cat = 'Категорія:Шаблони повідомлень про проблеми з завантаженням'
need_source_cat = 'Категорія:Шаблони ліцензій, що потребують джерела'
not_need_source_cat = 'Категорія:Шаблони ліцензій з необов’язковим джерелом'

