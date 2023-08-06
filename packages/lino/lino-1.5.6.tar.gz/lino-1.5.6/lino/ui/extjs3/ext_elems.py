# -*- coding: UTF-8 -*-
## Copyright 2009-2012 Luc Saffre
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

import logging
logger = logging.getLogger(__name__)

from cgi import escape

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.utils.translation import string_concat
from django.conf import settings

import lino

from lino import dd
from lino.core import dbtables
from lino.core import layouts
from lino.core import fields
from lino.core import actions
from lino.core.actions import Permittable
#~ from lino.core import perms
from lino.utils.ranges import constrain
from lino.utils import jsgen
from lino.utils import curry
from lino.utils import mti
from lino.core import choicelists
from lino.utils.jsgen import py2js, id2js, js_code
from lino.utils import choosers
from lino.utils.auth import make_view_permission_handler

from lino.utils.xmlgen import html as xghtml
E = xghtml.E
from lino.utils.xmlgen import RAW as RAWXML

from lino.ui import requests as ext_requests

EXT_CHAR_WIDTH = 9
EXT_CHAR_HEIGHT = 22

#~ FULLWIDTH = '100%'
#~ FULLHEIGHT = '100%'

FULLWIDTH = '-20' 
FULLHEIGHT = '-10' 


#~ DEFAULT_GC_NAME = 'std'
DEFAULT_GC_NAME = 0

DEFAULT_PADDING = 2

def form_field_name(f):
    if isinstance(f,models.ForeignKey) \
        or (isinstance(f,models.Field) and f.choices): #~ or isinstance(f,dd.LinkedForeignKey):
        return f.name + ext_requests.CHOICES_HIDDEN_SUFFIX
    else:
        return f.name
        

def rpt2url(rpt):
    return '/' + rpt.app_label + '/' + rpt.__name__

#~ def a2btn(a):
    #~ return dict(
      #~ opens_a_slave=a.opens_a_slave,
      #~ handler=js_code("Lino.%s" % a),
      #~ name=a.name,
      #~ label=a.label, # 20111111
    #~ )
      
def py2html(obj,name):
    for n in name.split('.'):
        obj = getattr(obj,n,"N/A")
    if callable(obj):
        obj = obj()
    if getattr(obj, '__iter__', False):
        obj = list(obj)
    return escape(unicode(obj))
    

def get_view_permission(e):
    if isinstance(e,Permittable) and not e.get_view_permission(jsgen._for_user_profile):
        return False
    #~ e.g. pcsw.ClientDetail has a tab "Other", visible only to system admins
    #~ but the "Other" contains a GridElement RolesByPerson which is not per se reserved for system admins.
    #~ js of normal users should not try to call on_master_changed() on it
    parent = e.parent
    while parent is not None:
    #~ if e.parent is not None:
        if isinstance(parent,Permittable) and not parent.get_view_permission(jsgen._for_user_profile):
            return False # bug 3 (bcss_summary) blog/2012/09/27
        parent = parent.parent
    return True

def before_row_edit(panel):
    l = []
    #~ l.append("console.log('before_row_edit',record);")
    master_field = panel.layout_handle.layout._datasource.master_field
    for e in panel.active_children:
        if not get_view_permission(e):
            continue
        #~ if not e.get_view_permission(jsgen._for_user_profile): 
        if isinstance(e,GridElement):
            l.append("%s.on_master_changed();" % e.as_ext())
        #~ elif isinstance(e,PictureElement):
            #~ l.append("this.load_picture_to(%s,record);" % e.as_ext())
        #~ elif isinstance(e,TextFieldElement):
            #~ if e.separate_window:
                #~ l.append("%s.refresh();" % e.as_ext())
        elif isinstance(e,HtmlBoxElement):
            l.append("%s.refresh();" % e.as_ext())
        elif isinstance(e,TextFieldElement):
            if e.format == 'html' and settings.LINO.use_tinymce:
                l.append("%s.refresh();" % e.as_ext())
        elif isinstance(e,FieldElement):
            chooser = choosers.get_for_field(e.field)
            if chooser:
                #~ logger.debug("20100615 %s.%s has chooser", self.layout_handle.layout, e.field.name)
                for f in chooser.context_fields:
                    if master_field and master_field.name == f.name:
                        #~ print 20120603, panel.layout_handle.layout._datasource, e.field.name, f.name
                        #~ l.append("console.log('20120602 before_row_edit',this.get_base_params());")
                        l.append("var bp = this.get_base_params();")
                        #~ ext_requests.URL_PARAM_MASTER_TYPE
                        #~ ext_requests.URL_PARAM_MASTER_KEY
                        l.append("%s.setContextValue('%s',bp['%s']);" % (
                          e.as_ext(),ext_requests.URL_PARAM_MASTER_PK,ext_requests.URL_PARAM_MASTER_PK))
                        l.append("%s.setContextValue('%s',bp['%s']);" % (
                          e.as_ext(),ext_requests.URL_PARAM_MASTER_TYPE,ext_requests.URL_PARAM_MASTER_TYPE))
                    else:
                        #~ l.append("console.log('20110128 before_row_edit',record.data);")
                        l.append(
                            "%s.setContextValue(%r,record ? record.data[%r] : undefined);" % (
                            e.as_ext(),f.name,form_field_name(f)))
    #~ return js_code('function(record){\n  %s\n}' % ('\n  '.join(l)))
    #~ return js_code('function(record){ %s }' % (' '.join(l)))
    return l

class GridColumn(jsgen.Component):
    """
    The component that generates the JS of a grid column.
    """
    declare_type = jsgen.DECLARE_INLINE
    
    def __init__(self,layout_handle,index,editor,**kw):
        """
        editor may be a Panel for columns on a GenericForeignKey
        """
        #~ print 20100515, editor.name, editor.__class__
        #~ assert isinstance(editor,FieldElement), \
            #~ "%s.%s is a %r (expected FieldElement instance)" % (cm.grid.report,editor.name,editor)
        #~ if isinstance(editor,BooleanFieldElement):
            #~ self.editor = None
        #~ else:
        self.editor = editor
        #~ self.value_template = editor.grid_column_template
        kw.update(sortable=True)
        #~ kw.update(submitValue=False) # 20110406
        kw.update(colIndex=index)
        kw.update(editor.get_column_options())
        #~ kw.update(hidden=editor.hidden)
        if editor.hidden:
            kw.update(hidden=True)
        if settings.LINO.use_filterRow:
            if editor.filter_type:
                if index == 0:
                    kw.update(clearFilter=True) # first column used to show clear filter icon in this column
                #~ else:
                    #~ print index, "is not 1"
                kw.update(filterInput=js_code('new Ext.form.TextField()'))
                kw.update(filterOptions=[
                  #~ dict(value='startwith', text='Start With'),
                  #~ dict(value='endwith', text='End With'),
                  dict(value='empty', text='Is empty'),
                  dict(value='notempty', text='Is not empty'),
                  dict(value='contains', text='Contains'),
                  dict(value='doesnotcontain', text='Does not contain')
                ])
              
        if settings.LINO.use_gridfilters and editor.gridfilters_settings:
            # 20121120 last minute
            if isinstance(editor,FieldElement) and not isinstance(editor.field,fields.VirtualField):
                kw.update(filter=editor.gridfilters_settings)
        #~ if isinstance(editor,FieldElement) and editor.field.primary_key:
        if isinstance(editor,FieldElement):
            if settings.LINO.use_quicktips:
                #~ if jsgen._for_user_profile.expert:
                if settings.LINO.show_internal_field_names:
                    ttt = "(%s.%s) " % (layout_handle.layout._datasource,self.editor.field.name)
                    #~ ttt = "(%s) " % self.editor.field.name
                else:
                    ttt = ''
                if self.editor.field.help_text and not "<" in self.editor.field.help_text:
                    #~ GridColumn tooltips don't support html
                    ttt = string_concat(ttt,self.editor.field.help_text)
                if ttt:
                    kw.update(tooltip=ttt)
                
            def fk_renderer(fld,name):
                """
                FK fields are clickable only if their target has a detail view
                """
                rpt = fld.rel.to._lino_default_table
                if rpt.detail_action is not None:
                    if rpt.detail_action.get_view_permission(jsgen._for_user_profile):
                        return "Lino.fk_renderer('%s','Lino.%s')" % (
                          name + ext_requests.CHOICES_HIDDEN_SUFFIX,
                          rpt.detail_action.full_name())
              
            rend = None
            if isinstance(editor.field,models.AutoField):
                rend = 'Lino.id_renderer'
            elif isinstance(editor.field,dd.DisplayField):
                rend = 'Lino.raw_renderer'
            elif isinstance(editor.field,models.TextField):
                rend = 'Lino.text_renderer'
            #~ elif isinstance(editor.field,models.DecimalField):
                #~ rend = 'Lino.hide_zero_renderer'
            #~ elif isinstance(editor.field,dd.LinkedForeignKey):
                #~ rend = "Lino.lfk_renderer(this,'%s')" % \
                  #~ (editor.field.name + ext_requests.CHOICES_HIDDEN_SUFFIX)
            elif isinstance(editor.field,models.ForeignKey):
                rend = fk_renderer(editor.field,editor.field.name)
            elif isinstance(editor.field,fields.VirtualField):
                kw.update(sortable=False)
                if isinstance(editor.field.return_type,models.ForeignKey):
                    rend = fk_renderer(editor.field.return_type,editor.field.name)
                #~ elif isinstance(editor.field.return_type,models.DecimalField):
                    #~ print "20120510 Lino.hide_zero_renderer", editor.field.name
                    #~ rend = 'Lino.hide_zero_renderer'
            #~ elif isinstance(editor.field,dd.GenericForeignKeyIdField):
                #~ rend = "Lino.gfk_renderer()"
            if rend:
                kw.update(renderer=js_code(rend))
            kw.update(editable=editor.editable)
            #~ if editor.editable:
            if editor.editable and not isinstance(editor,BooleanFieldElement):
                kw.update(editor=editor)
            #~ if str(editor.layout_handle.layout._datasource) == 'pcsw.CoachingsByProject':
              #~ if editor.name == 'user':
                #~ print 20120919, editor.field.__class__, editor.field.editable
                #~ print 20120919, editor.field.model, kw['editable']
        else:
            kw.update(editable=False)
        jsgen.Component.__init__(self,editor.name,**kw)
    
        #~ if self.editable:
            #~ editor = self.get_field_options()
        
        
