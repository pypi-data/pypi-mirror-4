## Copyright 2011-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

r"""
A shortcut to classes and methods needed 
when defining your database structure in a `models` module.

The name "dd" stands for "Data Definition".

A small wrapper around Django's `Model` class 
which adds some Lino specific features:

- :class:`Model <lino.core.model.Model>`

Tables:

- :class:`Table <lino.core.dbtables.Table>`
- :class:`VirtualTable <lino.core.tables.VirtualTable>`
- :class:`Frame <lino.core.frames.Frame>`

Extended Fields:

- :class:`NullCharField <lino.core.fields.NullCharField>`
- :class:`IncompleteDateField <lino.core.fields.IncompleteDateField>`
- :class:`PasswordField <lino.core.fields.PasswordField>`
- :class:`MonthField <lino.core.fields.MonthField>`
- :class:`QuantityField <lino.core.fields.QuantityField>`
- :class:`PriceField<lino.core.fields.PriceField>`
- :class:`GenericForeignKey <lino.core.fields.GenericForeignKey>`
- :class:`GenericForeignKeyIdField <lino.core.fields.GenericForeignKeyIdField>`
- :class:`RecurrenceField <lino.core.fields.RecurrenceField>`
- :class:`DummyField <lino.core.fields.DummyField>`
- :func:`ForeignKey <lino.core.fields.ForeignKey>`

Babel fields:

- :class:`BabelCharField <lino.utils.babel.BabelCharField>`
- :class:`BabelTextField <lino.utils.babel.BabelTextField>`

Virtual Fields:

- :class:`Constant <lino.core.fields.Constant>` and 
  :class:`@constant <lino.core.fields.constant>`
- :class:`DisplayField <lino.core.fields.DisplayField>` and 
  :class:`@displayfield <lino.core.fields.displayfield>`
- :class:`VirtualField <lino.core.fields.VirtualField>` and
  :class:`@virtualfield <lino.core.fields.virtualfield>`
- :class:`HtmlBox <lino.core.fields.HtmlBox>`

Layouts:

- :class:`FormLayout <lino.core.layouts.FormLayout>`
- :class:`Panel <lino.core.layouts.Panel>`
  
Utilities:

- :func:`fields_list <lino.core.fields.fields_list>`
- :func:`resolve_field <lino.core.modeltools.resolve_field>`
- :func:`resolve_model <lino.core.modeltools.resolve_model>`
- :func:`resolve_app <lino.core.modeltools.resolve_app>` 
- :func:`chooser <lino.utils.choosers.chooser>` 
- :func:`add_user_group` 
- :func:`inject_quick_add_buttons` 
- :func:`update_field` 
- :func:`inject_field` 

Actions:

- :class:`RowAction <lino.core.actions.RowAction >`
- :class:`ChangeStateAction <lino.core.changes.ChangeStateAction>`
- :class:`NotifyingAction <lino.core.actions.NotifyingAction>`
- :class:`AuthorRowAction <lino.mixins.AuthorRowAction>`

Miscellaneous:

- :class:`ChoiceList <lino.core.choicelists.ChoiceList>`
- :class:`Workflow <lino.core.workflows.Workflow>`


- :class:`UserProfiles <lino.utils.auth.UserProfiles>`
- :class:`UserGroups <lino.utils.auth.UserGroups>`
- :class:`UserLevels <lino.utils.auth.UserLevels>`


"""

import logging
logger = logging.getLogger(__name__)


from lino.core.tables import VirtualTable

from lino.core.modeltools import resolve_model, resolve_app, resolve_field, get_field, UnresolvedModel
from lino.core.modeltools import full_model_name
from lino.core.modeltools import models_by_base

from lino.core.model import Model

#~ from lino.core.table import fields_list, inject_field
from lino.core.dbtables import has_fk
from lino.core.dbtables import Table
from django.db.models.fields import FieldDoesNotExist
from django.db import models
from django.conf import settings
#~ Model = models.Model
#~ from lino.core import table
#~ Table = table.Table

from lino.core.dbtables import summary, summary_row

from lino.core.frames import Frame
from lino.core.dialogs import Dialog

from lino.core.actions import action
#~ from lino.core.actions import Action
from lino.core.actions import RowAction
from lino.mixins import AuthorRowAction
#~ from lino.core.actions import ListAction
from lino.core.actions import GridEdit, ShowDetailAction
from lino.core.actions import InsertRow, DeleteSelected
from lino.core.actions import SubmitDetail, SubmitInsert
#~ from lino.core.actions import Calendar

