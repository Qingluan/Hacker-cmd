# -*- coding:utf-8 -*- 
import re
import pickle
import requests
import copy
from urllib.parse import urljoin, urlencode
from contextlib import contextmanager
from termcolor import  colored
import bs4
import pandas
from bs4 import BeautifulSoup
from qlib.log import LogControl as L
from qlib.net import to
from qlib.io.console import dict_cmd

__doc__ = """
      'Analyze' can parse a web html , classfy by different vec.
   detect the search input form , and search content in html.

"""

BASE_ENCODING = (
        'gbk',
        'utf-8',
    )

ERR_ENCODING_2_RIGHT = {
    'iso-8859-1': 'utf-8',
}

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

def un_recursion(lst):
    if isinstance(lst, list):
        for l in lst:
            yield from un_recursion(l)
    else:
        yield lst



class BaseWeb:
    def __init__(self, url, show_process=True, cookie=True, session=None, **kargs):
        self.session = session
        if show_process:
            with show_pro("Geting", str(url) + " | " + str(kargs)):
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
        self.encoding = self.raw_response.encoding.lower()
        # L.err(self.encoding)

        # check if encoding is iso-8859-1
        self.encoding = ERR_ENCODING_2_RIGHT.get(self.encoding, self.encoding)

        try:
            self.content = self.raw_response.content.decode(self.encoding)
        except UnicodeDecodeError as e:
            L.err(e)
            L.title(self.encoding + "error", "try another charset" )
            self._decode_raw()
            
                


        self.content = re.sub(r'(\n)+', '\n', self.content)
        self.Soup = BeautifulSoup(self.content, "html.parser")
        self.Base = copy.copy(self.Soup)

    def _decode_raw(self):
        ok = False
        for e in BASE_ENCODING:
            try:
                self.content = self.raw_response.content.decode(e)
                ok = True
                break
            except UnicodeDecodeError:
                L.title(e, " err")
                continue

        if not ok:
            self.content = self.raw_response.content.decode("iso-8859-1")
            # print(self.raw_response.content)
    
    def save(self, file):
        with open(file, "wb") as fp:
            pickle.dump(self.raw_response, fp)

    @classmethod
    def load(cls, file):
        with open(file, 'rb') as fp:
            data = pickle.load(fp)
            return cls(data)

    def smart_remove(self, *tags, content=['script', 'style']):
        """
        @content : remove these tags.
        @tags: additional tags to remove
        """
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
        self.css = self.__call__("style", "link")
        self.script = self.__call__("script")
        self.smart_remove()
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
        """
        can see all the attrs sub self tag.
        like :  self.all("name")
            # this will get all tags' kind .

                self.all('id')
            # this will get all the ids sub this tag
         """
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

    def all(self, attr):
        """
        can see all the attrs sub self tag.
        like :  self.all("name")
            # this will get all tags' kind .

                self.all('id')
            # this will get all the ids sub this tag
         """
        attrs = []
        for tag in self(lambda x: hasattr(x,attr)):
            r_tmp = getattr(tag, attr)
            if isinstance(r_tmp, list):
                attrs += r_tmp
            else:
                attrs.append(r_tmp)

        s = set(attrs)
        if '' in s:
            s.remove('')
        return s

    def tags(self):
        return self.all("name")

    def text(self):
        if hasattr(self._res, "text"):
            return self._res.text

    def strings(self):
        if hasattr(self._res, "strings"):
            return self._res.strings

    def string(self):
        if hasattr(self._res, "string"):
            return self._res.string

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

    def __len__(self):
        return len(self._res)

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
        
    def text(self):
        if len(self._res) == 1:
            return self._res[0].text()
        else:
            texts = []
            for t in self._res:
                texts.append(t.text())
            return texts

    def tags(self):
        
        if len(self._res) == 1:
            return self._res[0].tags()
        else:
            a = set()
            for t in self._res:
                for i in t.tags():
                    a.add(i)
            return a


                
