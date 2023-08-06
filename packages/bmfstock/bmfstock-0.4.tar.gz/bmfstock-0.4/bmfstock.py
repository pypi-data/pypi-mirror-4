# -*- coding: UTF-8 -*-

"""
Module to retrive and to manage papers from BMFBovespa
"""

__all__ = [
    'atual_serie',
    'get_file_options',
    'get_options',
    'Paper',
    'PaperItem',
    'paper_calc',
    'PaperException',
    'update_last_values',
]

__version__ = '0.4'

from datetime import date, timedelta
import glob
import os
import re
from tempfile import gettempdir
from urllib2 import urlopen, URLError
from xml.dom.minidom import parse

from cdecimal import Decimal
import mechanize
import numpy as np


SERVER = 'http://investire.christoferbertonha.eng.br'
BMFSERVER = 'http://www.bmfbovespa.com.br'

PAPERS = {}


def atual_serie():
    deadlines = [16, 13, 19, 16, 21, 13, 16, 15, 17, 15, 19, 12]
    today = date.today()

    month = today.month
    deadline = deadlines[month - 1]
    if today.day > deadline:
        month += 1
        if month > 12:
            month = 1
    return month


class ValueProperty(object):
    def __init__(self, default=None):
        self.default = default

    def __get__(self, instance, owner):
        if not hasattr(self, 'name_attr'):
            return self.default
        return getattr(instance, self.name_attr)

    def __set__(self, instance, value):
        if not hasattr(self, 'name_attr'):
            for name, attr in instance.__class__.__dict__.items():
                if attr is self:
                    self.name_attr = '__' + name
                    break
            else:
                assert False, 'descriptor not found in class'

        if value is None or value == 0 or value == 'None':
            value = self.default
        else:
            value = Decimal(value)
        setattr(instance, self.name_attr, value)


def _get_previous_active_day():
    try:
        lastfile = sorted(glob.glob('%s/ROPC*.dat' % gettempdir()))[-1]
    except IndexError:
        # No existing files
        return None
    less_day = timedelta(days=1)
    today = date.today()
    previous = today - less_day
    year, month, day = lastfile[-12:-8], lastfile[-8:-6], lastfile[-6:-4]
    last_day = date(int(year), int(month), int(day))
    while previous.weekday() in (5, 6):
        # if previous is in weekend go to friday
        previous -= less_day
    if last_day in (today, previous):
        return lastfile
    return None

_last_filename = _get_previous_active_day()


def process_float_string(string):
    if ',' in string:
        string = string.replace(',', '.')
    elif '.' not in string:
        string = string[:-2] + '.' + string[-2:]
    return Decimal(string)


def save_option(data, path=None):
    global _last_filename

    if path is None:
        path = gettempdir()

    filename = os.path.basename(data.geturl())
    if not filename.endswith('.dat'):
        filename = 'ROPC{}.dat'.format(data.readline()[22:30])
    _last_filename = os.path.join(path, filename)
    with open(_last_filename, 'w') as f:
        f.write(data.read())
        f.flush()


def get_file_options():
    if not _last_filename:
        try:
            response = urlopen('{}/get_option'.format(SERVER))
        except URLError:
            response = get_file_options_bmf()
        save_option(response)
    return _last_filename


def get_file_options_bmf():
    br = mechanize.Browser()
    br.open('{}/opcoes/opcoes.aspx?Idioma=pt-br'.format(BMFSERVER))
    br.select_form(nr=0)
    response = br.submit(name='ctl00$contentPlaceHolderConteudo$'
                              'posicoesAbertoEmp$btnBuscarArquivos')
    return response


def get_options(symbol):
    symbol = re.search(r'[A-Z]*', symbol.upper()).group(0)
    options = []
    with open(get_file_options()) as data:
        for line in data:
            if line[2:6] == symbol:
                option = Paper(line[42:49].strip(), update=False)
                option.market = 'A' if line[152:153] == '1' else 'E'
                option.strike = process_float_string(line[62:75])
                year, month, day = line[24:28], line[28:30], line[30:32]
                option.deadline = date(int(year), int(month), int(day))
                options.append(option)
    options.sort()
    return options