from lino.core.choicelists import ChoiceList, Choice
from lino.core.workflows import Workflow, ChangeStateAction
#~ from lino.core.changes import ChangeStateAction
from lino.core.actions import NotifyingAction


from lino.core.fields import fields_list
from lino.core.fields import DummyField
from lino.core.fields import RecurrenceField
from lino.core.fields import GenericForeignKey
from lino.core.fields import GenericForeignKeyIdField
from lino.core.fields import IncompleteDateField
from lino.core.fields import DatePickerField
from lino.core.fields import NullCharField
from lino.core.fields import PasswordField
from lino.core.fields import MonthField
#~ from lino.core.fields import LinkedForeignKey
from lino.core.fields import QuantityField
from lino.core.fields import HtmlBox, PriceField, RichTextField

from lino.core.fields import DisplayField, displayfield
from lino.core.fields import VirtualField, virtualfield
from lino.core.fields import RequestField, requestfield
from lino.core.fields import Constant, constant
from lino.core.fields import ForeignKey

from lino.utils.babel import BabelCharField, BabelTextField
#~ from lino.core.fields import MethodField

from lino.utils.choosers import chooser

from lino.utils.auth import UserLevels, UserProfiles, UserGroups

#~ from lino.base.utils import UserLevels, UserGroups, UserProfiles

from lino.core.layouts import FormLayout, Panel
from lino.core.layouts import ParamsLayout
#~ from lino.core.layouts import ActionParamsLayout
#~ DetailLayout = InsertLayout = FormLayout

#~ from lino.core.layouts import DetailLayout, InsertLayout


class Module(object):
    pass
    
    
  
PENDING_INJECTS = dict()
PREPARED_MODELS = dict()

def fix_field_cache(model):
    """
    Remove duplicate entries in `_field_cache` to fix Django issue #10808
    """
    cache = []
    field_names = set()
    for f,m in model._meta._field_cache:
        if f.attname not in field_names:
            field_names.add(f.attname)
            cache.append( (f,m) )
    model._meta._field_cache = tuple(cache)
    model._meta._field_name_cache = [x for x, _ in cache]
    #~ logger.info("20130106 fixed field_cache %s (%s)",full_model_name(model),' '.join(field_names))


def on_class_prepared(signal,sender=None,**kw):
    """
    This is Lino's general `class_prepared` handler.
    It does two things:
    
    - Run pending calls to :func:`inject_field` and :func:`update_field`.
    
    - Apply a workaround for Django's ticket 10808.
      In a Diamond inheritance pattern, `_meta._field_cache` contains certain fields twice.    
      So we remove these duplicate fields from `_meta._field_cache`.
      (A better solution would be of course to not collect them.)
    """
    model = sender
    #~ return
    #~ if model is None:
        #~ return 
    k = model._meta.app_label + '.' + model.__name__
    PREPARED_MODELS[k] = model
    #~ logger.info("20120627 on_class_prepared %r = %r",k,model)
    todos = PENDING_INJECTS.pop(k,None)
    if todos is not None:
        for f in todos:
            f(model)
        #~ for k,v in injects.items():
            #~ model.add_to_class(k,v)

    """
    django.db.models.options
    """
    if hasattr(model._meta,'_field_cache'):
        fix_field_cache(model)
    #~ else:
        #~ logger.info("20120905 Could not fix Django issue #10808 for %s",model)


models.signals.class_prepared.connect(on_class_prepared)

def on_analyze_models(): # called from kernel.analyze_models()
    
    if PENDING_INJECTS:
        msg = ''
        for spec,funcs in PENDING_INJECTS.items():
            msg += spec + ': ' 
            #~ msg += '\n'.join([str(dir(func)) for func in funcs])
            #~ msg += '\n'.join([str(func.func_code.co_consts) for func in funcs])
            msg += str(funcs)
        raise Exception("Oops, there are pending injects: %s" % msg)
        #~ logger.warning("pending injects: %s", msg)

    """
    20130106
    now we loop a last time over each model and fill it's _meta._field_cache
    otherwise if some application module used inject_field() on a model which 
    has subclasses, then the new field would not be seen by subclasses
    """
    for model in models.get_models():
        model._meta._fill_fields_cache()
        fix_field_cache(model)

