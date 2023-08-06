from libacr.views.slice_group import SliceGroupRenderer
from routes import url_for
from libacr.lib import url
from webhelpers.feedgenerator import Rss201rev2Feed
from libacr.model.core import DBSession
from libacr.model.content import Slice, Content
from libacr.views.manager import ViewsManager
from sqlalchemy.orm import join

__all__ = ['rss_for_slicegroup']

def get_slicegroup_members(slice):
    config = ViewsManager.find_view('slicegroup').to_dict(slice.content.data)
    filter_tag = config.get('filter_tag', '')
    
    try:
        orderer = config.get('orderer')
        orderer = SliceGroupRenderer.slice_orderers[orderer]
    except:
        orderer = lambda x : x
                  
    slices = DBSession.query(Slice).\
            select_from(join(Slice, Content)).\
            filter(Slice.tags.any(name=filter_tag))
    return orderer(slices)

def rss_for_slicegroup(slice):
    feed = Rss201rev2Feed(title=u"Test", 
                          link=url_for(url(slice.page.url).encode('utf-8'), qualified=True), 
                          description=u"Test feed")
                          
    for member in get_slicegroup_members(slice):
        if member.view in ('html', 'genshi'):
            feed.add_item(title=member.page.title, link=url_for(url(member.page.url).encode('utf-8'), qualified=True), 
                          description=member.preview(omit_link=True))
                          
    return feed.writeString('utf-8')
