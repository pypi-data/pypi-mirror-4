'''
Скрипти для війни з ботами на cybportal.univ.kiev.ua/wiki

Деталі:
http://bunyk.wordpress.com/2012/03/27/cybwiki-episode-ii-attack-of-the-botes/
'''

from bwikibot.api import Wiki
from bwikibot.ui import ask_y_n
from bwikibot.cli import action

@action('cybwiki_stop_spam')
def main():
    ''' Block spammers and delete their creations on cybwiki'''
    wiki = get_wiki()
    kill_registered(wiki)
    #protect_all_pages(wiki)


def protect_all_pages(wiki):
    for i, page in enumerate(wiki.all_pages):
        print(i, page.title)
        page.protect('Закриваємо доступ на редагування анонімам')


def list_pages_for_moderation(wiki):
    pages = list(page.title for page in yield_suspected_pages(wiki))
    print('\n'.join(pages))
    with open('check_list.txt', 'w') as f:
        f.write('\n'.join(pages))


def get_wiki():
    wiki = Wiki('http://cybportal.univ.kiev.ua/w/api.php', throttle=1)
    wiki.session_file('cybwiki.session')
    return wiki


def yield_suspected_pages(wiki):
    human_pages = set(p.title for p in wiki.category('Люди').members())

    for n, page in enumerate(wiki.all_pages):
        last_contributor = next(page.contributors())
        print(n, page.title, last_contributor.name)
        trusted = last_contributor.userpage().title in human_pages
        if not trusted:
           yield page
        else:
            print("trusted")


def kill_registered(wiki):
    bot_pages = set(p.title for p in wiki.category('Боти').members())
    human_pages = set(p.title for p in wiki.category('Люди').members())

    def shoot_bot(bot):
        bot.userpage().write('{{Spambot}}', 'Попався!')
        bot_pages.add(bot.userpage().title)
        for contrib in bot.contributions():
            spam_page = wiki.page(contrib['title'])
            only_bots = True
            for user in spam_page.contributors():
                if user.userpage().title not in bot_pages:
                    only_bots = False
                    break
            if only_bots:
                spam_page.delete('Спам.')
        bot.block('Die spammers, die!')

    for user in wiki.all_users:
        userpage = user.userpage()
        if userpage.title in bot_pages:
            continue
        if userpage.title in human_pages:
            continue

        show_user_info(user)
        if user.edit_count() < 3:
            verdict = True
            print('Припускаємо що бот')
        else:
            verdict = ask_y_n('Це бот, як думаєте? (y/n або порожній рядок якщо не знаєте)')

        if verdict == '':
            continue
        elif verdict:
            shoot_bot(user)
        else:
            userpage.append('{{Approved}}',
                'Підтвердження того що власник сторінки - не бот.'
            )


def delete_pages(wiki, list_filename):
    names = open(list_filename, 'r', encoding='utf-8')
    for name in names:
        print('deleting %s' % name)
        page = wiki.page(name[:-1])
        if page.exists():
            page.delete('spam')


def show_user_info(user):
    userpage = user.userpage()
    page_text = userpage.read()
    if page_text:
        print(page_text)
    else:
        print('Сторінка користувача порожня')
    edits = user.edit_count()
    print(userpage.title, 'Редагувань: %d' % edits)
