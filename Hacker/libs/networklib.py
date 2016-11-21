import re
import requests
from urllib.parse import urljoin, urlencode
from contextlib import contextmanager
import bs4
from bs4 import BeautifulSoup
from qlib.log import LogControl as L
from qlib.net import to
from qlib.io.console import dict_cmd

__doc__ = """
      'Analyze' can parse a web html , classfy by different vec.
   detect the search input form , and search content in html.

"""

BASE_ENCODING = (
        'utf-8',
        'gbk',
    )

H = ['h1', 'h2','h3', 'h4', 'h5', 'h6']
Li = ['ul', 'ol']
T = 'table'
FORM = 'form'
P = ["p", "li", "article", "code", "i", "b"]

@contextmanager
def show_pro(sta, text):
    try:
        L.save()
        L.loc(0,0, True)
        L.i(text, tag = sta, end='\r', tag_color='green', txt_color='yellow', txt_attr=['underline'])
        yield
    finally:
        print('\r')
        L.load()


class BaseWeb:
    def __init__(self, url, show_process=True, cookie=True, session=None, **kargs):
        self.session = session
        if show_process:
            with show_pro("Geting", url + " | " + str(kargs)):
                if isinstance(url, requests.models.Response):
                    self.raw_response = url
                else:
                    if cookie:
                        if not self.session:
                            self.session, self.raw_response = to(url, cookie=True, **kargs)
                        else:
                            _, self.raw_response = to(url, cookie=True, session=self.session, **kargs)
                    else:
                        if self.session:
                            self.raw_response = to(url, session=self.session, **kargs)
                        else:
                            self.raw_response = to(url, **kargs)
        else:
            if isinstance(url, requests.models.Response):
                self.raw_response = url
            else:
                if cookie:
                    self.session, self.raw_response = to(url, cookie=True, **kargs)
                else:
                    if self.session:
                        self.raw_response = to(url, session=self.session, **kargs)
                    else:
                        self.raw_response = to(url, **kargs)

        self.show_process = show_process
        self.url = self.raw_response.url
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
        
        return self.__text_strip__(self.Soup.body.get_text())

    def __text_strip__(self, t):
        return re.sub(r'(\n)+','\n',t)

    def format(self, style='list'):
        """
        list , table, all
        """
        sub = None
        if style == "list":
            sub = self.Soup.body(Li)
        elif style == 'table':
            sub = self.Soup.body([T] + Li )
        elif style == 'all':
            sub = self.Soup.body([T] + H + Li)
        else:
            sub = self.Soup.body(style.splti())
        # return self.__text_strip__('\n'.join([i._res.get_text() for i in sub if i._res]))
        return self.__text_strip__('\n'.join([i.get_text() for i in sub]))

    def __call__(self, tags, *args, **kargs):
        return ShowTags(self.Soup(tags, *args, **kargs))


