# -*- coding: utf-8 -*-
from tg import expose, flash, require, url, request, redirect, TGController
from tg import tmpl_context, validate, config

from pylons import response
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates

from libacr.lib import url
from libacr import acr_zones
from libacr.forms import order_values
from libacr.model.core import DBSession
from libacr.model.comments import Comment

from sprox.formbase import AddRecordForm
from sprox.widgets import HiddenField
from formencode import validators

from datetime import datetime, timedelta

class CommentsController(TGController):
    @expose()
    def post(self, **kw):
        del kw['sprox_id']
        kw['time'] = datetime.now()
        kw['owner'] = request.identity and request.identity['user'] or None

        comment = Comment(**kw)
        DBSession.add(comment)   
        
        flash("Comment registered")
        return redirect(tmpl_context.pylons.request.referer)
    