class Toolbar(jsgen.Component):
    value_template = "new Ext.Toolbar(%s)"
    
class ComboBox(jsgen.Component):
    value_template = 'new Ext.form.ComboBox(%s)'
    
class ExtPanel(jsgen.Component): # todo: rename this to Panel, and Panel to PanelElement or sth else
    value_template = "new Ext.Panel(%s)"

#~ class FormPanel(Component): 
    #~ value_template = "new Ext.form.FormPanel(%s)"

class Calendar(jsgen.Component): 
    value_template = "new Lino.CalendarPanel(%s)"
    


NOT_GIVEN = object()

        
class VisibleComponent(jsgen.Component,Permittable):
    vflex = False
    hflex = True
    width = None
    height = None
    preferred_width = 10
    preferred_height = 1
    #flex = None
    
    def __init__(self,name,**kw):
        jsgen.Component.__init__(self,name)
        # install `allow_read` permission handler:
        self.setup(**kw)
        #~ Permittable.__init__(self,False) # name.startswith('cbss'))
        
        #~ def __init__(self,debug_permissions):
        #~ if type(debug_permissions) != bool:
            #~ raise Exception("20120925 %s %r",self,self)
        #~ if self.required is None:
            #~ self.allow_read = curry(make_permission_handler(
                #~ self,self,True,
                #~ debug_permissions),self)
        #~ else:
        self.install_permission_handler()
        
    def install_permission_handler(self):
        #~ if self.name == 'newcomers_left': # required.has_key('user_groups'):
            #~ logger.info("20121130 install_permission_handler() %s %s",self,self.required)
            #~ if self.required.get('user_groups') ==  'integ':
                #~ raise Exception("20121130")
        self.allow_read = curry(make_view_permission_handler(
            self,True,
            self.debug_permissions,
            **self.required),self)
            
    def get_view_permission(self,profile):
        #~ if self.name == 'newcomers_left': # required.has_key('user_groups'):
            #~ logger.info("20121130 get_view_permission() %s %s",self,self.required)
        return self.allow_read(profile)
        
    def setup(self,width=None,height=None,label=None,
        preferred_width=None,
        required=NOT_GIVEN,
        **kw):
        self.value.update(kw)
        #~ jsgen.Component.__init__(self,name,**kw)
        if preferred_width is not None:
            self.preferred_width = preferred_width
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if label is not None:
            self.label = label
        if required is not NOT_GIVEN:
            self.required = required
            #~ if self.name == 'newcomers_left': # required.has_key('user_groups'):
                #~ logger.info("20121130 setup() %s %s",self,self.required)
    

    def __str__(self):
        "This shows how elements are specified"
        name = jsgen.Component.__str__(self)
        if self.width is None:
            return name
        if self.height is None:
            return name + ":%d" % self.width
        return name + ":%dx%d" % (self.width,self.height)
        
    def unused__repr__(self):
        return str(self)
        
    def pprint(self,level=0):
        return ("  " * level) + str(self)
        
    def walk(self):
        yield self
        
        
    def debug_lines(self):
        sep = u"</td><td>"
        cols = """ext_name name parent label __class__.__name__ 
        elements js_value
        label_align vertical width preferred_width height 
        preferred_height vflex""".split()
        yield '<tr><td>' + sep.join(cols) + '</td></tr>'
        for e in self.walk():
            yield '<tr><td>'+sep.join([py2html(e,n) for n in cols]) +'</td></tr>'
            
    def unused_has_field(self,fld):
        for de in self.walk():
            if isinstance(de,FieldElement) and de.field is fld:
                return True
        return False
        
        
class LayoutElement(VisibleComponent):
    stored = False
    ext_name = None
    ext_suffix = ""
    #~ data_type = None 
    filter_type = None
    gridfilters_settings = None
    parent = None # will be set by Container
    
    label = None
    label_width = 0 
    editable = False
    sortable = False
    xtype = None # set by subclasses
    #~ grid_column_template = "new Ext.grid.Column(%s)"
    collapsible = False
    hidden = False
    active_child = True
    refers_to_ww = False
    
    def __init__(self,layout_handle,name,**kw):
        #logger.debug("LayoutElement.__init__(%r,%r)", layout_handle.layout,name)
        #self.parent = parent
        #~ name = layout_handle.layout._actor_name + '_' + name
        assert isinstance(layout_handle,layouts.LayoutHandle)
        opts  = layout_handle.layout._element_options.get(name,{})
        for k,v in opts.items():
            if not hasattr(self,k):
                raise Exception("%s has no attribute %s" % (self,k))
            setattr(self,k,v)
        
        if not kw.has_key('required'): # new since 20121130. theoretically better
            required = dict()
            required.update(layout_handle.layout._datasource.required)
            required.update(self.required)
            kw.update(required=required)
        #~ else:
            #~ logger.info("20121130 %s %s",name,kw)
          
        VisibleComponent.__init__(self,name,**kw)
        #~ if opts:
            #~ print "20120525 apply _element_options", opts, 'to', self.__class__, self
        self.layout_handle = layout_handle
        #~ if layout_handle is not None:
        #~ layout_handle.setup_element(self)
        #~ if str(self.layout_handle.layout._datasource) == 'lino.Home':
            #~ logger.info("20120927 LayoutElement.__init__ %r required is %s, kw was %s, opts was %s",
              #~ self,self.required,kw,opts)

    #~ def submit_fields(self):
        #~ return []
        
    def add_requirements(self,**kw):
        super(LayoutElement,self).add_requirements(**kw)
        self.install_permission_handler()
        
    def loosen_requirements(self,actor):
        """
        Retain only those requirements of obj which are also in actor.
        """
        if self.layout_handle.layout._datasource == actor:
            return 
        #~ kw = actor.required
        new = dict()
        loosened = set()
        for k,v in self.required.items():
            if actor.required.has_key(k):
                if actor.required[k] < v:
                    loosened.add(k)
                    self.required[k] = actor.required[k]
            else:
                loosened.add(k)
                del self.required[k]
            
        #~ for k,v in actor.required.items():
            #~ new[k] = v
            #~ if k in self.required:
                #~ if self.required[k] > v:
                    #~ removed.add(k)
            #~ else:
                #~ removed.add(k)
        if loosened:
            #~ self.required = new
            self.install_permission_handler()
            #~ logger.info("20121116 loosened requirements %s using %s by %s",,self.layout_handle.layout,actor)
            #~ logger.info("20121116 %s uses %s loosening requirements %s",actor,self.layout_handle.layout,','.join(loosened))
            #~ if self.layout_handle.layout._datasource != actor:
                #~ raise Exception("%s != %s" % (self.layout_handle.layout._datasource,actor))
            #~ for e in self.elements:
                #~ if isinstance(e,Container):
                    #~ e.loosen_requirements(actor)
        #~ elif self.layout_handle.layout._datasource != actor:
            #~ logger.info("20121116 %s uses %s with same requirements",actor,self.layout_handle.layout)
            
        
        
    def __repr__(self):
        return "<%s %s in %s>" % (self.__class__.__name__,self.name,self.layout_handle.layout)
        

    def get_property(self,name):
        v = getattr(self,name,None)
        if self.parent is None or v is not None:
            return v
        return self.parent.get_property(name)
        
    def get_column_options(self,**kw):
        return kw
        
    def set_parent(self,parent):
        #~ if self.parent is not None:
            #~ raise Exception("%s : parent is already %s, cannot set it to %s" % (self,self.parent,parent))
        self.parent = parent
        #~ if isinstance(parent,FieldSetPanel):
            #~ self.label = None
            #~ self.update(label = None)
        if self.label:
            if isinstance(parent,Panel):
                if parent.label_align == layouts.LABEL_ALIGN_LEFT:
                    self.preferred_width += len(self.label)

    def ext_options(self,**kw):
        if isinstance(self.parent,TabPanel):
            if not self.label:
                raise Exception(
                    "Item %s of tabbed %s has no label!" % (
                    self,self.layout_handle))
            #~ if self.value_template != 'new Lino.VBorderPanel(%s)':
            #~ if self.value_template == "%s":
            #~ if self.value_template == "new Ext.Container":
            #~ if self.value_template == "new Ext.Container(%s)":
                #~ self.value_template = "new Ext.Panel(%s)"
            #~ else:
                #~ logger.info("20120217 value_template %s",self.value_template)
            self.update(title=self.label)
            self.update(listeners=dict(activate=js_code("Lino.on_tab_activate")))
        if self.xtype is not None:
            self.update(xtype=self.xtype)
        if self.collapsible:
            self.update(collapsible=True)
        kw = VisibleComponent.ext_options(self,**kw)
        return kw

    def as_plain_html(self,ar,obj):
        yield E.p("cannot handle %s" % self.__class__)
            


