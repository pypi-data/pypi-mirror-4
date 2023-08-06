# -*- coding: utf-8 -*-
## Copyright 2011-2013 Luc Saffre
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
This module contains "quick" tests that are run on a demo database 
without any fixture. You can run only these tests by issuing::

  python manage.py test pcsw.QuickTest

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

Person = dd.resolve_model('contacts.Person')
Property = dd.resolve_model('properties.Property')
PersonProperty = dd.resolve_model('properties.PersonProperty')
cv = dd.resolve_app('cv')
pcsw = dd.resolve_app('pcsw')
contacts = dd.resolve_app('contacts')
households = dd.resolve_app('households')

#~ from lino.apps.pcsw.models import Person
#~ from lino.modlib.cv.models import PersonProperty
#~ from lino.modlib.properties.models import Property



class QuickTest(TestCase):
    pass
    #~ def setUp(self):
        #~ settings.LINO.never_build_site_cache = True
        #~ super(DemoTest,self).setUp()
            
  
def test01(self):
    """
    Used on :doc:`/blog/2011/0414`.
    See the source code at :srcref:`/lino/apps/pcsw/tests/pcsw_tests.py`.
    """
    from lino.utils.dumpy import Serializer
    from lino.apps.pcsw.models import Company, CourseProvider
    ser = Serializer()
    #~ ser.models = [CourseProvider,Company]
    ser.models = [CourseProvider]
    ser.write_preamble = False
    self.assertEqual(Company._meta.parents,{})
    parent_link_field = CourseProvider._meta.parents.get(Company)
    #~ print parent_link_field.name
    #~ self.assertEqual(CourseProvider._meta.parents.get(Company),{})
    #~ self.assertEqual(CourseProvider._meta.parents,{})
    fields = [f.attname for f in CourseProvider._meta.fields]
    local_fields = [f.attname for f in CourseProvider._meta.local_fields]
    self.assertEqual(','.join(local_fields),'company_ptr_id')
    fields = [f.attname for f in Company._meta.fields]
    local_fields = [f.attname for f in Company._meta.local_fields]
    self.assertEqual(fields,local_fields)
    #~ self.assertTrue(','.join([f.attname for f in local_fields]),'company_ptr_id')
      
    #~ foo = Company(name='Foo')
    #~ foo.save()
    bar = CourseProvider(name='Bar')
    bar.save()
    
    #~ ser.serialize([foo,bar])
    ser.serialize([bar])
    #~ print ser.stream.getvalue()
    self.assertEqual(ser.stream.getvalue(),"""
def create_pcsw_courseprovider(company_ptr_id):
    return insert_child(Company.objects.get(pk=company_ptr_id),CourseProvider)


def pcsw_courseprovider_objects():
    yield create_pcsw_courseprovider(1)


def objects():
    for o in pcsw_courseprovider_objects(): yield o

from lino.apps.pcsw.migrate import install
install(globals())
""")
test01.skip = True

