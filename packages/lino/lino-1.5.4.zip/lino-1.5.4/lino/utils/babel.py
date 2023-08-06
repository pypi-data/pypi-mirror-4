## Copyright 2009-2013 Luc Saffre
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

"""
Generic support for multilingual content
in both hard-coded values and database fields.

This includes definition of *babel fields* in your Django Models 
as well as methods to access these fields transparently.

Babel Fields are normal CharFields or TextFields, except 
that they have been automatically generated from a master field, 
depending on your local :setting:`LANGUAGE_CODE` 
and :setting:`LANGUAGES` settings

Example::

  class Foo(models.Model):
      name = babel.BabelCharField(_("Foo"), max_length=200)
      
To handle hard-coded multilingual texts we suggest 
the :mod:`lino.core.choicelists` module which uses
the :class:`BabelText` class defined below.

One known issue is that complex language codes are not yet 
supported or at least not tested. 
The :setting:`LANGUAGE_CODE` in your :xfile:`settings.py` 
should be ``'de'``, and not ``'de-BE'`` or ``'de-CH'``.

"""

import logging
logger = logging.getLogger(__name__)

import sys
import locale
import datetime


from django.db import models
from django.conf import settings
from django.template import defaultfilters
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

from lino.core import fields
from lino.core.model import Model


LANGUAGE_CODE_MAX_LENGTH = 2            
"""
"""

DEFAULT_LANGUAGE = settings.LANGUAGE_CODE[:LANGUAGE_CODE_MAX_LENGTH].strip()
"""
The 2 first chars of :setting:`LANGUAGE_CODE`.
"""

LANGUAGE_CHOICES = [ (k,_(v)) for k,v in settings.LANGUAGES ]

assert DEFAULT_LANGUAGE in [x[0] for x in settings.LANGUAGES]
  
BABEL_LANGS = [x[0] for x in settings.LANGUAGES if x[0] != DEFAULT_LANGUAGE]
  
AVAILABLE_LANGUAGES = tuple([DEFAULT_LANGUAGE] + BABEL_LANGS)

BABEL_LANGS = tuple(BABEL_LANGS)

LANGUAGE_DICT = dict()
for k,v in LANGUAGE_CHOICES:
    LANGUAGE_DICT[k] = v


#~ logger.info("Languages: %s ",AVAILABLE_LANGUAGES)

def default_language():
    """
    Returns the default language of this website
    as defined by :setting:`LANGUAGE_CODE` in your :xfile:`settings.py`.
    """
    return DEFAULT_LANGUAGE
    
    
def language_choices(language,choices):
    l = choices.get(language,None)
    if l is None:
        l = choices.get(DEFAULT_LANGUAGE)
    return l


LONG_DATE_FMT = {
  #~ None: 'l, j F Y',
  None: 'l, F j, Y',
  'en': 'l, F j, Y',
  'de': 'l, j. F Y',
  'fr': 'l j F Y',
  'et': 'l, j F Y.a.',
}

SHORT_DATE_FMT = {
  None: 'Y-m-d',
  'en': 'Y-m-d',
  'de': 'd.m.Y',
  'et': 'd.m.Y',
  'fr': 'd/m/Y',
}


def lc2locale(lang,country):
    """
    Convert a combination of `lang` and `country` codes to 
    a platform-dependant locale setting to be used for 
    :func:`locale.setlocale`.
    Thanks to 
    http://www.gossamer-threads.com/lists/python/bugs/721929
    and
    http://msdn.microsoft.com/en-us/library/hzz3tw78
    """
    if sys.platform == 'win32': # development server
        if lang == 'fr':
            if country == 'BE': return 'french-belgian'
            return 'french'
        if lang == 'de':
            if country == 'BE': return 'german-belgian'
            return 'german'
        raise NotImplementedError("lc2locale(%r,%r)" % (lang,country))
    else:
        return lang+'_'+country
        

def monthname(n):
    d = datetime.date(2013,n,1)
    return defaultfilters.date(d,'F')

def dtomy(d):
    """
    "date to month/year" :
    return the specified date as a localized string of type 'June 2011'."""
    if d is None: return ''
    return defaultfilters.date(d,'F Y')