class ConstantElement(LayoutElement):
    declare_type = jsgen.DECLARE_INLINE
    #declare_type = jsgen.DECLARE_THIS
    #~ declare_type = jsgen.DECLARE_VAR
    xtype = 'label'
    vflex = True
    
    def __init__(self,lh,fld,**kw):
        kw.update(html=fld.text_fn(lh.layout._datasource,lh.ui))
        #~ kw.update(html=fld.text)
        #~ kw.update(autoHeight=True)
        LayoutElement.__init__(self,lh,fld.name,**kw)
        #~ self.text = text

    #~ def ext_options(self,**kw):
        #~ kw = LayoutElement.ext_options(self,**kw)
        #~ kw.update(html=self.text.text)
        #~ return kw
        
    def as_plain_html(self,ar,obj):
        #~ return RAWXML(self.value.get('html'))
        return self.value.get('html')
        
        

class Spacer(LayoutElement):
    declare_type = jsgen.DECLARE_INLINE
    #xtype = 'label'
    value_template = "new Ext.Spacer(%s)"
    
        
        
        
class FieldElement(LayoutElement):
    #~ declare_type = jsgen.DECLARE_INLINE
    #~ declare_type = jsgen.DECLARE_THIS
    declare_type = jsgen.DECLARE_VAR
    stored = True
    filter_type = None # 'auto'
    active_change_event = 'change'
    #declaration_order = 3
    #~ ext_suffix = "_field"
    
    def __init__(self,layout_handle,field,**kw):
        if not hasattr(field,'name'):
            raise Exception("Field %s.%s has no name!" % (layout_handle,field))
        assert field.name, Exception("field %r has no name!" % field)
        self.field = field
        self.editable = field.editable # and not field.primary_key
        
        if not isinstance(layout_handle.layout,layouts.ListLayout):
            #~ help_text = getattr(self.field,'help_text',None):
            if settings.LINO.use_quicktips:
                if settings.LINO.show_internal_field_names:
                    ttt = "(%s.%s) " % (layout_handle.layout._datasource,self.field.name)
                else:
                    ttt = ''
                if self.field.help_text:
                    ttt = string_concat(ttt,self.field.help_text)
                if ttt:
                    #~ kw.update(qtip=self.field.help_text)
                    #~ kw.update(toolTipText=self.field.help_text)
                    #~ kw.update(tooltip=self.field.help_text)
                    kw.update(listeners=dict(render=js_code(
                      "Lino.quicktip_renderer(%s,%s)" % (
                          py2js(self.field.verbose_name),
                          py2js(ttt)))
                    ))
            

        #~ http://www.rowlands-bcs.com/extjs/tips/tooltips-form-fields
        #~ if self.field.__doc__:
            #~ kw.update(toolTipText=self.field.__doc__)
        #~ label = field.verbose_name
        #~ if not self.field.blank:
            #~ label = string_concat('<b>',label,'</b>')
            #~ label = string_concat(label,' [*]')
            
        #~ kw.update(style=dict(padding=DEFAULT_PADDING))
        #~ kw.update(style=dict(marginLeft=DEFAULT_PADDING))
        #~ kw.update(style='padding: 10px')
        #~ logger.info("20120931 %s %s",layout_handle,field.name)
        
        kw.setdefault('label',field.verbose_name)
        
        #~ kw.setdefault('label',string_concat('<b>',field.verbose_name,'</b>'))
        #~ kw.setdefault('label',
          #~ string_concat('<span class="ttdef"><a class="tooltip" href="#">',
            #~ field.verbose_name,
            #~ '<span class="classic">This is a test...</span></a></span>'))
        #~ kw.setdefault('label',
          #~ string_concat('<div class="ttdef"><a class="tooltip" href="#">',
            #~ field.verbose_name,
            #~ '<span class="classic">This is a test...</span></a></div>'))
            
        self.add_default_value(kw)
        
        LayoutElement.__init__(self,layout_handle,field.name,**kw)

    def as_plain_html(self,ar,obj):
        value = self.field.value_from_object(obj)
        text = unicode(value)
        if not text: text = " "
        #~ yield E.p(unicode(elem.field.verbose_name),':',E.br(),E.b(text))
        yield E.label(unicode(self.field.verbose_name))
        yield E.input(type="text",value=text)
        #~ yield E.p(unicode(elem.field.verbose_name),':',E.br(),E.b(text))
            
    def cell_html(self,ui,row):
        return getattr(row,self.field.name)
            
    def add_default_value(self,kw):
        if self.field.has_default():
            dv = self.field.default
            if callable(dv):
                return 
                #~ dv = dv()
            kw.update(value=dv)
            
        
    def get_column_options(self,**kw):
        #~ raise "get_column_options() %s" % self.__class__
        #~ kw.update(xtype='gridcolumn')
        #~ kw.update(dataIndex=self.field.name)
        kw.update(dataIndex=self.name)
        #~ if self.label is None:
            #~ kw.update(header=self.field.name)
        #~ else:
        #~ kw.update(header=unicode(self.label or self.name))
        kw.update(header=self.label or self.name)
        if not self.editable:
            kw.update(editable=False)
        if not self.sortable:
            kw.update(sortable=False)
        w = self.width or self.preferred_width
        #~ kw.update(width=w*EXT_CHAR_WIDTH)
        kw.update(width=js_code("Lino.chars2width(%d)" % w))
        return kw    
        
        
    def get_field_options(self,**kw):
        if self.xtype:
            kw.update(xtype=self.xtype)
        
        # When used as editor of an EditorGridPanel, don't set the name attribute
        # because it is not needed for grids and might conflict with fields of a 
        # surronding detail form. See ticket #38 (:doc:`/blog/2011/0408`).
        # Also don't set a label then.
        if not isinstance(self.layout_handle.layout,layouts.ListLayout):
            kw.update(name=self.field.name)
            if self.label:
                label = self.label
                if self.field.help_text:
                    if settings.LINO.use_css_tooltips:
                        label = string_concat(
                          '<a class="tooltip" href="#">',
                          label,
                          '<span class="classic">',
                          self.field.help_text,
                          '</span></a>')
                    elif settings.LINO.use_quicktips:
                        label = string_concat(
                          '<span style="border-bottom: 1px dotted #000000;">',
                          label,
                          '</span>')
            
                kw.update(fieldLabel=label)
        if self.editable:
            if not self.field.blank:
                kw.update(allowBlank=False)
            kw.update(selectOnFocus=True)
        else:
            kw.update(disabled=True)
            #~ kw.update(readOnly=True)
        return kw
        
    def ext_options(self,**kw):
        kw = LayoutElement.ext_options(self,**kw)
        kw.update(self.get_field_options())
        return kw
    
        
class TextFieldElement(FieldElement):
    #~ xtype = 'textarea'
    filter_type = 'string'
    gridfilters_settings = dict(type='string')
    vflex = True
    value_template = "new Ext.form.TextArea(%s)"
    xtype = None
    #width = 60
    preferred_width = 60
    preferred_height = 5
    #collapsible = True
    separate_window = False
    active_child = False
    format = 'plain'
    def __init__(self,layout_handle,field,**kw):
        self.format = getattr(field,'textfield_format',None) \
            or settings.LINO.textfield_format
        if self.format == 'html':
            if settings.LINO.use_tinymce:
                self.value_template = "new Lino.RichTextPanel(%s)"
                self.active_child = True
                #~ if self.label:
                    #~ kw.update(title=unicode(self.label))
                self.separate_window = True
                # we don't call FieldElement.__init__ but do almost the same:
                self.field = field
                self.editable = field.editable # and not field.primary_key
                #~ 20111126 kw.update(ls_url=rpt2url(layout_handle.rh.report))
                #~ kw.update(master_panel=js_code("this"))
                kw.update(containing_panel=js_code("this"))
                #~ kw.update(title=unicode(field.verbose_name)) 20111111
                kw.update(title=field.verbose_name)
                #~ kw.update(tinymce_options=dict(
                    #~ template_external_list_url=layout_handle.ui.build_url('templates',layout_handle.rh.report.app_label,layout_handle.rh.report.name)
                  #~ template_templates=[
                    #~ dict(title="Editor Details",
                        #~ src="editor_details.htm",
                        #~ description="Adds Editor Name and Staff ID")]
                #~ ))
                #~ LayoutElement.__init__(self,layout_handle,varname_field(field),label=unicode(field.verbose_name),**kw)
                #~ LayoutElement.__init__(self,layout_handle,field.name,label=unicode(field.verbose_name),**kw)
                return LayoutElement.__init__(self,layout_handle,field.name,**kw)
            else:
                self.value_template = "new Ext.form.HtmlEditor(%s)"
                if settings.LINO.use_vinylfox:
                    kw.update(plugins=js_code('Lino.VinylFoxPlugins()'))
        elif self.format == 'plain':
            kw.update(
              growMax=2000,
              #~ defaultAutoCreate = dict(
                #~ tag="textarea",
                #~ autocomplete="off"
              #~ )
            )
        else:
            raise Exception(
                "Invalid textfield format %r for field %s.%s" % (
                self.format,field.model.__name__,field.name))
        FieldElement.__init__(self,layout_handle,field,**kw)
        
    def as_plain_html(self,ar,obj):
        value = self.field.value_from_object(obj)
        text = unicode(value)
        if not text: text = " "
        #~ yield E.p(unicode(elem.field.verbose_name),':',E.br(),E.b(text))
        yield E.label(unicode(self.field.verbose_name))
        yield E.textarea(value=text,rows=str(self.preferred_height))
        
