import uuid
import transaction
from sqlalchemy.exc import IntegrityError

from libacr.model.core import DBSession, Group
from libacr.model.content import Content, ContentData, Tag

class InvalidCollectionName(Exception):
    pass

class Depot(object):
    """This emulates a key-value storage system to store and retrieve data in ACR"""
    def create(self, collection, data):
        object_id = str(uuid.uuid1())
        content_name = _make_content_name(collection, object_id)

        collection_name = '_depo_%s' % collection
        collection_tag = DBSession.query(Tag).filter_by(name=collection_name).first()
        while collection_tag is None:
            collection_tag = Tag(name=collection_name)
            internal_tags_group = DBSession.query(Group).filter_by(group_name='acr_internal_tags').first()
            while internal_tags_group is None:
                internal_tags_group = Group(group_name='acr_internal_tags')
                DBSession.add(internal_tags_group)
                try:
                    DBSession.flush()
                except IntegrityError:
                    transaction.abort()
                    internal_tags_group = DBSession.query(Group).filter_by(group_name='acr_internal_tags').first()

            collection_tag.group = internal_tags_group
            DBSession.add(collection_tag)
            try:
                DBSession.flush()
            except IntegrityError:
                transaction.abort()
                collection_tag = DBSession.query(Tag).filter_by(name=collection_name).first()

        content = Content(name=content_name)
        content.tags.append(collection_tag)
        DBSession.add(content)

        content_data = ContentData(content=content, revision=0, value=ContentData.encode(data))
        DBSession.add(content_data)

        return Result(object_id, data)

    def delete(self, collection, object_id):
        content_name = _make_content_name(collection, object_id)

        content_data = DBSession.query(ContentData).join(Content).filter(Content.name==content_name).first()
        if not content_data:
            return None

        previous_data = ContentData.decode(content_data.value)
        DBSession.delete(content_data.content)
        return Result(object_id, previous_data)

    def get(self, collection, object_id):
        content_name = _make_content_name(collection, object_id)

        data = DBSession.query(ContentData).join(Content).filter(Content.name==content_name).first()
        if not data:
            return None

        return Result(object_id, ContentData.decode(data.value))

    def update(self, collection, object_id, data):
        content_name = _make_content_name(collection, object_id)

        content_data = DBSession.query(ContentData).join(Content).filter(Content.name==content_name).first()
        if not content_data:
            return None

        previous_data = ContentData.decode(content_data.value)
        new_data = previous_data.copy()
        new_data.update(data)
        content_data.value = ContentData.encode(new_data)
        return Result(object_id, previous_data)

    def lookup(self, collection, filters):
        content_name = '_depo_%s' % collection

        similar_entries = DBSession.query(ContentData).join(Content).filter(Content.name.like(content_name+'%'))
        for value in filters.values():
            similar_entries = similar_entries.filter(ContentData.value.like('%'+value+'%'))
        return ResultSet(similar_entries, filters)
Depot = Depot()

class ResultSet(object):
    def __init__(self, entries, filters):
        self._iter = iter(entries)
        self._filters = filters

    def _filter(self, entry):
        data = ContentData.decode(entry.value)
        for name, value in self._filters.items():
            if data.get(name) != value:
                return None
        collection_name, object_id = _split_content_name(entry.content.name)
        return Result(object_id, data)

    def __iter__(self):
        return self

    def next(self):
        current = None
        while current is None:
            current = self._filter(self._iter.next())
        return current

    def first(self):
        try:
            return self.next()
        except StopIteration:
            return None

    def all(self):
        return list(self)

    def count(self):
        counter = (-1, None)
        for counter in enumerate(self):
            pass
        return counter[0]+1

def _make_content_name(collection, object_id):
    if '$' in collection:
        raise InvalidCollectionName('Collection names cannot contain "$" character')
    return '_depo_%s$%s' % (collection, object_id)

def _split_content_name(name):
    pre, object_id = name.split('$', 1)
    trash, collection_name = pre.split('_', 1)
    return collection_name, object_id

class Result(object):
    def __init__(self, object_id, data):
        self.object_id = object_id
        self.data = data

    def __repr__(self):
        return '<depot.Result %s>' % self.object_id