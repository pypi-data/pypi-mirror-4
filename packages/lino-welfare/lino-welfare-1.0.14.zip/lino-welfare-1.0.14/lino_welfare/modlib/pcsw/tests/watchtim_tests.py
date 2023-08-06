# -*- coding: UTF-8 -*-
## Copyright 2013 Luc Saffre
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
This module contains "watch_tim" tests. 
You can run only these tests by issuing::

  python manage.py test pcsw.WatchTimTest
  
"""

from __future__ import unicode_literals


import logging
logger = logging.getLogger(__name__)

#~ from django.utils import unittest
#~ from django.test.client import Client
from django.conf import settings

#from lino.igen import models
#from lino.modlib.contacts.models import Contact, Companies
#from lino.modlib.countries.models import Country
#~ from lino.modlib.contacts.models import Companies


from lino import dd
from lino.utils import i2d
from lino.utils import babel
#~ from lino.core.modeltools import resolve_model
#Companies = resolve_model('contacts.Companies')
from lino.utils.test import TestCase

#~ Person = dd.resolve_model('contacts.Person')
#~ Property = dd.resolve_model('properties.Property')
#~ PersonProperty = dd.resolve_model('properties.PersonProperty')

#~ from lino.apps.pcsw.models import Person
#~ from lino.modlib.cv.models import PersonProperty
#~ from lino.modlib.properties.models import Property

from lino_welfare.modlib.pcsw.management.commands.watch_tim import process_line


POST_GEORGES = """{"method":"POST","alias":"PAR","id":"0000023633","time":"20130220 08:55:30",\
"user":"MELANIE","data":{"IDPAR":"0000023633","FIRME":"Schneider Georges","NAME2":"",\
"RUE":"","CP":"","IDPRT":"S","PAYS":"B","TEL":"","FAX":"","COMPTE1":"","NOTVA":"",\
"COMPTE3":"","IDPGP":"","DEBIT":"","CREDIT":"","ATTRIB":"N","IDMFC":"30","LANGUE":"D",\
"IDBUD":"","PROF":"80","CODE1":"","CODE2":"","CODE3":"",\
"DATCREA":{"__date__":{"year":2013,"month":2,"day":20}},"ALLO":"","NB1":"","NB2":"",\
"IDDEV":"","MEMO":"","COMPTE2":"","RUENUM":"","RUEBTE":"","DEBIT2":"","CREDIT2":"",\
"IMPDATE": {"__date__":{"year":0,"month":0,"day":0}},"ATTRIB2":"","CPTSYSI":"",\
"EMAIL":"","MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},"IDUSR":"","DOMI1":""}}"""

PUT_MAX_MORITZ = """{"method":"PUT","alias":"PAR","id":"0000005088","time":"20130222 12:06:01",
"user":"MELANIE","data":{"IDPAR":"0000005088","FIRME":"Müller Max Moritz","NAME2":"",
"RUE":"Werthplatz 12","CP":"4700","IDPRT":"I","PAYS":"B","TEL":"","FAX":"",
"COMPTE1":"001-1234567-89","NOTVA":"BE-0999.999.999","COMPTE3":"","IDPGP":"",
"DEBIT":"","CREDIT":"","ATTRIB":"A","IDMFC":"","LANGUE":"D","IDBUD":"",
"PROF":"80","CODE1":"RH","CODE2":"","CODE3":"",
"DATCREA":{"__date__":{"year":1991,"month":8,"day":12}},
"ALLO":"Herr","NB1":"","NB2":"","IDDEV":"","MEMO":"","COMPTE2":"",
"RUENUM":"","RUEBTE":"","DEBIT2":"","CREDIT2":"",
"IMPDATE":{"__date__":{"year":1999,"month":5,"day":3}},"ATTRIB2":"",
"CPTSYSI":"","EMAIL":"","MVIDATE":{"__date__":{"year":0,"month":0,"day":0}},
"IDUSR":"ALICIA","DOMI1":""}}
"""

POST_PXS = """{"method":"POST","alias":"PXS","id":"0000023635","time":"20130222 11:07:42",
"user":"MELANIEL","data":{"IDPAR":"0000023635","NAME":"Heinz Hintz",
"GEBDAT":{"__date__":{"year":0,"month":0,"day":0}},"APOTHEKE":"","HILFE":"",
"ANTEIL":"","IDMUT":"","VOLLMACHT":{"__date__":{"year":0,"month":0,"day":0}},
"LAUFZEIT":{"__date__":{"year":0,"month":0,"day":0}},"DRINGEND":"","MONATLICH":"",
"SOZIAL":"","MIETE":"","MAF":"","REFERENZ":"","MEMO":"","SEXE":"","GENERIKA":"",
"IDPRT":"S","CARDNUMBER":"","VALID1":{"__date__":{"year":0,"month":0,"day":0}},
"VALID2":{"__date__":{"year":0,"month":0,"day":0}},"CARDTYPE":0,"NATIONALIT":"",
"BIRTHPLACE":"","NOBLECOND":"","CARDISSUER":""}}
"""



User = dd.resolve_model('users.User')
Partner = dd.resolve_model('contacts.Partner')
Company = dd.resolve_model('contacts.Company')
Person = dd.resolve_model('contacts.Person')
Client = dd.resolve_model('pcsw.Client')
Coaching = dd.resolve_model('pcsw.Coaching')

class WatchTimTest(TestCase):
    pass
    #~ def setUp(self):
        #~ settings.LINO.never_build_site_cache = True
        #~ super(DemoTest,self).setUp()
            
  
def test00(self):
    User(username='watch_tim').save()
    User(username='alicia').save()
    User(username='roger').save()
    
def test01(self):
    """
    AttributeError 'NoneType' object has no attribute 'coaching_type'
    """
    self.assertDoesNotExist(Client,id=23633)
    process_line(POST_GEORGES)
    georges = Client.objects.get(id=23633)
    self.assertEqual(georges.first_name,"Georges")
    
def test02(self):
    """
    Company becomes Client
    
    ValidationError([u'A Partner cannot be parent for a Client']) (201302-22 12:42:07)
    A Partner in TIM has both `PAR->NoTva` and `PAR->IdUsr` filled. 
    It currently exists in Lino as a Company but not as a Client.
    `watch_tim` then must create a Client after creating also the intermediate Person.
    The Company child remains.
    """
    
    Company(name="Müller Max Moritz",id=5088).save()
    
    process_line(PUT_MAX_MORITZ)
    company = Company.objects.get(id=5088) # has not been deleted
    person = Person.objects.get(id=5088) # has been created
    client = Client.objects.get(id=5088) # has been created
    company = Company.objects.get(id=5088) # has not been deleted
    coaching = Coaching.objects.get(client=client,user__username='alicia') # has been created
    self.assertEqual(person.first_name,"Max Moritz")
    self.assertEqual(client.first_name,"Max Moritz")
    self.assertEqual(coaching.primary,True)
    self.assertEqual(coaching.start_date,i2d(19910812))

def test03(self):
    """
    Test whether watch_tim raises Exception 
    'Cannot create Client ... from PXS' when necessary.
    """
    self.assertDoesNotExist(Client,id=23635)
    try:
        process_line(POST_PXS)
        self.fail("Expected an exception")
    except Exception as e:
        self.assertEqual(str(e),"Cannot create Client 0000023635 from PXS")
    self.assertDoesNotExist(Client,id=23635)
