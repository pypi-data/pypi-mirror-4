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


import os
import lino

from lino.projects.std.settings import *

class Lino(Lino):
    source_dir = os.path.dirname(__file__)
    title = "Lino/MinimalApp 2"
    #~ help_url = "http://lino.saffre-rumma.net/az/index.html"
    #~ migration_module = 'lino.projects.az.migrate'
    
    #~ project_model = 'contacts.Person'
    #~ project_model = 'contacts.Person'
    project_model = 'projects.Project'
    user_model = "users.User"
    
    #~ languages = ('de', 'fr')
    languages = ['en','et']
    
    #~ index_view_action = "dsbe.Home"
    
    #~ remote_user_header = "REMOTE_USER"
    #~ remote_user_header = None
    
    def get_app_source_file(self):  return __file__
        
    #~ def setup_quicklinks(self,ui,user,tb):
        #~ tb.add_action(self.modules.contacts.Persons.detail_action)
        #~ tb.add_action(self.modules.contacts.Companies.detail_action)

    def get_installed_apps(self):
        for a in super(Lino,self).get_installed_apps():
            yield a
        yield 'lino.modlib.users'
        yield 'lino.modlib.countries'
        yield 'lino.modlib.contacts'
        yield 'lino.modlib.projects'
        yield 'lino.modlib.uploads'
        yield 'lino.modlib.cal'
        yield 'lino.modlib.outbox'
        yield 'lino.modlib.pages'
        yield 'lino.projects.min2'

      
LINO = Lino(__file__,globals())



unused_INSTALLED_APPS = (
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
  #~ 'lino.modlib.properties',
  'lino.modlib.contacts',
  'lino.modlib.projects',
  #~ 'lino.projects.modlib.families',
  #~ 'lino.az.notes',
  #~ 'lino.projects.az.school',
  #~ 'lino.modlib.links',
  'lino.modlib.uploads',
  #~ 'lino.modlib.thirds',
  'lino.modlib.cal',
  #~ 'lino.modlib.mails',
  'lino.modlib.outbox',
  #~ 'lino.modlib.jobs',
  #~ 'lino.modlib.isip',
  #~ 'lino.modlib.bcss',
  #~ 'lino.modlib.newcomers',
  'lino.projects.min2',
)