from lino.core.modeltools import is_installed_model_spec

def do_when_prepared(model_spec,todo):
    if model_spec is None:
        return # e.g. inject_field during autodoc when user_model is None
        
    if isinstance(model_spec,basestring):
        if not is_installed_model_spec(model_spec):
            return
        k = model_spec
        model = PREPARED_MODELS.get(k,None)
        if model is None: 
            injects = PENDING_INJECTS.setdefault(k,[])
            injects.append(todo)
            #~ d[name] = field
            #~ logger.info("20120627 Defer inject_field(%r,%r,%r)", model_spec,name,field)
            return
    else:
        model = model_spec
        #~ k = model_spec._meta.app_label + '.' + model_spec.__name__
    todo(model)


def inject_field(model_spec,name,field,doc=None):
    """
    Adds the given field to the given model.
    See also :doc:`/tickets/49`.
    
    Since `inject_field` is usually called at the global level 
    of `models modules`, it cannot know whether the given `model_spec` 
    has already been imported (and its class prepared) or not. 
    That's why it uses Django's `class_prepared` signal to maintain 
    its own list of models.
    """
    #~ logger.info("20130106 inject_field(%r,%s)",model_spec,name)
    if doc:
        field.__doc__ = doc
    def todo(model):
        model.add_to_class(name,field)
        #~ if hasattr(model._meta,'_field_cache'):
        model._meta._fill_fields_cache()
        #~ fix_field_cache(model)
        #~ for m in models_by_base(model):
            #~ if hasattr(m._meta,'_field_cache'):
                #~ m._meta._fill_fields_cache()
                #~ fix_field_cache(m)
        #~ else:
            #~ logger.info("20130106 no need to fix_field_cache after inject_field")

    return do_when_prepared(model_spec,todo)    
    
    

def update_field(model_spec,name,**kw):
    """
    Update some attribute of the specified existing field.
    For example 
    :class:`PersonMixin <lino.modlib.contacts.models.PersonMixin>` 
    defines a field `first_name` which may not be blank.
    If you inherit from 
    :class:`PersonMixin <lino.modlib.contacts.models.PersonMixin>`
    but want `first_name` to be optional::
    
      class MyPerson(contacts.PersonMixin):
        ...
      dd.update_field(MyPerson,'first_name',blank=True)
      
    Or you want to change the label of a field defined in an inherited mixin,
    as done in  :app:`lino.modlib.outbox.models`::
    
      dd.update_field(Mail,'user',verbose_name=_("Sender"))
    
    """
    def todo(model):
        try:
            fld = model._meta.get_field(name)
            #~ fld = model._meta.get_field_by_name(name)[0]
        except FieldDoesNotExist:
            logger.warning("Cannot update unresolved field %s.%s", model,name)
            return
        if fld.model != model:
            raise Exception('20120715 update_field(%s.%s) : %s' % (model,fld,fld.model))
            #~ logger.warning('20120715 update_field(%s.%s) : %s',model,fld,fld.model)
        for k,v in kw.items():
            setattr(fld,k,v)
    return do_when_prepared(model_spec,todo)    
        

def inject_quick_add_buttons(model,name,target):
    """
    Injects a virtual display field `name` into the specified `model`.
    This field will show up to three buttons
    `[New]` `[Show last]` `[Show all]`. 
    `target` is the table that will run these actions.
    It must be a slave of `model`.
    """
    def fn(self,rr):
        return rr.renderer.quick_add_buttons(
          rr.spawn(target,master_instance=self))
    inject_field(model,name,
        VirtualField(DisplayField(
            target.model._meta.verbose_name_plural),fn))
    
def add_user_group(name,label):
    """
    Add a user group to the :class:`UserGroups <lino.core.perms.UserGroups>` 
    choicelist. If a group with that name already exists, add `label` to the 
    existing group.
    """
    #~ logging.info("add_user_group(%s,%s)",name,label)
    #~ print "20120705 add_user_group(%s,%s)" % (name,unicode(label))
    g = UserGroups.items_dict.get(name)
    if g is None:
        UserGroups.add_item(name,label)
    else:
        if g.text != label:
            g.text += " & " + unicode(label)
    
def required(**kw):
    #~ if not kw.has_key('auth'):
        #~ kw.update(auth=True)
    kw.setdefault('auth',True)
    return kw

    