class BaseAnalyze(BaseWeb):
    """
    base parser a web
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.smart_remove('link',)
        self.class_ = self.all('class')
        self.id = self.all('id')
        self.links = Links([i.href for i in super().__call__("a") if hasattr(i, "href")])
        self.forms = Forms(super().__call__("form"))
        
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
        self.attrs = self._res.attrs if hasattr(self._res, 'attrs') else None
        self.name = tag.name if hasattr(self._res, 'name') else None
        if self.attrs:
            for attr in self.attrs:
                v = self.attrs[attr]
                if v:
                    setattr(self, attr, v)

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
            self.keys = self._res.keys()

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
            return [i.__call__(*args, **kargs) for i in self._res]
        elif isinstance(self._res, dict):
            for k in self._res:
                v = self._res[k]
                if isinstance(v, list):
                    return [i.__call__(*args, **kargs) for i in v]
                elif isinstance(v, ShowTag):
                    return v.__call__(*args, **kargs)
                else:
                    return None
        


                
class Analyze(BaseAnalyze):
    """
    Analyze and handle
    """
        
    def Go(self, id):
        """
        can just input a id from self.links get the realurl
        """
        if isinstance(id, str):
            link = id
        elif isinstance(id, int):
            link = self.links[id]
        else:
            return None

        return Analyze(urljoin(self.url, link),
            session=self.session,
            show_process=self.show_process)

    def login(self, key='login', **data):
        link = None
        form = None
        method = 'post'
        id = None
        for i,f in enumerate(self.forms):
            if f.action.find(key) != -1 and f.method.lower() == 'post':
                link = f.action
                form = f
                id = i
                break

        if not link:
            L.err("no search form action be found !", txt_color='red')
            L.i('type search("xxx", key="[ here]")' ,tag="only found 'key' :\n")
            for i,v in enumerate(self.forms):
                L.i(v.action, tag=i)
            return None

        data = self.form_check(id, data)
        with show_pro('loging', link):
            res = to(urljoin(self.url, link),
                session=self.session,
                data=data,
                agent=True,
                method=method)
        return Analyze(res)

    def search(self, search_str, key='search'):
        link = None
        form = None
        method = None
        id = None
        for i,f in enumerate(self.forms):
            if f.action.find(key) != -1:
                link = f.action
                form = f
                id = i
                break

        # find GET form as search form
        for i,f in enumerate(self.forms):
            if f.method.lower() == 'get':
                link = f.action
                form = f
                id = i
                break

        if not link:
            L.err("no search form action be found !", txt_color='red')
            L.i('type search("xxx", key="[ here]")' ,tag="only found 'key' :\n")
            for i,v in enumerate(self.forms):
                L.i(v.action, tag=i)
            return None

        method = form.method.lower()
        f_table = {}
        for name in form.names():
            f_table[name] = search_str

        if method == 'get':
            link += "?%s" %  urlencode(f_table)
            
            return  Analyze(urljoin(self.url, link),
                show_process=self.show_process,
                session=self.session,
                method=method)
        else:
            res = to(link,
                method=method,
                session=self.session,
                data=f_table)

            if res.headers['Content-Type'].find("json") != -1:
                return res.json()
            elif res.headers['Content-Type'].find('ml') != -1:
                return Analyze(res,
                    session=self.session,
                    show_process=self.show_process)
            else:
                L.err("return res is not json or xml", res.headers['Content-Type'])
                return None

    def form_check(self, id, data):
        form = self.forms[id]
        i_keys = set(data.keys())
        t_keys = set(form.names())
        inputs = form.input

        t_table = { 
            i.name:i.value 
                if hasattr(i, 'value') 
                else None 
            for i in  inputs
                if i.type.lower() != 'submit'
        }

        if i_keys <= t_keys:
            pass
        else:
            L.err("only supported\n", t_table)
            return None
        
        t_table.update(data)
        need_to_fill = {}
        for k in t_table:
            if not t_table[k]:
                need_to_fill[k] = None

        t_table.update(dict_cmd(need_to_fill))
        return t_table
        
        
    def Post(self,form_id, **data):
        link = self.forms[form_id].action
        return Analyze(urljoin(self.url, link), show_process=self.show_process, method='post', data=data)
    
    def ShowForm(self, form_id):
        self.forms[form_id].show()

class Form:
    def __init__(self, form):
        if not isinstance(form, (ShowTag, bs4.element.Tag,)):
            raise TypeError("must be form Tag or bs4 Tag")
        self._res = form
        self.input = form("input")
        for attr in form.attrs:
            v = form.attrs[attr]
            if v:
                setattr(self, attr, v)
    
    def names(self):
        return [input.name for input in self.input if input.type != 'submit' ]

    def show(self):
        self.input.__repr__()

    def __repr__(self):
        self._res.__repr__()
        return ''

class Forms:

    def __init__(self, forms):
        self._res = [Form(f) for f in forms if 'action' in f.attrs]

    def __repr__(self):
        for i,f in enumerate(self._res):
            L.i(f.action, f.method, tag=i)
        return ''

    def __getitem__(self, k):
        return self._res[k]
        
        
class Links:
    def __init__(self, links):
        self._res = links

    def __call__(self,search_str):
        res = {}
        if isinstance(self._res, list):
            for i,link in enumerate(self._res):
                if link.find(search_str) != -1:
                    res[i] = link
            return Links(res)
        elif isinstance(self._res, dict):
            return Links({ k: self._res[k] for k in self._res if self._res[k].find(search_str) != -1})
            
    def __getitem__(self, k):
        return self._res[k]

    def __repr__(self):
        if isinstance(self._res, list):
            for i, v in enumerate(self._res):
                L.i(v, tag=i)
        elif isinstance(self._res, dict):
            for k in self._res:
                v = self._res[k]
                L.i(v, tag=k)
        return ''


class Google(Analyze):
    """
    @keywords can use google's search keywords
    @proxy must be right. default "socks5://127.0.0.1:1080"

    """
    BASE_KEYS = {
        "num":100,
        "start":0,
        "meta":"",
        "hl":"en",
        "q": None,
    }

    def __init__(self, keywords, *args, proxy='socks5://127.0.0.1:1080', **kargs):
        self.google_search_str = keywords
        self.google_other_keys = kargs
        self.google_keys = Google.BASE_KEYS
        self.google_keys['q'] = keywords
        self.proxy = proxy
        self.item_now = 0
        self.google_url = "https://www.google.com/search?"
        url = self.google_url + urlencode(self.google_keys)
        super().__init__(url, *args, proxy=proxy, **kargs)
        self.item_now = 100

    def next_page(self):
        self.google_keys['start'] = self.item_now
        url = self.google_url + urlencode(self.google_keys)
        res = Analyze(url, proxy=self.proxy, **self.google_other_keys)
        self.item_now += 100
        return res


class Linkedin(Google):

    def __init__(self, key, *args, **kargs):
        super().__init__("site:linkedin.com/in " + key, *args, **kargs)





