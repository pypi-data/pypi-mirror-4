import feedparser
import socket, operator, time
import tw.forms as twf
from datetime import datetime, timedelta

from base import EncodedView

socket.setdefaulttimeout(1)

class FeedRenderer(EncodedView):
    def __init__(self):
        self.name = 'rss'
        self.form_fields = [twf.TextField('url', label_text="Url:",
                                          validator=twf.validators.URL(not_empty=True, strip=True)),
                            twf.TextField('tag', label_text="Filter On Tag:",
                                          validator=twf.validators.String(strip=True))]
        self.exposed = True
        self.cache = {}

    def render(self, page, slice, data):
        data = self.to_dict(data)

        if self.cache.has_key(slice.uid) and self.cache[slice.uid]['time'] + timedelta(0, 900) >= datetime.now():
            feeds = self.cache[slice.uid]['feeds']
        else:
            feeds = data['url'].split('\n')
            feeds = map(lambda x : feedparser.parse(x).entries, feeds)
            feeds = reduce(operator.concat, feeds)
            if data['tag']:
                feeds = filter(lambda x : data['tag'] in map(lambda y : y['term'], x['tags']), feeds)
            feeds = sorted(feeds, lambda x,y : cmp(y.date_parsed, x.date_parsed))

            if feeds:
                self.cache[slice.uid] = dict(time=datetime.now(), feeds=feeds)

        res = ''
        for entry in feeds:
            res+='<div class="acr_rss_entry">'
            res+='<h3><a href="%s">%s</a></h3>' % (entry.link, entry.title)
            res+='<span class="acr_rss_info"><span class="acr_rss_author">%s</span> - %s</span>' % (entry.author, time.strftime("%Y-%m-%d %H:%M", entry.date_parsed))
            res+='<p>%s</p>' % entry.description
            res+='</div>'
        return res
    
    def preview(self, page, slice, data):
        return 'Preview not Implemented'

class TwitterRenderer(object):
    def __init__(self):
        self.name = 'twitter_rss'
        self.cache={}
        self.exposed = True
        self.form_fields = [twf.TextField('data', label_text="Url:", validator=twf.validators.URL(not_empty=True, strip=True))]

    def to_dict(self, data):
        return {'data':data}

    def from_dict(self, dic):
        return dic['data']

    def render(self, page, slice, data):
        start=data.startswith('[') 
        if start:
           value = data.split(']')
           number=value[0].lstrip('[')
           url= value[1]
           feeds = url.split('\n')
           feeds = map(lambda x : feedparser.parse(x).entries[0:int(number)], feeds)
        else:
           feeds = data.split('\n')
           feeds = map(lambda x : feedparser.parse(x).entries, feeds)
        feeds = reduce(operator.concat, feeds)
        feeds = sorted(feeds, lambda x,y : cmp(y.date_parsed, x.date_parsed))
        if feeds:
           self.cache[slice.uid]=feeds
        
        list_feed=self.cache.get(slice.uid,[])
        res = ''
        for entry in list_feed:
            res+='<div class="acr_twitter_entry">'
            res+='<span><a href="%s">%s</a></span>' % (entry.link, (time.strftime("%Y-%m-%d %H:%M", entry.date_parsed)))
            res+='<p>%s</p>' % entry.description
            res+='</div>'
        return res

    def preview(self, page, slice, data):
        return 'Preview not Implemented'