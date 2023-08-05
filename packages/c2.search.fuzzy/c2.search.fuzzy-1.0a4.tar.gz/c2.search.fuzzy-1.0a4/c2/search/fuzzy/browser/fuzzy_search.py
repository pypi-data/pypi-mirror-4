#!/usr/bin/env python
# encoding: utf-8
from time import time
import json
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
try:
    import MeCab
    from c2.splitter.mecabja.mecab import get_wakati_only_part
    HAS_MECAB = True
except ImportError:
    HAS_MECAB =False
from c2.search.fuzzy.automata import Matcher, find_all_matches
from c2.search.fuzzy.words_for_fuzzy_tool import _s_uni, _normalize
try:
    import collective.memcached
    MEMCACHE_AVAILABLE = True
except ImportError:
    MEMCACHE_AVAILABLE = False


def _cache_key(func, *args, **kw):
    cache_time = 60 * 60 * 24 #86400s (1day)
    cache_time_key = time() // (cache_time)
    return " ".join((str(cache_time_key), func.__name__, repr(args), repr(kw)))

@ram.cache(_cache_key)
def _cached_near_word(tool, s, k):
    if MEMCACHE_AVAILABLE:
        return list(_get_near_word(tool, s, k))
    else:
        return _get_near_word(tool, s, k)

def _get_near_word(tool, s, k=1):
    s = _s_uni(s)
    words = tool.get_all_yomi()
    m = Matcher(words)
    return find_all_matches(s, k, m)

def get_near_main(tool, s):
    k = 1
    sleuth_len = 8
    long_k = 2
    k_ja_minus = -1
    s = _s_uni(s.strip())
    if HAS_MECAB:
        part_adaptor = MeCab.Tagger()
        ss = get_wakati_only_part(_normalize(s), adaptor=part_adaptor,
                    part=("名詞", "動詞"))
    else:
        ss = ((w, w) for w in _normalize(s).split())
    for p, y in ss:
        k = k if len(_s_uni(y)) < sleuth_len else long_k
        if p != y: # is Japanese?
            k = k + k_ja_minus
        for yomi in _cached_near_word(tool, y, k=k):
            for word in tool.get_all_dic().get(yomi, []):
                if word and word.lower() != _s_uni(p).lower(): # if not is same word
                    yield word


class FuzzySearch(BrowserView):
    """
    """
    template = ViewPageTemplateFile('fuzzy_search.pt')

    def __init__(self, context, request):
        """
        """
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, "portal_catalog")
        self.fuzzy_tool = getToolByName(self.context, 'words_for_fuzzy')
        super(FuzzySearch, self).__init__(context, request)

    def __call__(self, *args, **kw):
        response_type = self.request.form.get('r_type', '')
#        self.base_url = getToolByName(self.context, 'portal_url')()
        if response_type.lower() == 'json':
            return self.get_json()
        return self.template()

    def get_keitaiso(self):
        text = self.request.form.get('search_text', None)
        if not text or not HAS_MECAB:
            return []
        return get_wakati_only_part(text, adaptor=MeCab.Tagger(), part=("名詞", "動詞"))

    def _get_near_main(self, s):
        return get_near_main(self.fuzzy_tool, s)

    def get_near(self):
        s = self.request.form.get('search_text')
        if not s:
            return []
        return self._get_near_main(s)

    def get_json(self):
        s = self.request.form.get("search_text")
        if s is None:
            return None
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'s':list(set(self._get_near_main(s)))})