def dtos(d):
    "Return the specified date as a localized short string of type '15.06.2011'."
    if d is None: return ''
    return defaultfilters.date(d,SHORT_DATE_FMT[get_language()])
    #~ return d.strftime(SHORT_DATE_FMT[LANG])

def dtosl(d):
    "Return the specified date as a localized long string of type 'Wednesday, May 4, 2011'."
    if d is None: return ''
    return defaultfilters.date(d,LONG_DATE_FMT[get_language()])
    #~ return d.strftime(LONG_DATE_FMT[LANG])
    

    
def set_language(lang):
    #~ global LANG
    #~ LANG = lang
    """
    Setting the locale is necessary in order to have :func:`dtosl` 
    return month names in the correct language.
    
    Note that :func:`locale.setlocale` is not thread-safe on most systems.
    http://www.velocityreviews.com/forums/t348372-setlocale-in-a-module-extension-library.html
    http://www.velocityreviews.com/forums/t332047-setlocale-returns-error.html
    """
    #~ print "20111111 babel.set_language()", lang
    if lang is None or lang is DEFAULT_LANGUAGE:
        #~ locale.setlocale(locale.LC_ALL,'')
        translation.deactivate()
    else:
        if not lang in AVAILABLE_LANGUAGES:
            raise Exception(
              "Cannot set language to %s: available languages are %s." % (
              lang,AVAILABLE_LANGUAGES))
        translation.activate(lang)
        #~ country = settings.LANGUAGE_CODE[3:]
        #~ locale.setlocale(locale.LC_ALL,lc2locale(lang,country))
    
        #~ save_ls = locale.getlocale()
        #~ ls = lc2locale(lang,country)
        #~ ls = 'de-DE' # de_DE
        #~ print ls
        #~ logger.debug("appy.pod render %s -> %s using locale=%r",tpl,target,ls)
        #~ locale.setlocale(locale.LC_ALL,'')
    
    
def babelattr(obj,attrname,*args):
    """
    return the value of the specified attribute `attrname` of `obj`,
    but if `obj` also has a multi-language version of that 
    attribute for the current language, then prefer this attribute's 
    value if it is not blank.
    
    This is to be used in multilingual document templates.

    For example in a document template of a Contract you may now use the following expression::

      babelattr(self.type,'name')

    When generating a Contract in french (:attr:`isip.Contract.language` is ``fr``), 
    the expression will return :attr:`isip.ContractType.name_fr` if this field is not blank. 
    Otherwise (if the contract's language is not ``fr``, 
    of if this contract's type's `name_fr` field is blank) 
    it returns :attr:`isip.ContractType.name`.

    Not tested for other field types than CHAR.
    
    Topic: :doc:`/topics/babel`.
    
    See also :doc:`/blog/2010/1207`.
    
    """
    LANG = translation.get_language()
    if LANG is not None and LANG != default_language():
        v = getattr(obj,attrname+"_"+LANG,None)
        if v:
            return v
    return getattr(obj,attrname,*args)
        
getattr_lang = babelattr
    
def _contribute_to_class(field,cls,fieldclass,**kw):
    if cls._meta.abstract:
        return
    kw.update(blank=True)
    for lang in BABEL_LANGS:
        kw.update(verbose_name=string_concat(field.verbose_name,' ('+lang+')'))
        newfield = fieldclass(**kw)
        newfield._lino_babel_field = True # used by modeltools.get_data_elems
        cls.add_to_class(field.name + '_' + lang,newfield)

class BabelCharField(models.CharField):
    """
    Define a variable number of clones of the "master" field, 
    one for each language of your :setting:`BABEL_LANGS`.
    """
        
    def contribute_to_class(self, cls, name):
        super(BabelCharField,self).contribute_to_class(cls, name)
        _contribute_to_class(self,cls,models.CharField,
            max_length=self.max_length)
        #~ kw = dict()
        #~ kw.update(max_length=self.max_length)
        #~ kw.update(blank=True)
        #~ for lang in BABEL_LANGS:
            #~ kw.update(verbose_name=self.verbose_name + ' ('+lang+')')
            #~ newfield = models.CharField(**kw)
            #~ newfield._lino_babel_field = True # used by modeltools.get_data_elems
            #~ cls.add_to_class(self.name + '_' + lang,newfield)
            

