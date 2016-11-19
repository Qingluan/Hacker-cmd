import re
from bs4 import BeautifulSoup
from qlib.log import LogControl
from qlib.net import to


BASE_ENCODING = (
        'utf-8',
        'gbk',
    )


class BaseWeb:
    def __init__(self, url, **kargs):
        self.raw_response = to(url, **kargs)
        self.encoding = self.raw_response.encoding
        try:
            self.content = self.raw_response.content.decode(self.encoding)
        except UnicodeDecodeError:
            LogControl.title(self.encoding + "error", "try another charset")
            self._decode_raw()

        self.content = re.sub(
                r'(\n)+',
                '\n',
                self.content)
        self.Soup = BeautifulSoup(self.content, "html.parser")

    def _decode_raw(self):
        for e in BASE_ENCODING:
            try:
                self.content = self.raw_response.content.decode(e)
                break
            except UnicodeDecodeError:
                continue

    def smart_remove(self, *tags,content='script'):
        [i.extract() for i in  self.Soup(content)]
        if tags:
            [i.extract() for i in self.Soup(tags)]

    def links(self):
        return self.Soup("a")

    def text(self):
        return self.Soup.body.get_text()

    def __call__(self, tags, *args, **kargs):
        return self.Soup(tags, *args, **kargs)


class BaseAnalyze(BaseWeb):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.smart_remove('link',)
        self.class_ = self.all('class')
        self.id = self.all('id')

    def classfy_by_tag(self):
        h = ['h1', 'h2','h3', 'h4', 'h5', 'h6']
        u = 'ul'
        t = 'table'
        form = 'form'
        p = ["p", "li", "article", "code", "i", "b"]
        return { 
            'h': self.Soup(h),
            'u': self.Soup('ul'),
            't': self.Soup('table'),
            'f': self.Soup('form'),
            'd': self.Soup('div'),
            'i': self.Soup("img"),
            "a": self.Soup("a"),
            "p": self.Soup(p)
        }

    def all(self, attr):
        attrs = []
        for tag in self.Soup(lambda x: x.has_attr(attr)):
            r_tmp = tag.get(attr)
            if isinstance(r_tmp, list):
                attrs += r_tmp
            else:
                attrs.append(r_tmp)

        s = set(attrs)
        if '' in s:
            s.remove('')
        return s

    def all_attrs(self):
        m = set()
        for tag in self.Soup(True):
            for attr in tag.attrs:
                m.add(attr)

        return m

    def classfy_by_attris(self, attr_t, level=1):
        if attr_t == 'class':
            attrs = self.class_
        elif attr_t == 'id':
            attrs = self.id
        else:
            attrs = self.all(attr_t) 

        res = {}
        if level >1:
            self.smart_remove("img")
            if level >2:
                for i in self.Soup(lambda x: not x.text and not x.has_attr('alt') and not x.has_attr('href')):
                    i.extract()
        for a in attrs:
            tmp = self.Soup.body(**{attr_t:a})
            # LogControl.i(tmp)
            if not tmp:
                continue

            res[a] = tmp
        return res
