# -*- coding: utf-8 -*-
## Copyright 2008-2012 Luc Saffre
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
This module contains some relatively quick tests 
that don't load any fixtures.
  
"""

from django.conf import settings

from lino.utils.test import TestCase
#from lino.igen import models
#from lino.modlib.contacts.models import Contact, Companies
#from lino.modlib.countries.models import Country
from lino.utils import babel

from lino.core.modeltools import resolve_model,resolve_app
Person = resolve_model(settings.LINO.person_model)
contacts = resolve_app('contacts')
from lino.utils.instantiator import Instantiator, create_and_get
from lino.utils.babel import babel_values
from lino.utils.choicelists import Gender

class QuickTest(TestCase):
    #~ fixtures = [ 'std', 'few_countries', 'ee', 'be', 'demo', 'demo_ee']
    #~ fixtures = 'few_countries few_languages demo_cities std demo demo_ee'.split()
    #~ fixtures = 'std few_countries few_cities few_languages props demo'.split()
    pass
    
    
person = Instantiator(settings.LINO.person_model).build
company = Instantiator(settings.LINO.company_model).build

def test01(self):
    """
    Tests some basic funtionality.
    """
    ee = create_and_get('countries.Country',
        isocode='EE',**babel_values('name',
        de=u"Estland",
        fr=u'Estonie',
        en=u"Estonia",
        nl=u'Estland',
        et=u'Eesti',
        ))
    be = create_and_get('countries.Country',
        isocode='BE',**babel_values('name',
        de=u"Belgien",
        fr=u'Belgique',
        en=u"Belgium",
        nl=u'Belgie',
        et=u'Belgia',
        ))
          
    eupen = create_and_get('countries.City',name=u'Eupen',country=be,zip_code='4700')
    vigala = create_and_get('countries.City',name=u'Vigala',country=ee)
          
    
    luc = create_and_get(settings.LINO.person_model,
        first_name='Luc',last_name='Saffre',
        gender=Gender.male,
        country=ee,street='Uus', street_no='1',
        addr2=u'Vana-Vigala küla',
        city=vigala,zip_code='78003')
        
    if 'en' in babel.AVAILABLE_LANGUAGES:
        babel.set_language('en')
        self.assertEquals(luc.address(), u'''\
Mr Luc SAFFRE
Uus 1
Vana-Vigala küla
78003 Vigala
Estonia''')
    if 'de' in babel.AVAILABLE_LANGUAGES:
        babel.set_language('de')
        self.assertEquals(luc.address(), u'''\
Herrn Luc SAFFRE
Uus 1
Vana-Vigala küla
78003 Vigala
Estland''')
    babel.set_language(None)
    
    
        
def test02(self):
    """
    """
    u = create_and_get(settings.LINO.user_model,
        username='root',language='')
    #~ lang = u.language
    #~ print 20120729, repr(u.language)
    
    #~ settings.LINO.never_build_site_cache = True
    
    """
    disable LINO.is_imported_partner() otherwise 
    disabled_fields may contain more than just the 'id' field.
    """
    save_iip = settings.LINO.is_imported_partner
    def f(obj): return False
    settings.LINO.is_imported_partner = f
    
    
    luc = Person.objects.get(name__exact="Saffre Luc")
    url = '/api/contacts/Person/%d?query=&an=detail&fmt=json' % luc.pk
    if 'en' in babel.AVAILABLE_LANGUAGES:
        u.language = 'en'
        u.save()
        response = self.client.get(url,REMOTE_USER='root') # ,HTTP_ACCEPT_LANGUAGE='en')
        result = self.check_json_result(response,'navinfo disable_delete data id title')
        self.assertEqual(result['data']['country'],"Estonia")
        self.assertEqual(result['data']['gender'],"Male")
    
    if 'de' in babel.AVAILABLE_LANGUAGES:
        u.language = 'de'
        u.save()
        response = self.client.get(url,REMOTE_USER='root') # ,HTTP_ACCEPT_LANGUAGE='de')
        result = self.check_json_result(
          response,
          'navinfo disable_delete data id title')
        self.assertEqual(result['data']['country'],"Estland")
        self.assertEqual(result['data']['gender'],u"Männlich")
        #~ self.assertEqual(result['data']['disabled_fields'],['contact_ptr_id','id'])
        #~ self.assertEqual(result['data']['disabled_fields'],['id'])
        self.assertEqual(result['data']['disabled_fields'],{'id': True})
        
        
    if 'fr' in babel.AVAILABLE_LANGUAGES:
        u.language = 'fr'
        u.save()
        response = self.client.get(url,REMOTE_USER='root') # ,HTTP_ACCEPT_LANGUAGE='fr')
        result = self.check_json_result(response,'navinfo disable_delete data id title')
        self.assertEqual(result['data']['country'],"Estonie")
        self.assertEqual(result['data']['gender'],u"Masculin")
        
    #~ u.language = lang
    #~ u.save()
    # restore is_imported_partner method
    settings.LINO.is_imported_partner = save_iip
