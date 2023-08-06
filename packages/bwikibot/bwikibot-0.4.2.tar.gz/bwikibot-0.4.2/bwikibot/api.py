#coding=utf-8

from copy import copy
from datetime import datetime
import getpass
import json
import mimetypes
import pickle
from pprint import pprint
import sys
import time
try: # python3
    from urllib.parse import urlencode
except ImportError: # python2
    from urllib import urlencode

import httplib2

DEBUG = False
SERVER_ENCODING = 'utf-8'
LIST_LIMIT = 400

httplib2.debuglevel = 4 if DEBUG else 0

class WikiError(Exception):
    def __init__(self, code, msg):
        super(WikiError, self).__init__('WikiError: %s' % msg)
        self.code = code

class ChainedRedirectError(Exception):
    def __init__(self, page):
        super(ChainedRedirectError, self).__init__(
            'Too much redirects on page %s' % page.title
        )


def utf8(x):
    if not x:
        return b''
    if isinstance(x, bytes):
        return x
    return x.encode('utf-8')


def datetime2zulu(t):
    return t.isoformat().split('.')[0] + 'Z'

def zulu2datetime(z):
    return datetime.strptime(z, '%Y-%m-%dT%H:%M:%SZ')

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    def app(l):
        L.append(utf8(l))

    for (key, value) in fields:
        app('--' + BOUNDARY)
        app('Content-Disposition: form-data; name="%s"' % key)
        app('')
        app(value)
    for (key, filename, value) in files:
        app('--' + BOUNDARY)
        app('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        app('Content-Type: %s' % get_content_type(filename))
        app('')
        app(value)
    app('--' + BOUNDARY + '--')
    app('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

class Wiki():
    ''' Class for performing general requests to the API
    and storing session info.
    '''
    cookies = None
    namespaces_names = None # map from id to localised name
    namespaces_ids = None # map from canonical name to id

    def __init__(self, endpoint=None, throttle=1,
        disable_ssl_certificate_validation=True
    ):
        ''' Create wiki client for given endpoint addres.  '''
        self._tokens = {}
        self.endpoint = endpoint
        self.throttle = throttle


        self.http = httplib2.Http('.cache')
        self.http.disable_ssl_certificate_validation = disable_ssl_certificate_validation



        if endpoint:
            self.get_namespaces()
        # else may be load session

    def get_unified_login_to(self, domain):
        ''' Returns new wiki instance with changed domain and namespace '''
        res = copy(self)
        url = self.endpoint.split('/') # http://domain/...
        url[2] = domain
        res.endpoint = '/'.join(url)
        res.get_namespaces()
        return res

    def load(self, filename):
        ''' Load cookies, endpoint, namespaces. '''
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.cookies = data['cookies']
                self.endpoint = data['endpoint']
                self.namespaces_names = data.get('namespaces_names')
                self.namespaces_ids = data.get('namespaces_ids')
                self.throttle = data.get('throttle', 1)
                self.init_namespaces()
        except IOError:
            return False
        return True

    def save(self, filename):
        ''' Save cookies, endpoint, namespaces '''
        with open(filename, 'wb') as f:
            data = dict(
                cookies=self.cookies,
                endpoint=self.endpoint,
                namespaces_names=self.namespaces_names,
                namespaces_ids=self.namespaces_ids,
                throttle=self.throttle,
            )
            pickle.dump(data, f)

    def request(self, params=None, method='GET', headers=None):
        ''' Perform any type of request to API.

        All query params should be passed throught params. 
        Authorisation cookies is passed throught headers
        authomathically if client is logged in.

        Returns headers and parsed json of resonce.
        '''
        assert self.endpoint, "Can't make a request without endpoint"
        if params is None:
            params = {}

        p2 = {}
        for k,v in params.items():
            if v is True:
                p2[k] = 1
            elif v is False:
                pass
            else:
                p2[k] = v
        params = p2

        params['format'] = 'json'
        if headers is None:
            headers = {}
        headers['user-agent'] = 'bwikibot'
        if self.cookies:
            headers['cookie'] = '; '.join(
                '%s=%s' % (n, v) for n,v in self.cookies.items()
            )
        body = urlencode(params)
        if method == 'GET':
            query = self.endpoint + '?' + body
            body = None
        else:
            query = self.endpoint
            if not headers.get('Content-type'):
                headers['Content-type'] = 'application/x-www-form-urlencoded'
            if params['action'] == 'upload':
                data = params.pop('file')
                content_type, body = encode_multipart_formdata(
                    params.items(), 
                    [('file', params['filename'], data)]
                )
                headers['Content-type'] = content_type
        time.sleep(self.throttle)
        responce, content = self.http.request(
            query,
            method,
            headers=headers,
            body=body,
        )
        if DEBUG:
            print('\n')
        content = json.loads(content.decode(SERVER_ENCODING))
        if not content:
            raise WikiError('empty responce', 'MediaWiki empty responce: %s' % content)
        if not isinstance(content, dict):
            return content
        error = content.get('error')
        if error:
            print('Request params:')
            pprint(params)
            raise WikiError(error['code'], 'MediaWiki responce error: "%s"' % error['info'])

        return responce, content

    def query(self, params):
        '''Get query to the API.
        '''
        params['action'] = 'query'
        responce, content = self.request(params)
        return content['query']

    def query_cont(self, params):
        ''' Get query to the API for lists.

        Returns pair of responce and continue query params.
        '''
        params['action'] = 'query'
        responce, content = self.request(params)
        return content['query'], content.get('query-continue')

    def opensearch(self, search, limit=20):
        ''' Return a sequence of page titles which starts from given prefix '''
        responce, content = self.request(dict(
            action='opensearch',
            search=search,
            limit=limit,
        ))
        return content

    def _get_login_cookie(self, login, password):
        ''' Returns dictionary with cookies for given account.  '''
        responce, content = self.request(
            dict(
                action='login',
                lgname=login,
                lgpassword=password,
            ),
            method='POST'
        )
        content = content['login']
        if content['result'] == 'NeedToken':
            headers = {
                'Cookie': responce['set-cookie']
            }
            responce, content = self.request(
                dict(
                    action='login',
                    lgname=login,
                    lgpassword=password,
                    lgtoken=content['token']
                ),
                method='POST',
                headers=headers
            )
            content = content['login']
        if content['result'] == 'Success':
            pref = content['cookieprefix']
            cookies = {
                pref + '_session': content['sessionid'],
                pref + 'Token': content['lgtoken'],
                pref + 'UserName': content['lgusername'],
                pref + 'UserID': content['lguserid'],
                'path': '/',
            }
            return cookies
        else:
            raise WikiError(content['result'], 'Login error: %s.' % content['result'])

    def session_login(self, endpoint=None, login=None, password=None):
        ''' Start session for given account. '''
        if self.endpoint:
            self.endpoint = endpoint
        else:
            if not endpoint:
                endpoint = input('Endpoint: ')
            self.endpoint = endpoint

        if not login:
            login = input('Login: ')
        if not password:
            password = getpass.getpass('Password for %s: ' % login)
        try:
            self.cookies = self._get_login_cookie(login, password)
            self.get_namespaces()
        except WikiError as e:
            if e.code == 'WrongPass':
                print('Wrong password')
                sys.exit(0)
            else:
                raise

    def session_file(self, filename):
        ''' Start session which is persistent in file. '''
        if not self.load(filename):
            self.session_login()
            self.save(filename)
        
    def get_token(self, intoken, **params):
        ''' Get token for edit operation. '''
        token = self._tokens.get(intoken)
        if not token:
            params['intoken'] = intoken
            params['prop'] = 'info'
            res = self.query(params)
            try:
                token = list(res['pages'].values())[0]['%stoken' % intoken]
            except KeyError:
                pprint(res)
            self._tokens[intoken] = token
        return token

    def get_users(self,
        from_name=None, to_name=None,
        prefix=None, prop=None,
        with_edits_only=False,
        active_only=False,
    ):
        ''' Returns generator of users of current wiki.

        Every user is of type User.
        '''
        q = {
            'list': 'allusers',
            'aulimit': LIST_LIMIT,
        }
        if from_name:
            q['aufrom'] = from_name
        if to_name:
            q['auto'] = to_name
        if prefix:
            q['auprefix'] = prefix
        if prop:
            q['auprop'] = prop
        if active_only:
            q['auactiveusers'] = 1
        if with_edits_only:
            q['auwitheditsonly'] = 1
        res, cont = self.query_cont(q)
        for user in res['allusers']:
            yield User(self, user['name'])

        while cont:
            q.update(cont['allusers'])
            res, cont = self.query_cont(q)
            for user in res['allusers']:
                yield User(self, user['name'])

    @property
    def all_users(self):
        ''' Generator of all users of current wiki
        '''
        return self.get_users()

    @property
    def all_pages(self):
        for namespace in self.namespaces_ids.values():
            if namespace < 0:
                continue
            for page in self.get_pages(namespace=namespace):
                yield page

    def get_pages(self,
        from_name=None, to_name=None,
        prefix=None, prop=None,
        namespace=None
    ):
        q = {
            'list': 'allpages',
            'aplimit': LIST_LIMIT,
        }
        if from_name:
            q['apfrom'] = from_name
        if to_name:
            q['apto'] = to_name
        if prefix:
            q['apprefix'] = prefix
        if namespace:
            q['apnamespace'] = namespace

        res, cont = self.query_cont(q)
        for page in res['allpages']:
            yield Page(self, page['title'])

        while cont:
            q.update(cont['allpages'])
            res, cont = self.query_cont(q)
            for page in res['allpages']:
                yield Page(self, page['title'])

    def logevents(self, start=None, end=None,
        event_type=None,
        direction='older', # or newer
    ):
        q = {
            'list': 'logevents',
            'lelimit': LIST_LIMIT,
            'ledir': direction,
        }
        if start and end and start < end:
            start, end = end, start # newer changes first, remember?
        if start:
            q['lestart'] = datetime2zulu(start)
        if end:
            q['leend'] = datetime2zulu(end)
        if event_type:
            q['letype'] = event_type

        q['leprop'] = 'user|comment|timestamp|title'
        res, cont = self.query_cont(q)
        for event in res['logevents']:
            yield Change(self, event)

        while cont:
            q.update(cont['logevents'])
            res, cont = self.query_cont(q)
            for event in res['logevents']:
                yield Change(self, event)
        

    def recent_changes(self, start=None, end=None,
        change_type=None, # edit, new, log
        namespace=None,
    ):
        q = {
            'list': 'recentchanges',
            'rclimit': LIST_LIMIT,
            'rcdir': 'older', # newer changes first
        }
        if start and end and start < end:
            start, end = end, start # newer changes first, remember?
        if start:
            q['rcstart'] = datetime2zulu(start)
        if end:
            q['rcend'] = datetime2zulu(end)
        if namespace:
            q['rcnamespace'] = namespace
        if change_type:
            q['rctype'] = change_type
        q['rcprop'] = 'user|comment|timestamp|title|flags'
        res, cont = self.query_cont(q)
        for change in res['recentchanges']:
            yield Change(self, change)

        while cont:
            q.update(cont['recentchanges'])
            res, cont = self.query_cont(q)
            for change in res['recentchanges']:
                yield Change(self, change)

    def page(self, title):
        return Page(self, title)

    def category(self, title):
        return Category(self, title)

    def file(self, title):
        return File(self, title)

    def user(self, name):
        return User(self, name)

    def get_namespaces(self):
        ''' Init two maps for namespaces:
        namespaces_names: from id to localised name 
        namespaces_ids: from canonical name to id
        '''
        res = self.query(dict(
            meta='siteinfo',
            siprop='namespaces',
        ))
        self.namespaces_names = {}
        self.namespaces_ids = {}
        for ns in res['namespaces'].values():
            self.namespaces_names[ns['id']] = ns['*']
            self.namespaces_ids[ns.get('canonical')] = ns['id']

        self.init_namespaces()

    def init_namespaces(self):
        ''' Set some constants '''
        def ns_name(canonical):
            return self.namespaces_names[self.namespaces_ids[canonical]]

        self.USER_NS_NAME = ns_name('User')
        self.USER_TALK_NS_NAME = ns_name('User talk')
        self.CATEGORY_NS_NAME = ns_name('Category')
        self.FILE_NS_NAME = ns_name('File')

    def logged_user_info(self):
        ''' Get info about currently logged user.
        '''
        return self.query(
            dict(
                meta='userinfo',
                uiprop='groups|rights|editcount|email',
            ),
        )['userinfo']

    def __str__(self):
        return 'Wiki("%s")' % self.endpoint


class Change:
    def __init__(self, wiki, data):
        self.wiki = wiki
        self.type = data.get('type')
        self.time = zulu2datetime(data['timestamp'])
        self.page = Page(wiki, data['title'])
        self.user = User(wiki, data['user'])

    def __str__(self):
        return '{}.change({})'.format(self.page, self.time)

class Page:
    def __init__(self, wiki, title):
        self.wiki = wiki
        self.title = title
        self.pageid = None
        self.missing = None
        self.text = None

    def read(self):
        ''' Returns page text, and remembers page meta info, 
        such as namespace, normalized title, is page missing,
        and page id.
        '''
        if self.text:
            return self.text
        res = self.wiki.query(dict(
            prop='revisions',
            rvprop='content',
            titles=self.title,
        ))
        page = list(res['pages'].values())[0]
        self.namespace = page['ns']
        self.title = page['title']
        if 'missing' in page:
            self.missing = True
            return None
        else:
            self.missing = False
            self.pageid = page['pageid']
        self.text = page['revisions'][0]['*']
        return self.text

    def exists(self):
        self.read()
        return not self.missing

    def is_category(self):
        if not getattr(self, 'namespace', False):
            self.read()
        return self.namespace == self.wiki.namespaces_ids['Category']

    def write(self, text, summary, bot=True, minor=False):
        ''' Replace page contents with given text. 
        summary param is the description of edit.
        '''
        responce, content = self.wiki.request(
            dict(
                action='edit',
                title=self.title,
                text=text,
                token=self.wiki.get_token('edit', titles=self.title),
                summary=summary,
                bot=bot,
                minor=minor,
            ),
            method='POST',
        )
        self.text = text
        return content

    def append(self, message, summary): 
        body = self.read()
        if not body:
            body = ''
        return self.write(body + message, summary)

    def delete(self, reason):
        if not self.exists():
            return
        responce, content = self.wiki.request(
            dict(
                action='delete',
                title=self.title,
                token=self.wiki.get_token('delete', titles=self.title),
                reason=reason,
            ),
            method='POST',
        )

    def revisions(self):
        q = {
            'prop': 'revisions',
            'rvlimit': LIST_LIMIT / 10,
            'rvprop': 'user|timestamp|comment|content',
            'titles': self.title,
        }
        res, cont = self.wiki.query_cont(q)
        res = res['pages'].popitem()[1]
        if 'revisions' not in res:
            pprint(res)
            return
        for contrib in res['revisions']:
            yield contrib
        while cont:
            q.update(cont['revisions'])
            res, cont = self.wiki.query_cont(q)
            for contrib in res['revisions']:
                yield contrib


    def contributors(self):
        q = {
            'prop': 'revisions',
            'rvlimit': LIST_LIMIT,
            'rvprop': 'user',
            'titles': self.title,
        }
        res, cont = self.wiki.query_cont(q)
        res = res['pages'].popitem()[1]
        if 'revisions' not in res:
            pprint(res)
            return
        for contrib in res['revisions']:
            if 'user' in contrib:
                yield User(self.wiki, contrib['user'])
        while cont:
            q.update(cont['revisions'])
            res, cont = self.wiki.query_cont(q)
            for contrib in res['revisions']:
                if 'user' in contrib:
                    yield User(self.wiki, contrib['user'])

    def interwikis(self):
        ''' Returns dictionary of page names in other languages
        '''
        resp = self.wiki.query({
            'prop': 'langlinks',
            'titles': self.title,
            'lllimit': LIST_LIMIT,
        })
        pages = resp.get('pages')
        if not pages:
            return {}
        links = pages.popitem()[1].get('langlinks')
        if not links:
            return {}
        res = {}
        for link in links:
            res[link['lang']] = link['*']
        return res

    def categories(self):
        ''' Return list of categories for page '''
        q = {
            'prop': 'categories',
            'cllimit': LIST_LIMIT,
            'titles': self.title,
        }
        res, cont = self.wiki.query_cont(q)
        res = res['pages'].popitem()[1]
        if 'categories' not in res:
            return
        for cat in res['categories']:
            if 'title' in cat:
                yield self.wiki.category(cat['title'])
        while cont:
            q.update(cont['categories'])
            res, cont = self.wiki.query_cont(q)
            for cat in res['categories']:
                if 'title' in cat:
                    yield self.wiki.category(cat['title'])

    def redirect(self):
        ''' Return None or page to which it redirects
        '''
        self.read() # Normalise title, otherwise sometimes don't work
        redirects = self.wiki.query({
            'titles': self.title,
            'redirects': None,
        }).get('redirects', [])
        for r in redirects:
            if r['from'] == self.title:
                return self.wiki.page(r['to'])

    def resolve_redirect(self):
        ''' Return page or page to which this redirects if it is redirect '''
        res = self
        i = 0
        while res.redirect():
            res = res.redirect()
            i += 1
            if i > 3:
                raise ChainedRedirectError(self)
        return res


    def protect(self, reason):
        req = dict(
            action='protect',
            title=self.title,
            token=self.wiki.get_token('protect', titles=self.title),
            reason=reason,
            protections='edit=autoconfirmed|move=autoconfirmed'
        )
        responce, content = self.wiki.request(req, method='POST')
        return content

    def __str__(self):
        return '%s.page("%s")' % (self.wiki, self.title)


class Category(Page):
    def __init__(self, wiki, title):
        if not title.startswith(wiki.CATEGORY_NS_NAME + ':'):
            title = wiki.CATEGORY_NS_NAME + ':' + title
        super(Category, self).__init__(wiki, title)

    def members(self, namespace=None):
        q = {
            'list': 'categorymembers',
            'cmlimit': LIST_LIMIT,
            'cmtitle': self.title,
        }
        if namespace is not None:
            q['cmnamespace'] = namespace
        res, cont = self.wiki.query_cont(q)
        for member in res['categorymembers']:
            yield self.wiki.page(member['title'])

        while cont:
            q.update(cont['categorymembers'])
            res, cont = self.wiki.query_cont(q)
            for member in res['categorymembers']:
                yield self.wiki.page(member['title'])

class File(Page):
    def __init__(self, wiki, title):
        if not title.startswith(wiki.FILE_NS_NAME + ':'):
            title = wiki.FILE_NS_NAME + ':' + title
        super(File, self).__init__(wiki, title)

    @property
    def filename(self):
        return self.title[len(self.wiki.FILE_NS_NAME) + 1:]

    def upload(self, path_to_file, comment, page_text):
        data = open(path_to_file, 'rb').read()
        responce, content = self.wiki.request(
            dict(
                action='upload',
                filename=self.filename,
                file=data,
                text=page_text,
                comment=comment,
                ignorewarnings=None,
                token=self.wiki.get_token('edit', titles='Головна сторінка'),
            ),
            method='POST',
        )
        res = content['upload']['result']
        if res == 'Warning':
            print(content['upload']['warnings'])
            return False
        if res == 'Success':
            return True

    def _url(self, width=None):
        query = dict(
            titles=self.title,
            prop='imageinfo',
            iiprop='url',
        )
        if width:
            query['iiurlwidth'] = width
        resp = self.wiki.query(query)
        try:
            info = list(resp['pages'].values())[0]['imageinfo'][0]
        except KeyError:
            print(resp)
        return info['thumburl' if width else 'url']

    def download(self, to_file, width=None):
        headers, content = self.wiki.http.request(self._url(width))
        with open(to_file, 'wb') as f:
            f.write(content)

class User():
    def __init__(self, wiki, name):
        self.wiki = wiki
        self.name = name

    def __str__(self):
        return '%s.user("%s")' % (self.wiki, self.name)

    def userpage(self):
        return Page(self.wiki, '%s:%s' % (
            self.wiki.USER_NS_NAME,
            self.name
        ))

    def talkpage(self):
        return Page(self.wiki, '%s:%s' % (
            self.wiki.USER_TALK_NS_NAME,
            self.name
        ))

    def contributions(self):
        q = {
            'list': 'usercontribs',
            'uclimit': LIST_LIMIT,
            'ucuser': self.name,
        }
        res, cont = self.wiki.query_cont(q)
        for contrib in res['usercontribs']:
            yield contrib

        while cont:
            q.update(cont['usercontribs'])
            res, cont = self.wiki.query_cont(q)
            for contrib in res['usercontribs']:
                yield contrib

    def edit_count(self):
        return int(self.wiki.query({
            'list': 'users',
            'ususers': self.name,
            'usprop': 'editcount',
        })['users'][0]['editcount'])

    def is_anonymous(self):
        return not bool(self.wiki.query({
            'list': 'users',
            'ususers': self.name,
            'usprop': 'registration',
        })['users'][0].get('registration', False))

    def block(self, reason, nocreate=True, autoblock=True):
        req = dict(
            action='block',
            user=self.name,
            token=self.wiki.get_token('block', titles=self.name),
            reason=reason,
        )
        if nocreate:
            req['nocreate'] = ''
        if autoblock:
            req['autoblock'] = ''
        try:
            responce, content = self.wiki.request(req, method='POST')
            return content
        except WikiError as e:
            if e.code == 'alreadyblocked':
                pass
            else:
                raise

    def unblock(self, reason):
        self.wiki.request(
            dict(
                action='unblock',
                user=self.name,
                token=self.wiki.get_token('unblock', titles=self.name),
                reason=reason,
            ),
            method='POST',
        )

    def __str__(self):
        return '%s.user("%s")' % (self.wiki, self.name)

from difflib import ndiff

def copy_file(from_wiki, to_wiki, file_name):
    import uuid
    import os
    temp_fn = str(uuid.uuid1())
    source = from_wiki.file(file_name)
    source.download(temp_fn)
    to_wiki.file(file_name).upload(temp_fn,
        'test file exporting', source.read()
    )
    os.remove(temp_fn)

if __name__ == '__main__':
    cybwiki = Wiki('http://cybportal.univ.kiev.ua/w/api.php')
    for i, change in enumerate(cybwiki.recent_changes()):
        if i > 10:
            break
        print(change)