def test02(self):
    """
    Tests error handling when printing a contract whose type's 
    name contains non-ASCII char.
    Created :doc:`/blog/2011/0615`.
    See the source code at :srcref:`/lino/apps/pcsw/tests/pcsw_tests.py`.
    """
    from lino_welfare.modlib.jobs.models import Contracts, Contract, ContractType, JobProvider, Job
    #~ from lino.modlib.notes.models import ContractType
    from lino.mixins.printable import PrintAction
    from lino.modlib.users.models import User
    #~ from lino_welfare.modlib.pcsw.models import Person
    from lino_welfare.modlib.pcsw.models import Client
    root = User(username='root',language='en',profile='900') # ,last_name="Superuser")
    root.save()
    
    jp = JobProvider(name="Test")
    jp.save()
    person = Client(first_name="Max",last_name="Mustermann")
    person.full_clean()
    person.save()
    t = ContractType(id=1,build_method='pisa',template="",name=u'Art.60\xa77')
    t.save()
    job = Job(provider=jp,contract_type=t)
    #~ job = Job(contract_type=t,name="Test")
    job.save()
    n = Contract(id=1,job=job,user=root,client=person)
    n.full_clean()
    n.save()
    
    
    if 'en' in babel.AVAILABLE_LANGUAGES:
        root.language='en'
        root.save()
        url = '/api/jobs/Contract/1?an=do_print'
        response = self.client.get(url,REMOTE_USER='root',HTTP_ACCEPT_LANGUAGE='en')
        result = self.check_json_result(response,'success message alert')
        self.assertEqual(result['success'],False)
        self.assertEqual(result['alert'],True)
        self.assertEqual(
          result['message'],
          u"""\
Invalid template '' configured for ContractType u'Art.60\\xa77' (expected filename ending with '.pisa.html').""")

    

    
def test03(self):
    """
    Testing whether `/api/notes/NoteTypes/1?fmt=json` 
    has no item `templateHidden`.
    Created :doc:`/blog/2011/0509`.
    See the source code at :srcref:`/lino/apps/pcsw/tests/pcsw_tests.py`.
    """
    #~ from lino.apps.pcsw.models import NoteType
    from lino.modlib.notes.models import NoteType
    i = NoteType(build_method='appyodt',template="Default.odt",id=1)
    i.save()
    response = self.client.get('/api/notes/NoteTypes/1?fmt=json',REMOTE_USER='root')
    result = self.check_json_result(response,'data title navinfo disable_delete id')
    self.assertEqual(result['data']['template'],'Default.odt')
    self.assertEqual(result['data'].has_key('templateHidden'),False)
    
    response = self.client.get('/api/notes/NoteTypes/1?fmt=detail',REMOTE_USER='root')
    #~ print '\n'.join(response.content.splitlines()[:1])
    
    c = response.content
    
    #~ print c
    
    self.assertTrue(c.endswith('''\
<div id="body"></div>
</body></html>'''))

    if False:
        """
        TODO:
        expat has a problem to parse the HTML generated by Lino.
        Problem occurs near <div class="htmlText">...
        Note that even if the parseString gets through, we won't 
        have any INPUT elements since they will be added dynamically 
        by the JS code...
        """
        fd = file('tmp.html','w')
        fd.write(c)
        fd.close()
        
        from xml.dom import minidom 
        dom = minidom.parseString(c)
        print dom.getElementsByTagName('input')
        response = self.client.get('/api/lino/SiteConfigs/1?fmt=json')
        
        
def test04(self):
    """
    Test some features used in document templates.
    Created :doc:`/blog/2011/0615`.
    See the source code at :srcref:`/lino/apps/pcsw/tests/pcsw_tests.py`.
    """
    from lino.dd import Genders
    Company = dd.resolve_model('contacts.Company')
    Person = dd.resolve_model('contacts.Person')
    Country = dd.resolve_model('countries.Country')
    City = dd.resolve_model('countries.City')
    be = Country(isocode="BE",name="Belgique")
    be.save()
    bxl = City(name="Bruxelles",country=be)
    bxl.save()
    p = Person(
      first_name="Jean Louis",last_name="Dupont",
      street_prefix="Avenue de la", street="gare", street_no="3", street_box="b",
      city=bxl, gender=Genders.male
      )
    p.full_clean()
    p.save()
    
    if 'fr' in babel.AVAILABLE_LANGUAGES:
        babel.set_language('fr')
        #~ self.assertEqual(p.get_titled_name,"Mr Jean Louis DUPONT")
        self.assertEqual(p.full_name,"M. Jean Louis Dupont")
        self.assertEqual('\n'.join(p.address_lines()),u"""\
M. Jean Louis Dupont
Avenue de la gare 3 b
Bruxelles
Belgique""")
    
    
    babel.set_language(None)
        
        
def test05(self):
    """
    obj2str() caused a UnicodeDecodeError when called on an object that had 
    a ForeignKey field pointing to another instance whose __unicode__() 
    contained non-ascii characters.
    See :doc:`/blog/2011/0728`.
    """
    #~ from lino.apps.pcsw.models import Activity, Person
    from lino.core.modeltools import obj2str
    a = pcsw.Activity(name=u"Sozialhilfeempfänger")
    p = pcsw.Client(last_name="Test",activity=a)
    self.assertEqual(unicode(a),"Sozialhilfeempfänger")
    
    # Django pitfall: repr() of a model instance may return basestring containing non-ascii characters.
    self.assertEqual(type(repr(a)),str)

    # 
    self.assertEqual(obj2str(a,True),"Activity(name='Sozialhilfeempf\\xe4nger')")
    a.save()
    self.assertEqual(obj2str(a,True),"Activity(id=1,name='Sozialhilfeempf\\xe4nger')")
    
    expected = "Client(language='%s'," % babel.DEFAULT_LANGUAGE
    expected += "last_name='Test'"
    expected += ",client_state=ClientStates.newcomer:10"
    #~ expected += ",is_active=True"
    #~ expected += r",activity=Activity(name=u'Sozialhilfeempf\xe4nger'))"
    #~ expected += ",activity=1"
    expected += ")"
    self.assertEqual(obj2str(p,True),expected)
    p.pk = 5
    self.assertEqual(obj2str(p),"Client #5 (u'TEST  (5)')")
    
    
