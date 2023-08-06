#!/usr/bin/python3

""" 
Get a link to wiki page (as parameter, or interactively)
and returns a markup optimized for wordpress:
1. Replaced wiki latex generated images to native wordpress $latex $ tags.
2. Removes [.edit] links.
3. Points links to right domain (from which was get page).
4. Removes red links.
5. Replaces geshi highlighting to [sourcecode lang=""] tags.

Depends on bs4 unit.
"""
__author__ = "Bunyk T."

import re
import sys
import httplib2
import bs4

http = httplib2.Http()

def get(url):
    return http.request(url)[1].decode('utf-8')

def get_source(domain, name):
    text = get(domain + '/w/index.php?title=' + name + '&action=raw')
    sources = re.findall('<source lang="(.*?)">(.*?)</source>', text, re.DOTALL)
    return sources

def wiki_filter(ln, domain):
    ln = re.sub( # replace latex
        r'<img (?:(?:class="tex"|alt="(.*?)"|src=".*?") ?){3}/>',
        r'$latex \1$',
    ln)
    ln = re.sub( # remove [.edit] links
        r'<span class="editsection">.*?</span>',
        "",
    ln)
    ln = re.sub( # remove comments
        r'<!--.*?-->',
        r"",
    ln)
    ln = re.sub( # point links to right domain
        r'<a href="/wiki/(.*?)"',
        r'<a href="' + domain + r'wiki/\1"',
    ln)
    return ln

START_MARK = "<!-- bodycontent -->"
FINISH_MARK = "<!-- /bodycontent -->"
GESHI_MARK = "GESHI-HIGHLIGHT"

if len(sys.argv) < 2:
    url = input("Page url: ")
else:
    url = sys.argv[1]

try:
    domain = re.findall("(http://.*?/)wiki/", url)[0]
    page_name = re.findall("http://.*?/wiki/(.*)$", url)[0]
except IndexError:
    domain = re.findall("(http://.*?/)w/index.php", url)[0]
    page_name = re.findall("http://.*?/w/index.php.*title=(.*?)&.*", url)[0]

doc = get(url)

has_source = False

soup = bs4.BeautifulSoup(doc)
geshis = soup.findAll("div", {"class": "mw-geshi"})
for i in geshis: # replace geshi highlight to temporal mark
    i.replaceWith(GESHI_MARK)
    has_source = True

red_links = soup.findAll("a", {"class":"new"}) # Remove red links
for i in red_links:
    i.replaceWith(bs4.BeautifulSoup(i.renderContents()))

if has_source:
    sources_list = get_source(domain, page_name) # get sources used on page
current_source = 0

doc = str(soup).splitlines()

inbody = False
for line in doc:
    if re.search(FINISH_MARK, line):
        break
    if re.search(GESHI_MARK, line):
        print(''.join([
            "[sourcecode language='",
            sources_list[current_source][0],
            "']",
            sources_list[current_source][1],
            "[/sourcecode]",
        ]))
        current_source += 1
        continue
    if inbody:
        print(wiki_filter(line, domain))
        continue
    if re.search(START_MARK, line):
        inbody = True
