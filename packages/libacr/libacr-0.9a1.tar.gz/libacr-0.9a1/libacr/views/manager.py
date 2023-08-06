from core import *
from feeds import *
from menu import *
from slice_group import *
from comments import *
from file_entry import *
from form import *
from image import *
from video import *
from search import *
from user_defined_views import *

from libacr.model.core import DBSession
from libacr.model.content import View

class ViewsManager(object):
    def __init__(self):
        self.views = [HTMLRenderer(), GenshiRenderer(), MenuRenderer(),
                      LinkRenderer(), AjaxRenderer(), FeedRenderer(),
                      SliceGroupRenderer(), CommentsRenderer(),
                      TwitterRenderer(), FileRenderer(),
                      FormRenderer(), ImageRenderer(), SearchRenderer(),
                      VideoRenderer(), ScriptRenderer(), TagCloudRenderer(),
                      BlogPostRenderer()]

        self.forms = {}

    def __call__(self):
        return self

    @property
    def rdisk_views(self):
        return [view for view in self.views if view.exposed == 'RDisk']

    @property
    def all_views(self):
        cur_views = self.views[:]
        for view in DBSession.query(View).filter_by(type='template').all():
            cur_views.append(UserDefinedViewRendererTemplate(view.name, view.code))
        return cur_views

    def view_names(self):
        views = [v.name for v in self.views]
        views.extend((v[0] for v in DBSession.query(View.name)))
        return views

    def find_view(self, name):
        view = filter(lambda view : view.name == name, self.views)
        if view:
            view = view[0]
        else:
            try:
                view = DBSession.query(View).filter_by(name=name).one()
                view = UserDefinedViewRendererTemplate(view.name, view.code)
            except:
                view = None
        return view

    def find_registered_view(self, name):
        view = filter(lambda view : view.name == name, self.views)
        if view:
            return view[0]
        return None

    def register_view(self, view):
        try:
            view_name = view.name
        except:
            raise NameError, 'Your view is missing View.name or View.type attributes'

        if not self.find_registered_view(view_name):
            self.views.append(view)
            exists = False

        if exists:
            raise NameError, 'A view with that name is already registered'

    def create_form(self, view, baseform):
        site_key = request.host
        if not self.forms.has_key(site_key):
            self.forms[site_key] = {}

        if not self.forms[site_key].has_key(view):
            self.forms[site_key][view] = {}

        if not self.forms[site_key][view].has_key(baseform):
            fields = baseform()
            fields.append(twf.HiddenField('view', default=view))

            fields_already_in_form = [oldfield.name for oldfield in fields]
            fields_to_add = filter(lambda field : field.name not in fields_already_in_form,
                                   ViewsManager.find_view(view).form_fields)
            fields.extend(fields_to_add)

            self.forms[site_key][view][baseform] = twf.TableForm(fields=fields, submit_text="Save")

        return self.forms[site_key][view][baseform]

    def validator(self, baseform):
        class AutoDetectedViewForm(object):
            def __init__(self, baseform):
                self.baseform = baseform

            def validate(self, params, state):
                form = ViewsManager.create_form(params['view'], self.baseform)
                return form.validate(params, state)
        return AutoDetectedViewForm(baseform)

    def encode(self, view, dic):
        return ViewsManager.find_view(view).from_dict(dic)

    def decode(self, view, data):
        d = ViewsManager.find_view(view).to_dict(data)
        d['view'] = view
        return d
ViewsManager = ViewsManager()