class CharFieldElement(FieldElement):
    filter_type = 'string'
    gridfilters_settings = dict(type='string')
    value_template = "new Ext.form.TextField(%s)"
    sortable = True
    xtype = None
  
    def __init__(self,*args,**kw):
        FieldElement.__init__(self,*args,**kw)
        self.preferred_width = 1 + min(20,max(3,self.field.max_length))
            
    def get_field_options(self,**kw):
        kw = FieldElement.get_field_options(self,**kw)
        kw.update(maxLength=self.field.max_length)
        if self.field.max_length is not None:
            if self.field.max_length <= 10:
                kw.update(boxMinWidth=js_code('Lino.chars2width(%d)' % self.field.max_length))
        
        #~ kw.update(style=dict(padding=DEFAULT_PADDING))
        #~ kw.update(margins='10px')
        return kw
        
        
class PasswordFieldElement(CharFieldElement):
    def get_field_options(self,**kw):
        kw = super(PasswordFieldElement,self).get_field_options(**kw)
        kw.update(inputType='password')
        return kw
    
class FileFieldElement(CharFieldElement):
    #~ xtype = 'fileuploadfield'
    #~ value_template = "new Lino.FileField(%s)"
    value_template = "Lino.file_field_handler(this,%s)"
    #~ value_template = "%s"
    
    #~ def __init__(self,layout_handle,*args,**kw):
        #~ CharFieldElement.__init__(self,layout_handle,*args,**kw)
        #~ layout_handle.has_upload = True
        
    #~ def get_field_options(self,**kw):
        #~ kw = CharFieldElement.get_field_options(self,**kw)
        #~ kw.update(emptyText=_('Select a document to upload...'))
        #~ # kw.update(buttonCfg=dict(iconCls='upload-icon'))
        #~ return kw
    
class ComboFieldElement(FieldElement):
    #~ value_template = "new Ext.form.ComboBox(%s)"        
    sortable = True
    xtype = None
    filter_type = 'string'
    gridfilters_settings = dict(type='string')
    
    def get_field_options(self,**kw):
        kw = FieldElement.get_field_options(self,**kw)
        # When used as editor of an EditorGridPanel, don't set the name attribute
        # because it is not needed for grids and might conflict with fields of a 
        # surronding detail form. See ticket #38 (`/blog/2011/0408`).
        # Also, Comboboxes with simple values may never have a hiddenName option.
        if not isinstance(self.layout_handle.layout,layouts.ListLayout) \
            and not isinstance(self,SimpleRemoteComboFieldElement):
            kw.update(hiddenName=self.field.name+ext_requests.CHOICES_HIDDEN_SUFFIX)
        return kw
      
class ChoicesFieldElement(ComboFieldElement):
    value_template = "new Lino.ChoicesFieldElement(%s)"
  
    def get_field_options(self,**kw):
        kw = ComboFieldElement.get_field_options(self,**kw)
        kw.update(store=tuple(self.field.choices))
        #~ kw.update(hiddenName=self.field.name+ext_requests.CHOICES_HIDDEN_SUFFIX)
        return kw
        
class ChoiceListFieldElement(ChoicesFieldElement):
    def get_field_options(self,**kw):
        kw = ComboFieldElement.get_field_options(self,**kw)
        #~ kw.update(store=js_code('Lino.%s.choices' % self.field.choicelist.actor_id))
        kw.update(store=js_code('Lino.%s' % self.field.choicelist.actor_id))
        return kw

class RemoteComboFieldElement(ComboFieldElement):
    value_template = "new Lino.RemoteComboFieldElement(%s)"
  
    def store_options(self,**kw):
        #~ kw.update(baseParams=js_code('this.get_base_params()')) # 20120202
        if self.editable:
            url = self.layout_handle.get_choices_url(self.field,**kw)
            #~ url = self.layout_handle.ui.build_url("choices",
                #~ self.layout_handle.layout._datasource.app_label,
                #~ self.layout_handle.layout._datasource.__name__,
                #~ self.field.name,**kw)
            proxy = dict(url=url,method='GET')
            kw.update(proxy=js_code("new Ext.data.HttpProxy(%s)" % py2js(proxy)))
        # a JsonStore without explicit proxy sometimes used method POST
        return kw
      
    def get_field_options(self,**kw):
        kw = ComboFieldElement.get_field_options(self,**kw)
        sto = self.store_options()
        #print repr(sto)
        kw.update(store=js_code("new Lino.ComplexRemoteComboStore(%s)" % py2js(sto)))
        return kw
        
class SimpleRemoteComboFieldElement(RemoteComboFieldElement):
    value_template = "new Lino.SimpleRemoteComboFieldElement(%s)"
    #~ def get_field_options(self,**kw):
        #~ todo : store
        #~ # Do never add a hiddenName
        #~ return FieldElement.get_field_options(self,**kw)
    
  
class ComplexRemoteComboFieldElement(RemoteComboFieldElement):
    #~ value_template = "new Lino.ComplexRemoteComboFieldElement(%s)"
        
    def unused_get_field_options(self,**kw):
        kw = RemoteComboFieldElement.get_field_options(self,**kw)
        kw.update(hiddenName=self.field.name+ext_requests.CHOICES_HIDDEN_SUFFIX)
        return kw
        
        
#~ class LinkedForeignKeyElement(ComplexRemoteComboFieldElement):
    #~ pass
  
class ForeignKeyElement(ComplexRemoteComboFieldElement):
  
    preferred_width = 20
    
    def __init__(self,layout_handle,field,**kw):
    #~ def __init__(self,*args,**kw):
        #~ print 20100903,repr(self.field.rel.to)
        #~ assert issubclass(self.field.rel.to,dd.Model), "%r is not a model" % self.field.rel.to
        #~ pw = getattr(field.rel.to,'_lino_preferred_width',None)
        pw = field.rel.to.preferred_foreignkey_width
        if pw is not None:
            kw.setdefault('preferred_width',pw)
            #~ kw.update(preferred_width=pw)
        self.actor = dbtables.get_model_report(field.rel.to)
        #~ if self.actor.model is None:
            #~ raise Exception("20120621 ForeignKeyElement for %s.%s" % (self.actor,field))
        a = self.actor.detail_action
        if a is not None:
            if not isinstance(layout_handle.layout,layouts.ListLayout):
                self.value_template = "new Lino.TwinCombo(%s)"
                kw.update(onTrigger2Click=js_code(
                    "function(e){ Lino.show_fk_detail(this,Lino.%s)}" % a.full_name()))
                    #~ "Lino.show_fk_detail_handler(this,Lino.%s)}" % a))
        FieldElement.__init__(self,layout_handle,field,**kw)
      
    #~ def submit_fields(self):
        #~ return [self.field.name,self.field.name+ext_requests.CHOICES_HIDDEN_SUFFIX]
        
        
    def get_field_options(self,**kw):
        kw = super(ForeignKeyElement,self).get_field_options(**kw)
        kw.update(pageSize=self.actor.page_length)
        if self.actor.model is not None:
            kw.update(emptyText=_('Select a %s...') % self.actor.model._meta.verbose_name)
        return kw

    def cell_html(self,ui,row):
        obj = getattr(row,self.field.name)
        if obj is None:
            return ''
        return ui.href_to(obj)


class TimeFieldElement(FieldElement):
    value_template = "new Lino.TimeField(%s)"
    #~ xtype = 'timefield'
    #~ data_type = 'time' # for store column
    sortable = True
    preferred_width = 8
    #~ filter_type = 'time'
    
  
class DateTimeFieldElement(FieldElement):
    #~ value_template = "new Lino.DateTimeField(%s)"
    value_template = "new Ext.form.DisplayField(%s)"
    #~ data_type = 'date' # for store column
    sortable = True
    preferred_width = 16
    #~ filter_type = 'date'
    
    def __init__(self,layout_handle,field,**kw):
        if self.editable:
            self.value_template = "new Lino.DateTimeField(%s)"
        else:
            kw.update(value="<br>")
        FieldElement.__init__(self,layout_handle,field,**kw)
    
class DatePickerFieldElement(FieldElement):
    value_template = "new Lino.DatePickerField(%s)"
    def get_column_options(self,**kw):
        raise Exception("not allowed in grid")
    
class DateFieldElement(FieldElement):
    if settings.LINO.use_spinner:
        raise Exception("20130114")
        value_template = "new Lino.SpinnerDateField(%s)"
    else:
        value_template = "new Lino.DateField(%s)"
        #~ value_template = "new Lino.DatePickerField(%s)"
    #~ xtype = 'datefield'
    #~ data_type = 'date' # for store column
    sortable = True
    preferred_width = 8
    filter_type = 'date'
    gridfilters_settings = dict(type='date',dateFormat=settings.LINO.date_format_extjs)
    # todo: DateFieldElement.preferred_width should be computed from Report.date_format
    #~ grid_column_template = "new Ext.grid.DateColumn(%s)"
    
    #~ def __init__(self,layout_handle,field,**kw):
        #~ if False: # getattr(field,'picker',False):
            #~ self.value_template = "new Lino.DatePickerField(%s)"
        #~ FieldElement.__init__(self,layout_handle,field,**kw)
        
    #~ def get_field_options(self,**kw):
        #~ kw = FieldElement.get_field_options(self,**kw)
        #~ kw.update(format=self.layout_handle.rh.actor.date_format)
        #~ return kw
        
    def get_column_options(self,**kw):
        kw = FieldElement.get_column_options(self,**kw)
        kw.update(xtype='datecolumn')
        #~ kw.update(format=self.layout_handle.rh.actor.date_format)
        kw.update(format=settings.LINO.date_format_extjs)
        #~ kw.update(boxMinWidth=js_code('Lino.chars2width(%d)' % 12)) # experimental value. 
        return kw
    
class MonthFieldElement(DateFieldElement):
    def get_field_options(self,**kw):
        kw = DateFieldElement.get_field_options(self,**kw)
        kw.update(format='m/Y')
        kw.update(plugins='monthPickerPlugin')
        return kw
        
    