def test06(self):
    """
    :doc:`/blog/2011/1003`.
    The `id` field of a Company or Person was never disabled 
    because Lino didn't recognize it as the primary key.
    
    """
    from django.db import models
    #~ from lino.apps.pcsw.models import Person
    from lino.core.fields import get_data_elem
    de = get_data_elem(pcsw.Client,'id')
    #~ print de.__class__
    self.assertEqual(de.__class__,models.AutoField)
    self.assertEqual(de.primary_key,True)
    pk = Person._meta.pk
    self.assertEqual(pk.__class__,models.OneToOneField)
    self.assertEqual(pk.primary_key,True)
    self.assertEqual(pk.rel.field_name,'id')
    
    #~ self.assertEqual(de,pk)
    

def test07(self):
    """
    Bug 20120127 : VirtualFields had sneaked into wildcard columns.
    """
    #~ from lino.apps.pcsw.models import Companies
    wcde = [de.name for de in contacts.Companies.wildcard_data_elems()]
    #~ expected = '''\
#~ id country city name addr1 street_prefix street street_no street_box 
#~ addr2 zip_code region language email url phone gsm fax remarks 
#~ partner_ptr prefix vat_id type is_active newcomer is_deprecated activity 
#~ bank_account1 bank_account2 hourly_rate'''.split()
    expected = '''\
    id created modified country city region zip_code name addr1 street_prefix 
    street street_no street_box addr2 language email url phone gsm fax
    remarks is_obsolete activity bank_account1 bank_account2 partner_ptr 
    prefix vat_id type client_contact_type'''.split()
    s = ' '.join(wcde)
    #~ print s
    #~ print [de for de in Companies.wildcard_data_elems()]
    self.assertEqual(wcde,expected)
        

def test08(self):
    """
    Test disabled fields on imported partners
    """
    save_iip = settings.LINO.is_imported_partner
    def f(obj): return True
    settings.LINO.is_imported_partner = f
    
    
    def check_disabled(obj,df,names):
        for n in names.split():
            if not n in df:
                self.fail(
                  "Field %r expected to be disabled on imported %s" % (n,obj))
    def check_enabled(obj,df,names):
        for n in names.split():
            if n in df:
                self.fail(
                  "Field %r expected to be enabled on imported %s" % (n,obj))
    
    
    Person = dd.resolve_model('contacts.Person')
    p = Person(last_name="Test Person")
    p.save()
    url = '/api/contacts/Person/%d?an=detail&fmt=json' % p.pk
    response = self.client.get(url,REMOTE_USER='root') # ,HTTP_ACCEPT_LANGUAGE='en')
    result = self.check_json_result(response,'navinfo disable_delete data id title')
    df = result['data']['disabled_fields']
    check_disabled(p,df,'id first_name last_name bank_account1')
    check_enabled(p,df,'gsm')
                
    #~ from lino.apps.pcsw.models import Household
    from lino.modlib.households.models import Households
    h = pcsw.Household(name="Test Household")
    h.save()
    df = households.Households.disabled_fields(h,None)
    #~ print df
    check_disabled(h,df,'name bank_account1')
    check_enabled(h,df,'gsm type')
    
                
    # restore is_imported_partner method
    settings.LINO.is_imported_partner = save_iip

def test09(self):
    obj = pcsw.Client(pk=128,first_name="Erwin",last_name="Evertz")
    obj.full_clean()
    obj.save()
    ar = cv.SoftSkillsByPerson.request(master_instance=obj)
    self.assertEqual(ar.get_request_url(),"")

