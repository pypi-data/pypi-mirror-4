""" Mediawiki markup lexer """

import re

TEXT, COMMENT, LINK, MARKUP, VERBATIM, HEADER, INTERWIKI = range(7)

def text(scaner, token):
    return (TEXT, token)

def link(scaner, token):
    a = re.match(r"\[\[([^\|\]]+)(\|[^\]\|]+)?\]\]",token)
    assert a != None , 'scanner get a bad link: ' + token
    page = text = ""
    if len(a.groups()) == 1:
        page = text = a.groups()[0]
    if len(a.groups()) == 2:
        page, text = a.groups()
        if text == None:
            text = page
        else:
            text = text[1:]
    return (LINK, page, text)
    
def comment(scaner, token):
    return (COMMENT, token)

def markup(scaner, token):
    return (MARKUP, token)

def verbatim(scaner, token):
    return (VERBATIM, token)

def header(scaner, token):
    a = re.match(r"\n(=+)(.*)(\1)\n",token)
    level = len(a.groups()[0])
    return (HEADER,a.groups()[1],level)

def interwiki(scaner,token):
    a = re.match(r"\[\[([^:]*):([^\]]*)\]\]",token)
    return (INTERWIKI,a.groups()[0],a.groups()[1])

def token_text(token): # translate token tuple back to text
    if token[0] == LINK:
        res = '[[' + token[1]
        if token[1] != token[2]:
            res += '|' + token[2]
        res += ']]'
        return res
    elif token[0] == HEADER:
        return '\n' + "=" * token[2] + token[1] + "=" * token[2] + '\n'
    elif token[0] == INTERWIKI:
        return '[[' + token[1] + ':' + token[2] + ']]'                
    else:
        return token[1]

iwiki_regex = r"\[\[(en|de|fr|zh|nl|pl|it|ja|es|pt|ru|sv|lt|no|fi|ca|uk|hu|cs|tr|ro|vo|eo|da|ko|id|sk|ar|vi|sr|he|bg|fa|sl|lmo|et|hr|new|te|nn|th|gl|el|ceb|simple|ms|eu|ht|bs|bpy|lb|ka|is|sq|la|br|hi|az|bn|mk|mr|sh|tl|cy|io|pms|lv|ta|su|oc|jv|nap|nds|scn|be|ast|ku|wa|af|be-x-old|an|ksh|szl|fy|frr|zh-yue|ur|ia|ga|yi|sw|als|hy|am|roa-rup|map-bms|bh|co|cv|dv|nds-nl|fo|fur|glk|gu|ilo|kn|pam|csb|kk|km|lij|li|ml|gv|mi|mt|nah|ne|nrm|se|nov|qu|os|pi|pag|ps|pdc|rm|bat-smg|sa|gd|sco|sc|si|tg|roa-tara|tt|to|tk|hsb|uz|vec|fiu-vro|wuu|war|vls|yo|diq|zh-min-nan|zh-classical|frp|lad|bar|bcl|kw|mn|haw|ang|ln|ie|wo|tpi|ty|crh|jbo|ay|zea|eml|ky|ig|or|mg|cbk-zam|kg|arc|rmy|gn|mo|so|kab|ks|stq|ce|udm|mzn|pap|cu|sah|tet|sd|lo|ba|pnb|iu|na|got|bo|dsb|chr|cdo|hak|om|my|sm|ee|pcd|ug|as|ti|av|bm|zu|pnt|nv|cr|pih|ss|ve|bi|rw|ch|arz|xh|kl|ik|bug|dz|ts|tn|kv|tum|xal|st|tw|bxr|ak|ab|ny|fj|lbe|ki|za|ff|lg|sn|ha|sg|ii|cho|rn|mh|chy|ng|kj|ho|mus|kr|hz|mwl|pa):([^\]]*)\]\]"
redirect_regex = r"#\w+ \[\[([^\]]+)\]\]"

def redirect_to(text):
    ''' Where redirect redirects '''
    a = re.findall(redirect_regex,text)
    if a:
        return a[0]
    else:
        return None

lexer = re.Scanner([
    (r"<!--(.|\n)*?-->", comment),
    (r"<(source|syntaxhighlight|math|nowiki).*?>(.|\n)*?</(\1)>", verbatim),
    (iwiki_regex,interwiki), #interwikis
    (r"\[\[(File|Image):[^|\]]+\.(jpg|png|svg|gif)\|([a-z0-9]+\|)*",markup), #images, files
    (r"\[\[[^\|\]]+(\|[^\]\|]+){2,}\]\]",markup),#files in other languages
    (r"\[\[[^\|\]]+(\|[^\]\|]+)?\]\]",link), # internal links
    (r"\[[^\]]+\]",markup), # external links
    (r"(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?",markup), #external link too
    (r"\n(=+)([^\n]*)(\1)\n",header),
    (r"\|\}\}",markup),
    (r"\{\|",markup),
    (r"\|\}",markup),
    (r"\{\{",markup),
    (r"\}\}",markup),
    (r"\{",markup), # !!!
    (r"\}",markup), # !!!
    (r"\]\]",markup),
    ("<[\"\s<]",text),
    (r"<[a-zA-Z/][^>]*>", markup),
    (r"'''",markup), 
    (r"''",markup), 
    (r"\n[*#]+:*",markup),
    (r"\n:+",markup),
    (r"\n\|-",markup),
    (r"\|",markup),
    (r"\n!",markup),
    (r"==+",markup),
    (r"=",markup),
    (r":",markup),
    (r"\s",text),
    (r"\[\]",text),#i quite surprised but it really is text
    (r"((?!''+)[^\|\{\}\[\]:=<\n])*",text),
    (r"<\s",text),
    (r"[^<]*",text)
    ])

class ParseError(Exception):
    pass

def tokenize(text):
    res = lexer.scan(text)
    if res[1]:
        raise ParseError('Markup is not fully parsed')
    return res[0]


def clean_markup(markup):
    lex,rest = parser(markup)
    res = [" "]
    for i in lex:
        if i[0]==LINK:
            res.append(i[2])
        elif i[0]==VERBATIM:
            res.append(i[1])
        elif i[0]==HEADER:
            res.append(i[1])
        elif i[0]==TEXT:
            res.append(i[1])
        else:
            if res[-1]!=" ":
                res.append(" ")
    return "".join(res)