class URLFieldElement(CharFieldElement):
    sortable = True
    preferred_width = 40
    value_template = "new Lino.URLField(%s)"
    
    #~ def get_field_options(self,**kw):
        #~ kw = FieldElement.get_field_options(self,**kw)
        #~ kw.update(vtype='url') #,vtypeText=
        #~ return kw
        
    
class IntegerFieldElement(FieldElement):
    filter_type = 'numeric'
    gridfilters_settings = dict(type='numeric')
    #~ xtype = 'numberfield'
    xtype = None
    sortable = True
    preferred_width = 5
    #~ data_type = 'int' 
    value_template = "new Ext.form.NumberField(%s)"

class IncompleteDateFieldElement(CharFieldElement):
    """
    Widget for :class:`lino.core.fields.IncompleteDate` fields.
    """
    preferred_width = 10
    value_template = "new Lino.IncompleteDateField(%s)"
    
    #~ def __init__(self,*args,**kw):
        #~ FieldElement.__init__(self,*args,**kw)
        
    def get_field_options(self,**kw):
        # skip CharFieldElement.get_field_options because 
        # boxMinWidth and maxLength are set by Lino.IncompleteDateField
        kw = FieldElement.get_field_options(self,**kw)
        #~ kw.update(maxLength=10)
        return kw
        


class DecimalFieldElement(FieldElement):
    #~ value_template = "new Ext.form.NumberField(%s)"
    filter_type = 'numeric'
    gridfilters_settings = dict(type='numeric')
    xtype = 'numberfield'
    sortable = True
    #~ data_type = 'float' 
    #~ grid_column_template = "new Ext.grid.NumberColumn(%s)"
    
    def __init__(self,*args,**kw):
        FieldElement.__init__(self,*args,**kw)
        self.preferred_width = max(5,self.field.max_digits) \
                + self.field.decimal_places
                
    def get_field_options(self,**kw):
        kw = FieldElement.get_field_options(self,**kw)
        if self.field.decimal_places:
            kw.update(decimalPrecision=self.field.decimal_places)
            kw.update(decimalSeparator=settings.LINO.decimal_separator)
        else:
            kw.update(allowDecimals=False)
        return kw
        
    #~ def get_column_options(self,**kw):
        #~ kw = FieldElement.get_column_options(self,**kw)
        #~ kw.update(xtype='numbercolumn')
        #~ kw.update(align='right')
        #~ if settings.LINO.decimal_separator == ',':
            #~ fmt = "0.000"
            #~ if self.field.decimal_places > 0:
                #~ fmt += ',' + ("0" * self.field.decimal_places)
                #~ fmt += "/i"
        #~ elif settings.LINO.decimal_separator == '.':
            #~ fmt = "0,000"
            #~ if self.field.decimal_places > 0:
                #~ fmt += '.' + ("0" * self.field.decimal_places)
        #~ kw.update(format=fmt)
        #~ return kw
        
    def get_column_options(self,**kw):
        kw = FieldElement.get_column_options(self,**kw)
        kw.update(xtype='numbercolumn')
        kw.update(align='right')
        #~ if settings.LINO.decimal_group_separator:
            #~ fmt = '0' + settings.LINO.decimal_group_separator + '000'
        #~ else:
        # Ext.utils.format.number() is not able to specify ' ' as group separator,
        # so we don't use grouping at all.
        fmt = '0'
        if self.field.decimal_places > 0:
            fmt += settings.LINO.decimal_separator + ("0" * self.field.decimal_places)
        if settings.LINO.decimal_separator == ',':
            fmt += "/i"
        kw.update(format=fmt)
        return kw
        
class DisplayElement(FieldElement):
    """
    ExtJS element to be used for :class:`DisplayFields <lino.core.fields.DisplayField>`.
    """
    preferred_width = 30
    preferred_height = 3
    ext_suffix = "_disp"
    #~ declare_type = jsgen.DECLARE_THIS
    declare_type = jsgen.DECLARE_VAR
    value_template = "new Ext.form.DisplayField(%s)"
    
    def __init__(self,*args,**kw):
        kw.setdefault('value','<br/>') # see blog/2012/0527
        kw.update(always_enabled=True)
        FieldElement.__init__(self,*args,**kw)
        if self.field.max_length:
            self.preferred_width = self.field.max_length
    
class BooleanDisplayElement(DisplayElement):
    preferred_width = 20
    preferred_height = 1
    
                
class BooleanFieldElement(FieldElement):
  
    value_template = "new Ext.form.Checkbox(%s)"
    #~ xtype = 'checkbox'
    #~ data_type = 'boolean' 
    filter_type = 'boolean'
    gridfilters_settings = dict(type='boolean')
    #~ grid_column_template = "new Ext.grid.BooleanColumn(%s)"
    #~ def __init__(self,*args,**kw):
        #~ FieldElement.__init__(self,*args,**kw)
    #~ active_change_event = 'check'
        
    def set_parent(self,parent):
        FieldElement.set_parent(self,parent)
        #~ if isinstance(parent,Panel) and parent.hideCheckBoxLabels:
        if parent.hideCheckBoxLabels:
            self.update(hideLabel=True)
            
    def add_default_value(self,kw):
        if self.field.has_default():
            dv = self.field.default
            if callable(dv):
                return 
                #~ dv = dv()
            kw.update(checked=dv)
            #~ self.remove('value')

    def get_field_options(self,**kw):
        kw = FieldElement.get_field_options(self,**kw)
        if not isinstance(self.layout_handle.layout,layouts.ListLayout):
            if kw.has_key('fieldLabel'):
                del kw['fieldLabel']
            #~ kw.update(hideLabel=True)
            
            label = self.label
            #~ if isinstance(self.field,mti.EnableChild):
                #~ m = self.field.child_model
                #~ url = self.layout_handle.rh.ui.build_url('api',m._meta.app_label,m.__name__)
                #~ js = "Lino.show_mti_child('%s','%s')" % (self.field.name,url)
                #~ label += """ (<a href="javascript:%s">%s</a>)""" % (js,_("show"))
            if isinstance(self.field,mti.EnableChild):
                rpt = self.field.child_model._lino_default_table
                if rpt.detail_action is not None:
                    js = "Lino.show_mti_child('%s',Lino.%s)" % (
                      self.field.name,
                      rpt.detail_action.full_name())
                    label += """ (<a href="javascript:%s">%s</a>)""" % (
                      js,_("show"))
                
        #~ self.verbose_name = \
            #~ 'is a <a href="javascript:Lino.enable_child_label()">%s</a>' % self.field.child_model.__name__
            #~ 'is a <a href="foo">[%s]</a>' % self.child_model._meta.verbose_name
                
            kw.update(boxLabel=label)
        
        return kw
        
    def get_column_options(self,**kw):
        kw = FieldElement.get_column_options(self,**kw)
        kw.update(xtype='checkcolumn')
        return kw
        
    def get_from_form(self,instance,values):
        """
        standard HTML submits checkboxes of a form only when they are checked.
        So if the field is not contained in values, we take False as value.
        """
        instance[self.field.name] = values.get(self.field.name,False)



class GenericForeignKeyElement(DisplayElement):
    """
    A :class:`DisplayElement` specially adapted to a :term:`GFK` field.
    """
    def __init__(self,layout_handle,field,**kw):
        #~ if not hasattr(field,'name'):
            #~ raise Exception("Field %s.%s has no name!" % (layout_handle.rh.actor,field))
        #~ assert field.name, Exception("field %r has no name!" % field)
        self.field = field
        self.editable = False
        kw.update(label=getattr(field,'verbose_name',None) or field.name)
        #~ kw.update(label=field.verbose_name) 
        LayoutElement.__init__(self,layout_handle,field.name,**kw)
  
    def add_default_value(self,kw):
        pass
    
    
class RecurrenceElement(DisplayElement):
    value_template = "new Ext.ensible.cal.RecurrenceField(%s)"
    
class HtmlBoxElement(DisplayElement):
    """
    Element that renders to a `Lino.HtmlBoxPanel`.
    """
    ext_suffix = "_htmlbox"
    #~ declare_type = jsgen.DECLARE_VAR
    value_template = "new Lino.HtmlBoxPanel(%s)"
    preferred_height = 5
    vflex = True
    filter_type = 'string'
    gridfilters_settings = dict(type='string')
    refers_to_ww = True
    
    #~ def __init__(self,layout_handle,name,action,**kw):
        #~ kw.update(plugins=js_code('Lino.HtmlBoxPlugin'))
        #~ LayoutElement.__init__(self,layout_handle,name,**kw)
        
    def get_field_options(self,**kw):
        kw.update(master_panel=js_code("this"))
        kw.update(name=self.field.name)
        kw.update(containing_panel=js_code("this"))
        kw.update(layout='fit')
        #~ kw.update(autoScroll=True)
        
        # hide horizontal scrollbar      
        # for this trick thanks to Vladimir 
        # <http://forums.ext.net/showthread.php?1513-CLOSED-Autoscroll-on-ext-panel>
        #~ kw.update(bodyStyle="overflow-x:hidden !important;")
        kw.update(bodyStyle="overflow-x:hidden")
        
        #~ if self.field.drop_zone: # testing with drop_zone 'FooBar'
            #~ kw.update(listeners=dict(render=js_code('initialize%sDropZone' % self.field.drop_zone)))
        kw.update(items=js_code("new Ext.BoxComponent({autoScroll:true})"))
        #~ kw.update(items=js_code("new Ext.BoxComponent({})"))
        if self.label:
            #~ kw.update(title=unicode(self.label)) 20111111
            kw.update(title=self.label)
        #~ if self.field.bbar is not None:
            #~ kw.update(ls_bbar_actions=self.field.bbar)
        return kw
        