def update_last_values(papers):
    url = '{}/Pregao-Online/ExecutaAcaoAjax.asp?CodigoPapel={}'
    codes = '|'.join([paper.code for paper in papers])
    doc = parse(urlopen(url.format(BMFSERVER, codes)))

    for paper, data in zip(papers, doc.getElementsByTagName('Papel')):
        last = process_float_string(data.getAttribute('Ultimo'))
        changed = False
        if last != paper.last:
            if paper.last != 0:
                paper.evolution = 1 if last > paper.last else -1
            paper.last = last
            changed = True
        else:
            paper.evolution = 0
        paper.changed = changed


def Paper(code, *args, **kwargs):
    try:
        paper = PAPERS[code]
    except KeyError:
        paper = _Paper(code, *args, **kwargs)
        PAPERS[code] = paper
    return paper


class _Paper(object):
    evolution = 0
    market = 'A'
    last = ValueProperty(0)
    changed = False

    # Options
    strike = ValueProperty(None)
    deadline = None

    def __init__(self, code, update=False):
        self._code = code.upper()
        self.last = 0
        self.strike = None

        if self.code.endswith('F'):
            self.step = 1
        else:
            self.step = 100
        if update:
            self.get_stock()

    def __cmp__(self, other):
        def split(string):
            return (string[:5], int(string[5:]))

        if isinstance(other, basestring):
            other_code = other.upper()
        else:
            other_code = other.code
        return cmp(split(self.code), split(other_code))

    def __str__(self):
        return self.code

    @property
    def code(self):
        return self._code

    def get_stock(self):
        url = '{}/cotacoes2000/formCotacoesMobile.asp?codsocemi={}'
        doc = parse(urlopen(url.format(BMFSERVER, self.code)))

        try:
            paper = doc.getElementsByTagName('PAPEL')[0]
        except IndexError:
            raise PaperException(u'Código "%s" inexistente.' % self.code)

        self.last = process_float_string(paper.getAttribute('VALOR_ULTIMO'))
        description = paper.getAttribute('DESCRICAO')
        if paper.getAttribute('MERCADO') == u'Opções':
            self.strike = process_float_string(description.split()[-1])


class PaperItem(object):
    enabled = False
    buy = True
    value = ValueProperty()

    def __init__(self, paper):
        self.paper = paper
        self.value = None

    @property
    def paper(self):
        return self._paper

    @paper.setter
    def paper(self, paper):
        if isinstance(paper, basestring):
            paper = Paper(paper, update=True)
        elif not isinstance(paper, _Paper):
            raise TypeError('Cannot create a paper with', type(paper))
        self._paper = paper
        self.value = None
        if not hasattr(self, 'qtd'):
            self.qtd = paper.step
        elif self.qtd % paper.step != 0:
            self.qtd = paper.step

    @property
    def total(self):
        total = self.get_value() * self.qtd
        if self.buy:
            total *= -1
        return total

    def calculate(self, arange, last_value=False):
        if isinstance(arange, np.ndarray):
            atual = arange.copy()
        else:
            atual = np.array([arange])

        value = self.get_value()
        if last_value:
            value = self.paper.last

        if self.paper.strike is not None:
            less = atual <= self.paper.strike
            great = atual > self.paper.strike
            atual[less] = -value
            atual[great] -= (self.paper.strike + value)
        else:
            atual -= value
        if not self.buy:
            atual *= -1
        return atual * self.qtd

    def get_value(self):
        if self.value:
            return self.value
        else:
            return self.paper.last

    def to_dict(self):
        dic = {
            'paper': self.paper.code,
            'value': str(self.value),
            'qtd': self.qtd,
            'enabled': self.enabled,
            'buy': self.buy,
        }
        return dic

    @staticmethod
    def from_dict(dic):
        paper = PaperItem(dic['paper'])
        paper.value = dic['value']
        paper.qtd = dic['qtd']
        paper.enabled = dic['enabled']
        paper.buy = dic['buy']
        return paper


class PaperException(Exception):
    '''
    Exception code invalid
    '''


def paper_calc(iterable, x, **kwargs):
    return np.array([op.calculate(x, kwargs) for op in iterable]).sum(axis=0)
