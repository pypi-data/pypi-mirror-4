#!/usr/bin/env python3
# -*- mode: python -*-
"""
This is "zovem" module, which is the part of "mailsanity"
package. The only function from this module
ever should be used is "reformat" -- given some email message,
it checks, whether is is a zovem.ru rss email, and if it is,
it fetch information from web and format it for
convient reading and in remind(1) format.
"""
import sys
import email
import textwrap
from email.header import decode_header
from urllib.request import urlopen
from itertools import takewhile, dropwhile
from datetime import datetime, date, time
from collections import namedtuple

from bs4 import *

def warn(obj: object):
    """Dump obj into stderr with noticable markers."""
    sys.stderr.write("\n\n----- Begin stderr dump -----\n\n")
    sys.stderr.write(str(obj))
    sys.stderr.write("\n\n----- End stderr dump -----\n\n")

month_index_map = { month: index + 1 for (index, month)
                    in enumerate([ 'января', 'февраля', 'марта', 'апреля',
                                   'мая', 'июня', 'июля', 'августа', 'сентября',
                                   'октября', 'ноября', 'декабря'])}
"""
Mapping from month name in russian to it's number. It deals with
specific of page markup.
"""

def parse_date(string: str) -> datetime:
    """
    Return datetime object, corresponding to
    string of natural russian, describing date and,
    optionally, time. In case of absence of time,
    set time to midnight.

    >>> parse_date('14 марта 2013, 19:00')
    datetime.datetime(2013, 3, 14, 19, 0)
    >>> parse_date('9 марта 2013, 08:45')
    datetime.datetime(2013, 3, 9, 8, 45)
    >>> parse_date('01 марта 2013')
    datetime.datetime(2013, 3, 1, 0, 0)
    >>> parse_date('02 марта 2013 - 03 марта 2013')
    datetime.datetime(2013, 3, 2, 0, 0)
    >>> parse_date('24 февраля 2013, с 13:00 до 20:00')
    datetime.datetime(2013, 2, 24, 13, 0)
    >>> parse_date('20 февраля 2013 - 10 марта 2013')
    datetime.datetime(2013, 2, 20, 0, 0)
    >>> parse_date('20 февраля 2013 - 10 марта 2013, Екатеринбург')
    datetime.datetime(2013, 2, 20, 0, 0)
    """
    string = string.rsplit(',', maxsplit = 1)[0]
    (day, month, year, *timestamp) = string.split()
    (day, month) = (int(day), month_index_map[month])
    year = int(year.strip(','))
    (hour, minute) = (0, 0)
    for substr in timestamp:
        if substr.find(':') != -1:
            (hour, minute) = map(int, substr.split(':'))
            break

    return datetime(year, month, day, hour, minute)

def header_string(msg, header) -> str:
    """ Return string representation of header"""
    return ''.join(map (lambda obj: obj[0].decode(obj[1]),
                        decode_header(msg[header])))

def rfc2822_format_datetime(dt: datetime):
    """
    Format datetime object into RFC2822 format
    >>> from datetime import datetime
    >>> rfc2822_format_datetime(datetime(2013, 3, 4, 2, 41))
    'Mon, 04 Mar 2013 02:41:00 +0400'
    """
    return email.utils.formatdate(float(dt.strftime("%s")), localtime = True)


header_meaning = {
        'Время начала' : 'time',
        'Условия участия' : 'requirements',
        'Куда идти' : 'place',
        'Адрес в сети': 'web',
        'Даты проведения': 'date',
        'Контакты': 'contacts',
        'Напишите, в чем ошибка': None,
        }
""" Mapping from article headers to their meaning."""
class ArticleInfo:
    """
    Named, modificable tuple to hold information,
    fetched from article
    """
    __slots__ =  ['article', 'city'] + list(filter(None, set(header_meaning.values())))
    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, '__invalid__')

def parse_article(article: open):
    """
    Parse file-like article to get map, containing generic information
    about event. Messy function. Subject to rewrite.
    """
    result_info = ArticleInfo()
    quater = BeautifulSoup(article)('index')[0]
    info = quater('p', 'small')
    result_info.city = info[0].span.get_text()
    for obj in info:
        (rus_key, value)  = obj.get_text().split(':', maxsplit = 1)
        try:
            setattr(result_info, header_meaning.get(rus_key), value)
        except: pass

    all_paragraphs = quater("p")
    result_info.article = ""
    for obj in takewhile (lambda x: x.get('class') == None,
                          dropwhile(lambda x: x.get('class') != None, all_paragraphs)):
        result_info.article += obj.get_text().translate(str.maketrans('','','\t\r'))+"\n"
    return result_info

MAIL_TEMPLATE = """
Where: {0.place}
How: {0.requirements}
Contacts: {0.contacts}

{0.article}

-----BEGIN REMIND ENTRY-----

{reminder}

-----END REMIND ENTRY-----
"""[1:-1]

def applicable(msg):
    """ Check whether msg is actually zovem.ru RSS email."""
    return str(msg['X-RSS-URL']).startswith('http://www.zovem.ru')

def format_reminder(what: str, where: str, when: str):
    """
    Format semi-decent reminder with note what, when and
    where should something happen.
    """
    with_time = (when.hour, when.minute) != (0, 0)
    (date_fmt, time_fmt) = (when.strftime('%d %B %Y'), when.strftime('%H:%M'))
    if with_time:
        header = "REM {0} AT {1} MSG \\\n".format(date_fmt, time_fmt)
    else:
        header = "REM {0} MSG \\\n".format(date_fmt)
    (what, where) = map(lambda x: textwrap.fill(x)+'\n', (what, where))
    (what, where) = map(lambda x: '%_\\\n'.join(x.split('\n')), (what, where))
    if with_time:
        footer = '[_default_date_time_format_()]'
    else:
        footer = '[_default_date_format_()]'
    return header + what + where + footer

def reformat(msg) -> bool:
    if applicable(msg):
        info = parse_article(urlopen(msg['X-RSS-URL']))
        info.article = '\n'.join(map(lambda x: textwrap.fill(x, width = 75), info.article.split('\n')))
        (subject, event_date) = (header_string(msg, 'Subject'), parse_date(info.date))
        reminder = format_reminder(subject, info.place, event_date)

        msg.set_payload(MAIL_TEMPLATE.format(info, reminder = reminder))
        msg.set_charset('utf-8')
        msg.replace_header('Date', rfc2822_format_datetime(event_date))
        for (attr, header) in {'city': 'X-Town', 'web': 'X-Web', 'who': 'X-Maintainer'}.items():
            try:
                msg[header] = getattr(info, attr).strip()
            except: pass
        return True
    return False


if __name__ == '__main__':
    import doctest
    doctest.testmod()