class Container(LayoutElement):
    """
    Base class for Layout Elements that can contain other Layout Elements:
    :class:`Panel`,
    :class:`TabPanel`,
    :class:`FormPanel`,
    :class:`GridPanel`
    """
    vertical = False
    hpad = 1
    is_fieldset = False
    #~ xtype = 'container'
    value_template = "new Ext.Container(%s)"
    hideCheckBoxLabels = True
    label_align = layouts.LABEL_ALIGN_TOP
    
    #declare_type = jsgen.DECLARE_INLINE
    declare_type = jsgen.DECLARE_VAR
    #~ declare_type = jsgen.DECLARE_THIS
    #~ declare_type = jsgen.DECLARE_THIS
    
    
    def __init__(self,layout_handle,name,*elements,**kw):
        #~ if name == 'cbss':
            #~ logger.info("20120925 Container.__init__() 1 %r",kw)
        #~ self.has_frame = layout_handle.layout.has_frame
        #~ self.labelAlign = layout_handle.layout.label_align
        #~ self.hideCheckBoxLabels = layout_handle.layout.hideCheckBoxLabels
        self.active_children = []
        self.elements = elements
        if elements:
            #~ self.has_fields = False
            for e in elements:
                #~ v = getattr(self,e.name,None)
                #~ if v is not None:
                    #~ raise Exception("%s has already %s = %s" % (self,e.name,v))
                #~ setattr(self,e.name,e)
                e.set_parent(self)
                #~ if isinstance(e,FieldElement):
                    #~ self.has_fields = True
                if not isinstance(e,LayoutElement):
                    raise Exception("%r is not a LayoutElement" % e)
                if e.active_child:
                    self.active_children.append(e)
                elif isinstance(e,Panel):
                    self.active_children += e.active_children
                    #~ self.has_fields = True
            #~ kw.update(items=elements)
                
        LayoutElement.__init__(self,layout_handle,name,**kw)
        
        #~ if self.required:
            #~ if layout_handle.layout._datasource.__name__.startswith('IntegClient'):
                #~ print 20120924, layout_handle, self.required
        #~ if name == 'cbss':
            #~ logger.info("20120925 Container.__init__() 2 %r",self.required)
        
    def as_plain_html(self,ar,obj):
        children = []
        for e in self.elements:
            for chunk in e.as_plain_html(ar,obj):
                children.append(chunk)
        if self.vertical:
            yield E.div(*children)
        else:
            tr = E.tr(*[E.td(ch) for ch in children])
            yield E.table(tr)
        
    def subvars(self):
        return self.elements
            
    def walk(self):
        for e in self.elements:
            for el in e.walk():
                yield el
        yield self
        
    def find_by_name(self,name):
        for e in self.walk():
            if e.name == name:
                return e
        

    def pprint(self,level=0):
        margin = "  " * level
        s = margin + str(self) + ":\n"
        # self.__class__.__name__
        for e in self.elements:
            for ln in e.pprint(level+1).splitlines():
                s += ln + "\n"
        return s

    def ext_options(self,**kw):
        kw = LayoutElement.ext_options(self,**kw)
        #~ not necessary to filter here, jsgen does that
        #~ items = [e for e in self.elements if e.get_view_permission()]
        #~ if items != self.elements:
            #~ print "20120525", self.layout_handle, self, items
        #~ kw.update(items=items)
        kw.update(items=self.elements)
        return kw
        
        

    def get_view_permission(self,profile):
        """
        A Panel which doesn't contain a single visible element 
        becomes itself hidden.
        """
        #~ if self.value.get("title") == "CBSS":
        #~ if str(self.layout_handle.layout) == 'ClientDetail on pcsw.Clients':
            #~ if self.name == 'cbss':
                #~ print '20120925 ext_elems', self.name, 
                #~ if jsgen.Permittable.get_view_permission(self,user):
                #~ if super(Container,self).get_view_permission(user): 
                    #~ logger.warning("Expected %r to be invisible for %s", self,user)
            #~ print "20120525 Container.get_view_permission()", self
            
        # if the Panel itself is invisble, no need to loop through the children
        if not super(Container,self).get_view_permission(profile): 
        #~ if not Permittable.get_view_permission(self,user):
            return False
        #~ if self.value.get("title") == "CBSS":
            #~ print "20120525 Container.get_view_permission() passed", self
        for e in self.elements:
            if (not isinstance(e,Permittable)) or e.get_view_permission(profile):
                # one visble child is enough, no need to continue loop 
                return True
        #~ logger.info("20120925 not a single visible element in %s of %s",self,self.layout_handle)
        return False
        
class Wrapper(VisibleComponent):
    #~ label = None
    def __init__(self,e,**kw):
        kw.update(layout='form')
        if not isinstance(e,TextFieldElement):
            kw.update(autoHeight=True)
        #~ kw.update(labelAlign=e.parent.labelAlign)
        kw.update(labelAlign=e.parent.label_align)
        kw.update(items=e,xtype='panel')
        VisibleComponent.__init__(self,e.name+"_ct",**kw)
        self.wrapped = e
        for n in ('width', 'height', 'preferred_width','preferred_height','vflex','loosen_requirements'):
            setattr(self,n,getattr(e,n))
        #~ e.update(anchor="100%")
        if e.vflex: 
            #~ 20120630 e.update(anchor="100% 100%")
            #~ e.update(anchor="-25 -25")
            e.update(anchor=FULLWIDTH + ' ' + FULLHEIGHT)
        else:
            #~ e.update(anchor="100%")
            #~ e.update(anchor="-25")
            e.update(anchor=FULLWIDTH)
        #~ e.update(padding=DEFAULT_PADDING)
        #~ self.allow_read = e.allow_read
        #~ self.get_view_permission = e.get_view_permission
            
    def get_view_permission(self,profile):
        return self.wrapped.get_view_permission(profile)
        
    #~ def allow_read(self,*args):
        #~ return self.wrapped.allow(user)
        
    def walk(self):
        for e in self.wrapped.walk():
            #~ if e.get_view_permission():
            yield e
        yield self

    def as_plain_html(self,ar,obj):
        for chunk in self.wrapped.as_plain_html(ar,obj):
            yield chunk
            
