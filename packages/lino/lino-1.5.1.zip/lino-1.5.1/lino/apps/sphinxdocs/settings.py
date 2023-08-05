# -*- coding: UTF-8 -*-
## Copyright 2012 Luc Saffre
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

A special settings module to be used as DJANGO_SETTINGS_MODULE 
when Sphinx generates the Lino docs.
It contains *all* modlib modules, which makes no sense in practice 
and would raise errors if you try to initialize a database or 
validate the models, but it is enough to have autodocs do its job. 
And that's all we want.

"""

import os
import lino

from lino.apps.std.settings import *


class Lino(Lino):
    source_dir = os.path.dirname(__file__)
    title = "lino.apps.sphinxdocs"
    
    project_model = 'contacts.Person'
    user_model = 'users.User'
    
    #~ languages = ('de', 'fr', 'nl', 'en')
    languages = ['en']
    

LINO = Lino(__file__,globals())



INSTALLED_APPS = (
  #~ 'django.contrib.auth',
  'django.contrib.contenttypes',
  #~ 'django.contrib.sessions',
  #~ 'django.contrib.sites',
  #~ 'django.contrib.markup',
  #~ 'lino.modlib.system',
  'lino',
  'lino.modlib.users',
  'lino.modlib.countries',
  #~ 'lino.modlib.documents',
  'lino.modlib.properties',
  'lino.modlib.contacts',
  
  'lino.modlib.uploads',
  'lino.modlib.thirds',
  'lino.modlib.notes',
  #~ 'lino.modlib.links',
  
  
  #~ 'lino.modlib.projects',
  'lino.modlib.outbox',
  'lino.modlib.cal',
  'lino.modlib.postings',
  #~ 'lino.modlib.inbox',
  'lino.modlib.households',
  
  'lino.modlib.accounts',
  'lino.modlib.ledger',
  'lino.modlib.vat',
  'lino.modlib.products',
  'lino.modlib.sales',
  
  #~ 'lino.modlib.jobs',
  #~ 'lino.modlib.isip',
  #~ 'lino.modlib.cbss',
  #~ 'lino.apps.pcsw',
  'lino.apps.presto',
)

