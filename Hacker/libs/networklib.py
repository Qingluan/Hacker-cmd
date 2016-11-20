import re
import bs4
from bs4 import BeautifulSoup
from qlib.log import LogControl as L
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
            L.title(self.encoding + "error", "try another charset")
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
        return ShowTags({ 
            'h': self.Soup(h),
            'u': self.Soup('ul'),
            't': self.Soup('table'),
            'f': self.Soup('form'),
            'd': self.Soup('div'),
            'i': self.Soup("img"),
            "a": self.Soup("a"),
            "p": self.Soup(p)
        })

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
            # L.i(tmp)
            if not tmp:
                continue

            res[a] = tmp
        return ShowTags(res)


class ShowTag:

    def __init__(self, tag):
        self._res = tag
        self.attrs = self._res.attrs

    def __repr__(self):
        attrs = self._res.attrs
        attrs.update({"name": self._res.name})
        for attr in attrs:
            L.i(attrs[attr], tag=attr)
        print(" ------------------------------------ ")
        return ''

    def __call__(self, *args, **kargs):
        if isinstance(self._res, bs4.element.Tag):
            return ShowTags(self._res(*args, **kargs))
        else:
            L.err("not supported this search function")
            return None

    def __getitem__(self, key):
        return self._res.get(key)
    

class ShowTags:

    def __init__(self, tags):
        self._res = None
        if isinstance(tags, list):
            self._res = [ShowTag(tag) for tag in tags]
        elif isinstance(tags, dict):
            self._res = {}
            for key in tags:
                v = tags[key]
                if isinstance(v, list):
                    v_list = [ShowTag(tag) for tag in v]
                    self._res[key] = v_list
                elif isinstance(v, bs4.element.Tag):
                    self._res[key] = ShowTag(v)
                else:
                    self._res[key] = v

    def __repr__(self):
        if isinstance(self._res, list):
            for i in self._res:
                i.__repr__()
        elif isinstance(self._res, dict):
            for k in self._res:
                v = self._res[k]
                if isinstance(v, list):
                    for ii in v:
                        ii.__repr__()
                else:
                    v.__repr__()
        return ''

    def __getitem__(self, key):
        return self._res[key]

    def __call__(self, *args, **kargs):
        if isinstance(self._res, list):
            return [ShowTags(i.__call__(*args, **kargs)) for i in self._res]
        elif isinstance(self._res, dict):
            for k in self._res:
                v = self._res[k]
                if isinstance(v, list):
                    return [ShowTags(i.__call__(*args, **kargs)) for i in v]
                elif isinstance(v, ShowTag):
                    return ShowTags(v.__call__(*args, **kargs))
                else:
                    return None
        