class Panel(Container):
    """
    A vertical Panel is vflex if and only if at least one of its children is vflex.
    A horizontal Panel is vflex if and only if *all* its children are vflex 
    (if vflex and non-vflex elements are together in a hbox, then the 
    vflex elements will get the height of the highest non-vflex element).
    """
    ext_suffix = "_panel"
    active_child = False
    value_template = "new Ext.Panel(%s)"
    #~ declare_type = jsgen.DECLARE_VAR
    #~ value_template = "new Ext.Panel(%s)"
    
    def __init__(self,layout_handle,name,vertical,*elements,**kw):
        self.vertical = vertical
        #~ if name == 'cbss':
            #~ logger.info("20120925 Panel.__init__() %r",kw)
        #~ if self.vertical:
            #~ vflex_elems = [e for e in elements if e.vflex]
            #~ if len(flex_elems) > 0:
                #~ assert len(kw) == 0, "%r is not empty" % kw
                #~ vfix_elems = [e for e in elements if not e.vflex]
                #~ flex_panel = Panel(layout_handle,name,vertical,*vflex_elems)
                #~ fix_panel = Panel(layout_handle,name,vertical,*vfix_elems)
                
        self.vflex = not vertical
        stretch = False
        #~ monitorResize = False
        for e in elements:
            #~ if e.collapsible:
                #~ monitorResize = True
            if e.vflex:
                stretch = True
            if self.vertical:
                if e.vflex:
                    self.vflex = True
            else:
                if not e.vflex:
                    self.vflex = False
                    #~ print 20100615, self.layout_handle.layout, self, "hbox loses vflex because of", e
        if len(elements) > 1 and self.vflex:
            if self.vertical:
                """
                Example : The panel contains a mixture of fields and grids. 
                Fields are not vflex, grids well.
                """
                #~ print 20100615, self.layout_handle, self
                # so we must split this panel into several containers.
                # vflex elements go into a vbox, the others into a form layout. 
                
                if False:
                    # Rearrange elements into "element groups"
                    # Each element of egroups is a list of elements who have same vflex
                    egroups = []
                    for e in elements:
                        if len(egroups) and egroups[-1][0].vflex == e.vflex:
                            egroups[-1].append(e)
                        else:
                            egroups.append([e])
                            
                    if len(egroups) == 1:
                        # all elements have same vflex
                        assert tuple(egroups[0]) == elements, "%r != %r" % (tuple(egroups[0]), elements)
                        
                    elements = []
                    for eg in egroups:
                        if eg[0].vflex:
                            #~ for e in eg: e.update(flex=1,align='stretch')
                            for e in eg: 
                                e.update(flex=1)
                                e.collapsible = True
                                #~ e.update(collapsible=True)
                            if len(eg) == 1:
                                g = eg[0]
                            else:
                                #~ g = Container(layout_handle,name,*eg,**dict(layout='vbox',flex=1)
                                g = Panel(layout_handle,name,vertical,*eg,**dict(layout='vbox',
                                  flex=1,layoutConfig=dict(align='stretch')))
                                assert g.vflex is True
                        else:
                            #~ for e in eg: e.update(align='stretch')
                            if len(eg) == 1:
                                g = eg[0]
                            else:
                                g = Container(layout_handle,name,*eg,**dict(layout='form',autoHeight=True))
                                #~ g = Container(layout_handle,name,*eg,**dict(layout='form'))
                                assert g.vflex is False
                        #~ if monitorResize:
                            #~ g.update(monitorResize=True)
                        #~ g.update(align='stretch')
                        #~ g.update(layoutConfig=dict(align='stretch'))
                        elements.append(g)
                    kw.update(layout='vbox',layoutConfig=dict(align='stretch'))
                    #~ self.elements = elements
            else: # not self.vertical
                kw.update(layout='hbox',layoutConfig=dict(align='stretch'))
              
        for e in elements:
            #~ e.set_parent(self)
            if isinstance(e,FieldElement):
                self.is_fieldset = True
                #~ if self.label_width < e.label_width:
                    #~ self.label_width = e.label_width
                if e.label:
                    w = len(e.label) + 1 # +1 for the ":"
                    if self.label_width < w:
                        self.label_width = w


        if False: # not yet converted to new dtl syntax 20120214
            label = layout_handle.layout.collapsible_elements.get(name,None)
            if label:
                self.collapsible = True
                self.label = label
            
        #~ if str(layout_handle.layout) == 'ClientDetail on pcsw.Clients':
            #~ if name == 'cbss':
                #~ print '20120925 ext_elems', name, kw

        Container.__init__(self,layout_handle,name,*elements,**kw)
        
        #~ if name == 'cbss':
            #~ logger.info("20120925 Panel.__init__() 2 %r",self.required)
        
        w = h = 0
        has_height = False # 20120210
        for e in self.elements:
            ew = e.width or e.preferred_width
            eh = e.height or e.preferred_height
            if self.vertical:
                #~ h += e.flex
                h += eh
                w = max(w,ew)
            else:
                if e.height:
                    has_height = True
                #w += e.flex
                w += ew
                h = max(h,eh)
        if has_height:
            self.height = h
            self.vflex = True
        else:
            self.preferred_height = h
        self.preferred_width = w
        assert self.preferred_height > 0, "%s : preferred_height is 0" % self
        assert self.preferred_width > 0, "%s : preferred_width is 0" % self
        
        d = self.value
        if not d.has_key('layout'):
            if len(self.elements) == 1:
                d.update(layout='fit')
            elif self.vertical:
                #~ d.update(layout='form')
                if self.vflex:
                    d.update(layout='vbox',layoutConfig=dict(align='stretch'))
                else:
                    # 20100921b
                    #~ d.update(layout='form')
                    d.update(layout='form',autoHeight=True)
                    #~ d.update(layout='vbox',autoHeight=True)
            else:
                d.update(layout='hbox',autoHeight=True) # 20101028
                
        if d['layout'] == 'form':
            assert self.vertical
            #~ self.update(labelAlign=self.labelAlign)
            self.update(labelAlign=self.label_align)
            self.wrap_formlayout_elements()
            #~ d.update(autoHeight=True)
            if len(self.elements) == 1 and self.elements[0].vflex:
                #~ 20120630 self.elements[0].update(anchor="100% 100%")
                #~ self.elements[0].update(anchor="-25 -25")
                self.elements[0].update(anchor=FULLWIDTH + ' ' + FULLHEIGHT)
                
            else:
                for e in self.elements:
                    #~ 20120630 e.update(anchor="100%")
                    #~ e.update(anchor="-25")
                    e.update(anchor=FULLWIDTH)
                
        elif d['layout'] == 'hbox':
                
            #~ if self.as_ext() == 'main_1_panel187':
                #~ logger.info("20120210 b main_1_panel187 : %r",[repr(e) for e in self.elements])
            
            self.wrap_formlayout_elements()
            for e in self.elements:
                """
                20120210
                a hbox having at least one child with explicit height 
                will become itself vflex
                """        
                if e.height:
                    #~ logger.info("20120210 %s becomes vflex because %s has height",self,e)
                    self.vflex = True
                  
                if e.hflex:
                    w = e.width or e.preferred_width
                    #~ e.value.update(columnWidth=float(w)/self.preferred_width) # 20100615
                    e.value.update(flex=int(w*100/self.preferred_width))
                    
            if not self.vflex: # 20101028
                d.update(autoHeight=True)
                d.update(layoutConfig=dict(align='stretchmax'))
                
              
        elif d['layout'] == 'vbox':
            "a vbox with 2 or 3 elements, of which at least two are vflex will be implemented as a VBorderPanel"
            assert len(self.elements) > 1
            self.wrap_formlayout_elements()
            vflex_count = 0
            h = self.height or self.preferred_height
            for e in self.elements:
                eh = e.height or e.preferred_height
                if e.vflex:
                    e.update(flex=int(eh*100/h))
                    vflex_count += 1
            if vflex_count >= 2 and len(self.elements) <= 3:
            #~ if vflex_count >= 1 and len(self.elements) <= 3:
                self.remove('layout','layoutConfig')
                self.value_template = 'new Lino.VBorderPanel(%s)'
                for e in self.elements:
                    #~ if self.ext_name == 'main_panel627':
                        #~ print 20110715, e.height, e.preferred_height
                    #~ if e.vflex: # """as long as there are bugs, make also non-vflex resizable"""
                    if e.vflex:
                        e.update(flex=e.height or e.preferred_height)
                    e.update(split=True)
                self.elements[0].update(region='north')
                self.elements[1].update(region='center')
                if len(self.elements) == 3:
                    self.elements[2].update(region='south')
        elif d['layout'] == 'fit':
            self.wrap_formlayout_elements()
        else:
            raise Exception("layout is %r" % d['layout'] )
            
        
    def wrap_formlayout_elements(self):
        #~ if layout_handle.main_class is DetailMainPanel:
        def wrap(e):
            #~ if isinstance(e,Panel): return e
            if not isinstance(e,FieldElement): return e
            if e.label is None: return e
            if isinstance(e,HtmlBoxElement): return e
            if settings.LINO.use_tinymce:
                if isinstance(e,TextFieldElement) and e.format == 'html': 
                    # no need to wrap them since they are Panels
                    return e
            return Wrapper(e)
        self.elements = [wrap(e) for e in self.elements]
          
        
    def ext_options(self,**d):
        #~ if not self.label and self.value_template == "new Ext.Panel(%s)":
            # if not self.parent or len(self.parent.elements) == 1:
            # if self.parent and len(self.parent.elements) > 1:
            #~ if self.parent is not None:
                #~ self.value_template = "new Ext.Container(%s)"
            
        if self.label:
            if not isinstance(self.parent,TabPanel):
                self.update(title=self.label)
                self.value_template = "new Ext.form.FieldSet(%s)"
                self.update(frame=False)
                self.update(bodyBorder=True)
                self.update(border=True)
            #~ elif isinstance(self.parent,DetailMainPanel):
                #~ if self.value_template == "new Ext.Container(%s)":
                    #~ self.value_template = "new Ext.Panel(%s)"
              
            #~ else:
                #~ self.value_template = "new Ext.Panel(%s)"
        d = Container.ext_options(self,**d)
        
        # hide scrollbars
        d.update(autoScroll=False)
        
        #~ if self.collapsible:
            #~ d.update(xtype='panel')
            #~ js = "function(cmp,aw,ah,rw,rh) { console.log('Panel.collapse',this,cmp,aw,ah,rw,rh); this.main_panel.doLayout(); }"
            #~ d.update(listeners=dict(scope=js_code('this'),collapse=js_code(js),expand=js_code(js)))
            #d.update(monitorResize=True)
        #~ else:
            #~ d.update(xtype='container')
        #d.update(margins='0')
        #d.update(style=dict(padding='0px'))
        
        #~ d.update(items=self.elements)
        #l = [e.as_ext() for e in self.elements ]
        #d.update(items=js_code("[\n  %s\n]" % (", ".join(l))))
        #d.update(items=js_code("this.elements"))
        #~ if self.label and not isinstance(self,MainPanel) and not isinstance(self.parent,MainPanel):
        
        
        if self.is_fieldset:
            d.update(labelWidth=self.label_width * EXT_CHAR_WIDTH)
        #~ if len(self.elements) > 1 and self.vertical:
        if self.parent is None or (len(self.elements) > 1 and self.vertical):
            """
            The `self.parent is None` test is e.g. for Parameter 
            Panels which are usually not vertical but still want a frame 
            since they are the main panel.
            """
            d.update(frame=True)
            d.update(bodyBorder=False)
            d.update(border=False)
            #~ 20120115 d.update(labelAlign=self.labelAlign)
            #d.update(style=dict(padding='0px'),color='green')
        else:
            d.update(frame=False)
            #self.update(bodyBorder=False)
            d.update(border=False)
            
        
        
        return d
        