class Analyze(BaseAnalyze):
    """
    Analyze and handle
    @show_process: if show a progress bar .
    @cookie [bool]
        can use cookie to scarp cookie , return session, response
    @proxy
        proxy={
            'https': 'socks5://127.0.0.1:1080',
            'http': 'socks5://127.0.0.1:1080'
        }

        ... 
        proxy='socks5://127.0.0.1:1080'
    @ssl [bool]
        can trans 'wwwxxx.xxxx' -> 'https://' xxxx
    @data [dict]
        post's payload
    @agent [bool /str]
        if True:
            will use random agent from {....} [841]
        if str:
            will set User-agent: agent directly
    @parser [str/None] 'bs4/lxml utf8/gbk'
        import it as parser.
    @options:
        @headners
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

    def post(self, key,**data):
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
        return Analyze(res, session=self.session)


    def login(self, key='login', **data):
        return self.post(key, **data)
        # link = None
        # form = None
        # method = 'post'
        # id = None
        # for i,f in enumerate(self.forms):
        #     if f.action.find(key) != -1 and f.method.lower() == 'post':
        #         link = f.action
        #         form = f
        #         id = i
        #         break

        # if not link:
        #     L.err("no search form action be found !", txt_color='red')
        #     L.i('type search("xxx", key="[ here]")' ,tag="only found 'key' :\n")
        #     for i,v in enumerate(self.forms):
        #         L.i(v.action, tag=i)
        #     return None

        # data = self.form_check(id, data)
        # with show_pro('loging', link):
        #     res = to(urljoin(self.url, link),
        #         session=self.session,
        #         data=data,
        #         agent=True,
        #         method=method)
        # return Analyze(res, session=self.session)

    def search(self, search_str, key='search'):
        link = None
        form = None
        method = None
        id = None

        

        for i,f in enumerate(self.forms):
            if not hasattr(f, 'method'):
                f.method = 'get' # just for js's search form

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
            i = form[name]['value']
            if not i:
                f_table[name] = search_str
            else:
                f_table[name] = i

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
        r_ks = []
        for k in data:
            if data[k] == "*None*":
                r_ks.append(k)

        t_table.update(data)
        need_to_fill = {}
        for k in t_table:
            if not t_table[k]:
                need_to_fill[k] = None

        t_table.update(dict_cmd(need_to_fill))
        for k in r_ks:
            t_table.pop(k)
        return t_table
        
        
    def Post(self,form_id, **data):
        link = self.forms[form_id].action
        return Analyze(urljoin(self.url, link), show_process=self.show_process, method='post', data=data)
    
    def ShowForm(self, form_id):
        self.forms[form_id].show()

    def table(self, name="csv"):
        """
        supported dict and csv
        """
        # L.wrn("check")
        return getattr(TableAtom(self),  name)

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

    def __getitem__(self, k):
        for i in self.input:
            if i.name == k:
                return i

    def __repr__(self):
        self._res.__repr__()
        return ''

class Forms:

    def __init__(self, forms):
        self._res = [Form(f) for f in forms if 'action' in f.attrs]

    def __repr__(self):
        for i,f in enumerate(self._res):
            m = f.method if hasattr(f, 'method') else 'no method'
            L.i(f.action, m, tag=i)
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

    def __init__(self, keywords, *args, start=0, proxy='socks5://127.0.0.1:1080', **kargs):
        self.google_search_str = keywords
        self.google_other_keys = kargs
        self.google_keys = Google.BASE_KEYS
        self.google_keys['q'] = keywords
        self.proxy = proxy
        self.item_now = start
        self.google_url = "https://www.google.com/search?"
        url = self.google_url + urlencode(self.google_keys)
        super().__init__(url, *args, proxy=proxy, **kargs)
        self.item_now = start + 100
        self.google_result = list()

    def __getitem__(self, key):
        """
        r: mean get result from google_results
        i: mean get index from set
        """
        _r = []
        for i in self.google_result:
            r = i[key]
            if r:
                _r.append(r)
        return _r

    def next_page(self):
        """
        go to next page
        """
        self.google_keys['start'] = self.item_now
        url = self.google_url + urlencode(self.google_keys)
        res = Google( self.google_search_str, start=self.item_now ,proxy=self.proxy, **self.google_other_keys)
        self.item_now += 100
        return res

    def parse(self):
        """
        parse text and images
        """
        for res in self('div', class_="g"):
            if res:
                self.google_result.append(GoogleText(res._res))

    def show(self, start=0, end=None):
        if not end:
            _l = self.google_result[start:]
        else:
            _l = self.google_result[start: end]
    
        for i in _l[::-1]:
            i.show()

    def stats(self):
        return self("div", id="resultStats")[0].text()

    def __repr__(self):
        return self.google_keys['q'] + '|' + str(self.google_keys['start'])

class TextAtomException(TypeError):
    pass

class TextAtom:
    """
    this will parse a single item from a list tags.
    to find time, img , title, doc, video, link 
    """

    def  __init__(self, tag):
        self.title = ''
        self.link = None
        self.time = None
        self.doc = None
        self.img = None
        self.video = None
        self.other_links = None
        self.attrs = {}
        self._res = tag

        self._parse_title()
        self._parse_link()
        self._parse_doc()
        self._parse_img()
        self._parse_time()
        

    def __getitem__(self, k):
        """
        t: type to search:
            [a, c, t]   # attrs , content , title
        """
    
        if k in self.title:
            return self
    
        for i in un_recursion([list(i.attrs.values()) for i in self._res(True)]):
            if k in i:
                return self
    
        if k in self._res.text:
            return self
    
        return None

        

    def show(self, t='c'):
        """
        t == 'c':
            show in console
        t == 'b':
            show in browser
        """
        if t == 'c':
            L.i(self.link, tag=self.title, txt_color='yellow', txt_attr=['underline'])
            if self.time:
                L.i(self.time, tag='T', txt_attr=['bold'])
            if self.img:
                L.i(self.img, tag='img')
            L.i(self.doc, tag='doc', end='\n' + '-'* (L.SIZE[1] -10) +'\n' )

        else:
            pass

    def _parse_title(self, **kargs):
        """
        Principle:
          if the title is None after parse_link to find h tag.
        """
        
        title_t = self._res(['h1','h2', 'h3', 'h4'])
        self.title = '|'.join([i.text for i in title_t])


    def _parse_link(self, **kargs):
        """
        Principle:
          i declare the first a tag include title and link.
        """

        links = self._res(lambda x: x and x.name == 'a' and len(x.text) > 2, **kargs)
        if len(links) >= 1:
            self.link = links[0]['href']
            if not self.title:
                self.title = links[0].text

        if len(links) > 1:
            self.other_links = ShowTags(links[1:])
    
    def _parse_doc(self, tags=['p', 'span', 'article'], **kargs):
        """
        Principle:
          i think the doc's tag  include 'p', 'span', 'b', 'i', 'em', 
        """
        doc_t = self._res(tags)
        if not doc_t:
            doc_t = self._res(["div","li"])

        self.doc = '\n'.join([i.text for i in doc_t])

    def _parse_img(self):
        imgs = self._res('img')
        if imgs:
            self.img = ShowTags(imgs)

    def _parse_time(self, **kargs):
        times_t = ''.join([i.text for i in self._res(True)])
        times_a = ''.join(un_recursion([ list(i.attrs.values()) for i in self._res(True)]))
        _t = TextTimeAtom(times_a + times_t)
        if _t.if_find:
            self.time = _t.txt()

    def __repr__(self):
        return self.title + '(%s)' % self.__class__.__name__



class TextTimeAtom:
    patterns = [
        r'((?:\d{4})[ \-\/\.年]{1,4}(?:\d{1,2})[\D]{1,4}(?:\d{1,2}))', # baidu.com
        r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\D{1,4}(?:\d{1,2})\D{1,4}(?:\d{4}))', # google.com
        r'((?:\d{1,2}) hours ago)', # hours ago , google.com
        r'((?:\d{1,2})小时前)', # hours ago , baidu.com
    ]


    def __init__(self, raw_str):
        self.if_find = False
        self._time = []

        self.find(raw_str)


    def find(self, strs):
        self._time = list(set(un_recursion([re.findall(p, strs.lower()) for p in TextTimeAtom.patterns]) ))
        if self._time:
            self.if_find = True

    def __getitem__(self, k):
        return self._time[k]

    def txt(self):
        return ','.join(self._time)

    def __repr__(self):
        return self.txt()
            

class TableAtom:

    def __init__(self, soup):
        self.tables = soup("table")
        self._meta = None
        self._base()

    def _base(self):
        base = []
        csv = ""
        head = []
        l = 0
        meta = dict()

        def all_lines(tables):
            for table in tables:
                for tr in table("tr"):
                    yield tr

        for i, tr in enumerate(all_lines(self.tables)):

            tmp = [ i.strip() for i in tr("td").text()]
            # if i == 0:
            #     head = tmp
            
            if not head or l != len(tmp) :
                head = tmp
            l = len(tmp)
            ol = meta.get(len(tmp), [])
            ol.append(i)
            meta[len(tmp)] = ol
            csv += ",".join(tmp) + "\n"
            base.append(tmp)
        self._res = base
        self.csv = csv
        self._head = head
        self._meta = meta

    @property
    def dict(self):
        max_c = max(self._meta, key=lambda x: len(self._meta[x]))
        max_c_c = len(self._meta[max_c])
        # L.err(max_c, max_c_c, self._meta)
        vals = []
        for k in self._meta[max_c]:
            vals.append(self._res[k])
        
        # L.err(vals)
        return pandas.DataFrame(vals, columns=self._head)

    @property
    def raw(self):
        return self._res

    @property
    def meta(self):
        return self._meta

    @property
    def head(self):
        return self._head



class GoogleText(TextAtom):

    def  __init__(self, tag):
        super().__init__(tag)

        if tag.name == 'div' and 'g' in tag['class']:
            self._res = tag
        else:
            self._res = None
            L.err("not google text item")

    def _parse_link(self, **kargs):
        super()._parse_link(**kargs)
        tmp = self._res('cite')
        self.link = tmp[0].text if tmp else ''


class Linkedin(Google):

    def __init__(self, key, *args, **kargs):
        super().__init__("site:linkedin.com/in " + key, *args, **kargs)

        