class BabelTextField(fields.RichTextField):
#~ class BabelTextField(models.TextField):
    """
    Define a variable number of clones of the "master" field, 
    one for each language of your :setting:`BABEL_LANGS`.
    """
    def contribute_to_class(self, cls, name):
        super(BabelTextField,self).contribute_to_class(cls, name)
        _contribute_to_class(self,cls,fields.RichTextField,
            format=self.textfield_format)
            
        #~ if cls._meta.abstract:
            #~ return
        #~ kw = dict()
        #~ kw.update(format=self.textfield_format)
        #~ kw.update(blank=True)
        #~ for lang in BABEL_LANGS:
            #~ kw.update(verbose_name=self.verbose_name + ' ('+lang+')')
            #~ # newfield = models.TextField(**kw)
            #~ newfield = fields.RichTextField(**kw)
            #~ newfield._lino_babel_field = True # used by modeltools.get_data_elems
            #~ cls.add_to_class(self.name + '_' + lang,newfield)


def kw2field(name,**kw):
    """
    kw2names
    """
    d = { name : kw.get(default_language())}
    for lang in BABEL_LANGS:
        v = kw.get(lang,None)
        if v is not None:
            d[name+'_'+lang] = v
    return d
babel_values = kw2field


def field2kw(obj,name):
    d = { default_language() : getattr(obj,name) }
    for lang in BABEL_LANGS:
        v = getattr(obj,name+'_'+lang)
        if v:
            d[lang] = v
    return d
  

def babelitem(**v):
    lng = translation.get_language()
    #~ print lng,v
    #~ lng = LANG or DEFAULT_LANGUAGE
    if lng == DEFAULT_LANGUAGE:
        return v.get(lng)
    x = v.get(lng,None)
    if x is None:
        x = v.get(DEFAULT_LANGUAGE)
    return x
    
# babel_get(v) = babelitem(**v)
        
def babeldict_getitem(d,k):
    v = d.get(k,None)
    if v is not None:
        assert type(v) is dict
        return babelitem(**v)
        
        
def unused_discover():
    """This would somehow have to be called 
    *during* and not after model setup.
    """
    logger.debug("Discovering babel fields...")
    for model in models.get_models():
        babel_fields = getattr(model,'babel_fields',None)
        if babel_fields:
            for name in babel_fields:
                add_babel_field(model,name)
                
                
                
class BabelText(object):
    def __init__(self,**texts):
        self.texts = texts

    def __unicode__(self):
        return unicode(babelitem(**self.texts))
        

class BabelNamed(Model):
    """
    Mixin for models that have a non-nullable field `name` 
    (labelled "Description") for each language.
    """
    
    grid_search_field = 'name'

    class Meta:
        abstract = True
        
    name = BabelCharField(max_length=200,verbose_name=_("Designation"))
    
    def __unicode__(self):
        return babelattr(self,'name')
    
            
                
class LanguageField(models.CharField):
    """
    A field that lets the user select a language 
    from :setting:`LANGUAGES` setting.
    """
    def __init__(self, *args, **kw):
        defaults = dict(
            verbose_name=_("Language"),
            choices=LANGUAGE_CHOICES,
            #~ default=DEFAULT_LANGUAGE,
            default=get_language,
            max_length=LANGUAGE_CODE_MAX_LENGTH,
            )
        defaults.update(kw)
        models.CharField.__init__(self,*args, **defaults)

                
def run_with_language(lang,func):                
    """
    Selects the specified language `lang`, 
    calls the specified functon `func`,
    restores the previously selected language.
    """
    current_lang = get_language()
    set_language(lang)
    try:
        rv = func()
    except Exception:
        set_language(current_lang)
        raise
    set_language(current_lang)
    return rv
                
                
LOOKUP_OP = '__iexact'

def lookup_filter(fieldname,value,**kw):
    kw[fieldname+LOOKUP_OP] = value
    #~ kw[fieldname] = value
    flt = models.Q(**kw)
    del kw[fieldname+LOOKUP_OP]
    for lng in BABEL_LANGS:
        kw[fieldname+'_'+lng+LOOKUP_OP] = value
        #~ flt = flt | models.Q(**{self.lookup_field.name+'_'+lng+'__iexact': value})
        #~ flt = flt | models.Q(**{self.lookup_field.name+'_'+lng: value})
        flt = flt | models.Q(**kw)
        del kw[fieldname+'_'+lng+LOOKUP_OP]
    return flt
        