class GridElement(Container): 
    declare_type = jsgen.DECLARE_VAR
    #~ declare_type = jsgen.DECLARE_THIS
    #value_template = "new Ext.grid.EditorGridPanel(%s)"
    #~ value_template = "new Ext.grid.GridPanel(%s)"
    value_template = "new Lino.GridPanel(%s)"
    ext_suffix = "_grid"
    vflex = True
    xtype = None
    preferred_height = 5
    refers_to_ww = True
    
    def __init__(self,layout_handle,name,rpt,*columns,**kw):
        """
        :param layout_handle: the handle of the FormLayout owning this grid
        :param rpt: the table being displayed (:class:`lino.core.tables.AbstractTable`)
        """
        #~ assert isinstance(rpt,dd.AbstractTable), "%r is not a Table!" % rpt
        self.value_template = "new Lino.%s.GridPanel(%%s)" % rpt
        self.actor = rpt
        if len(columns) == 0:
            self.rh = rpt.get_handle(layout_handle.ui)
            if not hasattr(self.rh,'list_layout'):
                raise Exception("%s has no list_layout" % self.rh)
            columns = self.rh.list_layout.main.columns
            #~ columns = self.rh.list_layout._main.elements
        w = 0
        for e in columns:
            w += (e.width or e.preferred_width)
        self.preferred_width = constrain(w,10,120)
        #~ kw.update(boxMinWidth=500)
        self.columns = columns
        
        vc = dict(emptyText=_("No data to display."))
        if rpt.editable:
            vc.update(getRowClass=js_code('Lino.getRowClass'))
        
        #~ //autoScroll:true,
        #~ //autoFill:true,
        #~ //forceFit=True,
        #~ //enableRowBody=True,
        #~ //~ showPreview:true,
        #~ //~ scrollOffset:200,
        #~ //~ enableRowBody: true,
        
        if rpt.auto_fit_column_widths:
            vc.update(forceFit=True)
            
        kw.update(viewConfig=vc)
        kw.setdefault('label',rpt.label)
        
        #~ kw.update(containing_window=js_code("this.containing_window"))
        kw.update(containing_panel=js_code("this"))
        #~ if not rpt.show_params_at_render:
        if rpt.params_panel_hidden:
            kw.update(params_panel_hidden=True)
        Container.__init__(self,layout_handle,name,**kw)
        self.active_children = columns
        #~ 20111125
        #~ assert not kw.has_key('before_row_edit')
        #~ self.update(before_row_edit=before_row_edit(self))
        
        #~ if self.report.master is not None and self.report.master is not dd.Model:
            #~ self.mt = ContentType.objects.get_for_model(self.report.master).pk
        #~ else:
            #~ self.mt = 'undefined'
            
            
    def get_view_permission(self,profile):
        #~ if not super(GridElement,self).get_view_permission():
        # skip Container parent:
        #~ return super(Container,self).get_view_permission(user)
        #~ return LayoutElement.get_view_permission(self,user)
        if not super(Container,self).get_view_permission(profile): 
            return False
        return self.actor.get_view_permission(profile)
        #~ return self.actor.get_permission(actions.VIEW,jsgen._for_user_profile,None)
        
    def ext_options(self,**kw):
        #~ not direct parent (Container), only LayoutElement
        kw = LayoutElement.ext_options(self,**kw)
        return kw




#~ class DetailMainPanel(Panel,MainPanel):
class DetailMainPanel(Panel):
    #~ declare_type = jsgen.DECLARE_THIS
    #~ xtype = 'form'
    xtype = None
    #~ value_template = "new Ext.form.FormPanel(%s)"
    value_template = "new Ext.Panel(%s)"
    def __init__(self,layout_handle,name,vertical,*elements,**kw):
        #~ self.rh = layout_handle.datalink
        #~ 20111126 self.report = layout_handle.rh.report
        #~ MainPanel.__init__(self)
        #~ DataElementMixin.__init__(self,layout_handle.link)
        kw.update(autoScroll=True)
        #~ kw.update(height=800, autoScroll=True)
        Panel.__init__(self,layout_handle,name,vertical,*elements,**kw)
        #layout_handle.needs_store(self.rh)
        
    def ext_options(self,**kw):
        #~ self.setup()
        kw = Panel.ext_options(self,**kw)
        #~ if self.layout_handle.layout.label:
            #~ kw.update(title=_(self.layout_handle.layout.label))
        #~ ws = self.layout_handle.layout._window_size
        #~ if ws is not None and ws[1] == 'auto':
            #~ kw.update(autoHeight=True)
        if self.layout_handle.main.label:
            kw.update(title=_(self.layout_handle.main.label))
        return kw
        

class ParamsPanel(Panel):
    """
    The optional Panel for `parameters` of a Table. 
    JS part stored in `Lino.GridPanel.params_panel`.
    """
    #~ value_template = "new Ext.form.FormPanel(%s)"
    #~ value_template = "new Ext.form.FormPanel({layout:'fit', autoHeight: true, frame: true, items:new Ext.Panel(%s)})"
    value_template = "%s"
    #~ pass
    def unused__init__(self,lh,name,vertical,*elements,**kw):
        Panel.__init__(self,lh,name,vertical,*elements,**kw)
        
        #~ fkw = dict(layout='fit', autoHeight= True, frame= True, items=pp)
        if lh.layout._datasource.params_panel_hidden:
            self.value_template = "new Ext.form.FormPanel({hidden:true, layout:'fit', autoHeight: true, frame: true, items:new Ext.Panel(%s)})"
          
            #~ fkw.update(hidden=True)
        #~ self.value = 
        #~ return ext_elems.FormPanel(**fkw)
    

#~ class ParamsForm(Panel):
#~ class DialogPanel(Panel):
class ActionParamsPanel(Panel):
    """
    The optional Panel for `parameters` of an Action. 
    """
    xtype = None
    #~ value_template = "%s"
    #~ value_template = "new Ext.form.FormPanel(%s)"
    #~ value_template = "new Lino.ActionParamsPanel({layout:'fit', autoHeight: true, frame: true, items:new Ext.Panel(%s)})"
    value_template = "new Lino.ActionParamsPanel(%s)"
    

class TabPanel(Panel):
    value_template = "new Ext.TabPanel(%s)"

    def __init__(self,layout_handle,name,*elems,**kw):
        kw.update(autoScroll=True)
        kw.update(
          split=True,
          activeTab=0, 
          #~ layoutOnTabChange=True, # 20101028
          #~ forceLayout=True, # 20101028
          #~ deferredRender=False, # 20120212
          #~ autoScroll=True, 
          #~ width=300, # ! http://code.google.com/p/lino/wiki/20100513
          #~ items=elems,
          # http://www.extjs.com/forum/showthread.php?26564-Solved-FormPanel-in-a-TabPanel
          #~ listeners=dict(activate=js_code("function(p) {p.doLayout();}"),single=True),
        )
        Container.__init__(self,layout_handle,name,*elems,**kw)
        



_FIELD2ELEM = (
    #~ (dd.Constant, ConstantElement),
    (dd.RecurrenceField, RecurrenceElement),
    (dd.HtmlBox, HtmlBoxElement),
    #~ (dd.QuickAction, QuickActionElement),
    (dd.DisplayField, DisplayElement),
    (dd.IncompleteDateField, IncompleteDateFieldElement),
    #~ (dd.LinkedForeignKey, LinkedForeignKeyElement),
    (models.URLField, URLFieldElement),
    (models.FileField, FileFieldElement),
    (models.EmailField, CharFieldElement),
    #~ (dd.HtmlTextField, HtmlTextFieldElement),
    #~ (dd.RichTextField, RichTextFieldElement),
    (models.TextField, TextFieldElement), # also dd.RichTextField
    (dd.PasswordField, PasswordFieldElement),
    (models.CharField, CharFieldElement),
    (dd.MonthField, MonthFieldElement),
    (models.DateTimeField, DateTimeFieldElement),
    (dd.DatePickerField, DatePickerFieldElement),
    (models.DateField, DateFieldElement),
    (models.TimeField, TimeFieldElement),
    (models.IntegerField, IntegerFieldElement),
    (models.DecimalField, DecimalFieldElement),
    (dd.QuantityField, CharFieldElement),
    (models.BooleanField, BooleanFieldElement),
    #~ (models.ManyToManyField, M2mGridElement),
    (models.ForeignKey, ForeignKeyElement),
    (models.AutoField, IntegerFieldElement),
)
    
TRIGGER_BUTTON_WIDTH = 3

def field2elem(layout_handle,field,**kw):
    #~ if hasattr(field,'_lino_chooser'):
    ch = choosers.get_for_field(field)
    if ch:
        #~ if ch.on_quick_insert is not None:
        #~ if ch.meth.quick_insert_field is not None:
        #~ if ch.multiple:
            #~ raise Exception("20120616")
        if ch.can_create_choice or not ch.force_selection:
            kw.update(forceSelection=False)
            #~ print 20110425, field.name, layout_handle
        if ch.simple_values:
            #~ kw.update(forceSelection=False)
            return SimpleRemoteComboFieldElement(layout_handle,field,**kw)
        else:
            if isinstance(field,models.ForeignKey):
                return ForeignKeyElement(layout_handle,field,**kw)
            #~ elif isinstance(field,fields.GenericForeignKeyIdField):
                #~ return ComplexRemoteComboFieldElement(layout_handle,field,**kw)
            else:
                return ComplexRemoteComboFieldElement(layout_handle,field,**kw)
    if field.choices:
        if isinstance(field,choicelists.ChoiceListField):
            kw.setdefault('preferred_width',
                field.choicelist.preferred_width+TRIGGER_BUTTON_WIDTH)
            kw.update(forceSelection=field.force_selection)
            return ChoiceListFieldElement(layout_handle,field,**kw)
        else:
            kw.setdefault('preferred_width',20)
            return ChoicesFieldElement(layout_handle,field,**kw)
    
    selector_field = field
    if isinstance(field,dd.VirtualField):
        selector_field = field.return_type
    elif isinstance(field,fields.RemoteField):
        selector_field = field.field
    
    if isinstance(selector_field,models.BooleanField) and not field.editable:
        return BooleanDisplayElement(layout_handle,field,**kw)
        
    for cl,x in _FIELD2ELEM:
        if isinstance(selector_field,cl):
            return x(layout_handle,field,**kw)
    if isinstance(field,dd.VirtualField):
        raise NotImplementedError("No LayoutElement for VirtualField %s on %s in %s" % (
          field.name,field.return_type.__class__,layout_handle.layout))
    if isinstance(field,fields.RemoteField):
        raise NotImplementedError("No LayoutElement for RemoteField %s on %s" % (
          field.name,field.field.__class__))
    raise NotImplementedError("No LayoutElement for %s (%s) in %s" 
        % (field.name,field.__class__,layout_handle.layout))
