from libacr.model.content import ContentData

class EncodedView(object):
    def to_dict(self, data):
        return ContentData.decode(data)

    def from_dict(self, dic):
        return ContentData.encode(dic)
