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

from lino.apps.std.settings import *

class Lino(Lino):
    source_dir = os.path.dirname(__file__)
    title = "Lino/MinimalApp 1"
    #~ help_url = "http://lino.saffre-rumma.net/az/index.html"
    #~ migration_module = 'lino.apps.az.migrate'
    
    use_extensible = False
    #~ project_model = 'contacts.Person'
    #~ project_model = 'contacts.Person'
    #~ project_model = None
    #~ user_model = None
    
    default_user = 'root'
    
    #~ languages = ('de', 'fr')
    languages = ['en']
    
    #~ index_view_action = "dsbe.Home"
    
    #~ remote_user_header = "REMOTE_USER"
    
    def get_app_source_file(self):  return __file__
        
    def setup_quicklinks(self,ui,user,tb):
        tb.add_action(self.modules.contacts.Persons.detail_action)
        tb.add_action(self.modules.contacts.Companies.detail_action)
        
      
LINO = Lino(__file__,globals())


TIME_ZONE = None


INSTALLED_APPS = (
  #~ 'django.contrib.auth',
  'django.contrib.contenttypes',
  #~ 'django.contrib.sessions',
  #~ 'django.contrib.sites',
  #~ 'django.contrib.markup',
  'lino',
  'lino.modlib.users',
  'lino.modlib.countries',
  'lino.modlib.contacts',
  'lino.apps.min1',
)


