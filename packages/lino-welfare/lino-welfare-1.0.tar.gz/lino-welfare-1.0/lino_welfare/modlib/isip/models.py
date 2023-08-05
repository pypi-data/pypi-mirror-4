# -*- coding: UTF-8 -*-
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
ISIP (Individualized Social Integration 
Projects, fr. "PIIS", german "VSE")
are contracts between a PCSW and a Client.

"""

import os
import cgi
import datetime

from django.db import models
#~ from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode 


from lino import dd
from lino.utils import dblogger
#~ from lino.utils import printable
from lino import mixins
#~ from lino.modlib.contacts import models as contacts
#~ from lino.modlib.notes import models as notes
notes = dd.resolve_app('notes')
contacts = dd.resolve_app('contacts')
pcsw = dd.resolve_app('pcsw')

#~ from lino.modlib.links import models as links
from lino.modlib.uploads import models as uploads
#~ from lino.utils.choicelists import HowWell
#~ from lino.modlib.properties.utils import KnowledgeField #, StrengthField
#~ from lino.modlib.uploads.models import UploadsByPerson
from lino.core.modeltools import get_field
from lino.core.modeltools import resolve_field
from lino.utils.babel import DEFAULT_LANGUAGE, babelattr, babeldict_getitem, language_choices
from lino.utils.htmlgen import UL
#~ from lino.utils.babel import add_babel_field, DEFAULT_LANGUAGE, babelattr, babeldict_getitem
from lino.utils import babel 
from lino.utils.choosers import chooser
from lino.utils.choicelists import ChoiceList
from lino.utils import mti
from lino.utils.ranges import isrange, overlap, overlap2, encompass, rangefmt
from lino.mixins.printable import DirectPrintAction
#~ from lino.mixins.reminder import ReminderEntry
from lino.core.modeltools import obj2str, models_by_abc

#~ from lino.modlib.cal.models import update_auto_task

#~ from lino.modlib.cal import models as cal

cal = dd.resolve_app('cal')

COACHINGTYPE_ASD = 1          


#~ class IntegTable(dd.Table):
  
    #~ @classmethod
    #~ def get_permission(self,action,user,obj):
        #~ if not user.integ_level:
            #~ return False
        #~ return super(IntegTable,self).get_permission(action,user,obj)
        

#
# CONTRACT TYPES 
#
class ContractType(mixins.PrintableType,babel.BabelNamed):
  
    """
    The contract type determines the print template to be used. 
    Print templates may use the `ref` field to conditionally 
    hide or show certain parts.
    `exam_policy` is the default ExamPolicy for new Contracts.
    """
    
    _lino_preferred_width = 20 
    
    templates_group = 'isip/Contract'
    
    class Meta:
        verbose_name = _("ISIP Type")
        verbose_name_plural = _('ISIP Types')
        
    ref = models.CharField(_("Reference"),max_length=20,blank=True)
    exam_policy = models.ForeignKey("isip.ExamPolicy",
        related_name="%(app_label)s_%(class)s_set",
        blank=True,null=True)
        

class ContractTypes(dd.Table):
    required=dict(user_groups = ['integ'],user_level='manager')
    model = ContractType
    column_names = 'name ref build_method template *'
    detail_layout = """
    id name 
    ref build_method template
    ContractsByType
    """



#
# EXAMINATION POLICIES
#
class ExamPolicy(babel.BabelNamed,cal.RecurrenceSet):
#~ class ExamPolicy(babel.BabelNamed,mixins.ProjectRelated,cal.RecurrenceSet):
    """
    Examination policy. 
    This also decides about automatic tasks to be created.
    """
    class Meta:
        verbose_name = _("Examination Policy")
        verbose_name_plural = _('Examination Policies')
        

class ExamPolicies(dd.Table):
    required=dict(user_groups = ['integ'],user_level='manager')
    model = ExamPolicy
    column_names = 'name *'

#
# CONTRACT ENDINGS
#
class ContractEnding(dd.Model):
    class Meta:
        verbose_name = _("Contract Ending")
        verbose_name_plural = _('Contract Endings')
        
    name = models.CharField(_("designation"),max_length=200)
    
    def __unicode__(self):
        return unicode(self.name)
        
class ContractEndings(dd.Table):
    required=dict(user_groups = ['integ'],user_level='manager')
    model = ContractEnding
    column_names = 'name *'
    order_by = ['name']




#~ class ContractBase(contacts.CompanyContact,mixins.DiffingMixin,mixins.TypedPrintable,cal.EventGenerator):
class ContractBase(
    #~ contacts.CompanyContact,
    contacts.ContactRelated,
    mixins.TypedPrintable,
    cal.EventGenerator):
    """
    Abstract base class for 
    :class:`lino_welfare.modlib.jobs.models.Contract`
    and
    :class:`lino_welfare.modlib.isip.models.Contract`
    """
    
    TASKTYPE_CONTRACT_APPLIES_UNTIL = 1
    
    class Meta:
        abstract = True
        
    #~ eventgenerator = models.OneToOneField(cal.EventGenerator,
        #~ related_name="%(app_label)s_%(class)s_ptr",
        #~ parent_link=True)
  
    #~ person = models.ForeignKey(settings.LINO.person_model,
    client = models.ForeignKey('pcsw.Client',
        related_name="%(app_label)s_%(class)s_set_by_client")
        
    language = babel.LanguageField()
    
    applies_from = models.DateField(_("applies from"),blank=True,null=True)
    applies_until = models.DateField(_("applies until"),blank=True,null=True)
    date_decided = models.DateField(blank=True,null=True,verbose_name=_("date decided"))
    date_issued = models.DateField(blank=True,null=True,verbose_name=_("date issued"))
    
    user_asd = models.ForeignKey("users.User",
        verbose_name=_("responsible (ASD)"),
        related_name="%(app_label)s_%(class)s_set_by_user_asd",
        #~ related_name='contracts_asd',
        blank=True,null=True) 
    
    exam_policy = models.ForeignKey("isip.ExamPolicy",
        related_name="%(app_label)s_%(class)s_set",
        blank=True,null=True)
        
    ending = models.ForeignKey("isip.ContractEnding",
        related_name="%(app_label)s_%(class)s_set",
        blank=True,null=True,
        verbose_name=_("Ending"))
    date_ended = models.DateField(blank=True,null=True,verbose_name=_("date ended"))
    
    #~ def summary_row(self,ui,rr,**kw):
    def summary_row(self,ar,**kw):
        s = ar.href_to(self)
        #~ s += " (" + ui.href_to(self.person) + ")"
        #~ s += " (" + ui.href_to(self.person) + "/" + ui.href_to(self.provider) + ")"
        return s
            
    def __unicode__(self):
        #~ return u'%s # %s' % (self._meta.verbose_name,self.pk)
        #~ return u'%s#%s (%s)' % (self.job.name,self.pk,
            #~ self.person.get_full_name(salutation=False))
        return u'%s#%s (%s)' % (self._meta.verbose_name,self.pk,
            self.client.get_full_name(salutation=False))
    
    #~ def __unicode__(self):
        #~ msg = _("Contract # %s")
        #~ # msg = _("Contract # %(pk)d (%(person)s/%(company)s)")
        #~ # return msg % dict(pk=self.pk, person=self.person, company=self.company)
        #~ return msg % self.pk
        
    def get_recipient(self):
        contact = self.get_contact()
        #~ if self.contact_person:
        if contact is not None:
            #~ contacts = self.get_contact_set()
            return contact
        if self.company:
            return self.company
        return self.client
    recipient = property(get_recipient)
    
    # backwards compat for document templates
    def get_person(self): 
        return self.client
    person = property(get_person)
        
        
    #~ @classmethod
    #~ def contact_choices_queryset(cls,company):
        #~ return contacts.Role.objects.filter(
            #~ type__use_in_contracts=True,
            #~ company=company)

    @classmethod
    def contact_person_choices_queryset(cls,company):
        return settings.LINO.person_model.objects.filter(rolesbyperson__company=company,
            rolesbyperson__type__use_in_contracts=True)
            
    @dd.chooser()
    def contact_role_choices(cls):
        return contacts.RoleType.objects.filter(use_in_contracts=True)
        
        

    #~ def dsbe_person(self): removed 20120921 because no longer used
        #~ """Used in document templates."""
        #~ if self.person_id is not None:
            #~ if self.person.coach2_id is not None:
                #~ return self.person.coach2_id
            #~ return self.person.coach1 or self.user
            
    def client_changed(self,request):
        """
        If the contract's author is the client's primary coach, 
        then set user_asd to None,
        otherwise set user_asd to the primary coach.
        We suppose that only integration agents write contracts.
        """
        if self.client_id is not None:
            #~ pc = self.person.get_primary_coach()
            #~ qs = self.person.get_coachings(self.applies_from,active=True)
            qs = self.client.get_coachings(self.applies_from,type__id=COACHINGTYPE_ASD)
            if qs.count() == 1:
                user_asd = qs[0].user
                if user_asd is None or user_asd == self.user:
                #~ if self.person.coach1_id is None or self.person.coach1_id == self.user_id:
                    self.user_asd = None
                else:
                    self.user_asd = user_asd
                
    def on_create(self,ar):
        super(ContractBase,self).on_create(ar)
        self.client_changed(ar)
      
                    
    def full_clean(self,*args,**kw):
        r = self.active_period()
        if not isrange(*r):
            raise ValidationError(u'Contract ends before it started.')
        
        if self.type_id and self.type.exam_policy_id:
            if not self.exam_policy_id:
                self.exam_policy_id = self.type.exam_policy_id
        # The severe test is ready and now also activated :
        if True:
          if self.client_id is not None:
            msg = OverlappingContractsTest(self.client).check(self)
            if msg:
                raise ValidationError(msg)
            
        super(ContractBase,self).full_clean(*args,**kw)
        

    def update_owned_instance(self,other):
        #~ mixins.Reminder.update_owned_task(self,task)
        #~ contacts.PartnerDocument.update_owned_task(self,task)
        #~ task.company = self.company
        if isinstance(other,mixins.ProjectRelated):
            other.project = self.client
        super(ContractBase,self).update_owned_instance(other)
        
    def after_update_owned_instance(self,other):
        if other.is_user_modified():
            self.update_reminders()
        
        
    def update_cal_rset(self):
        return self.exam_policy
        
    def update_cal_from(self):
        return self.applies_from
        
    def update_cal_calendar(self,i):
        #~ return self.exam_policy.event_type
        return self.exam_policy.calendar
        
    def update_cal_until(self):
        return self.date_ended or self.applies_until
        
    def update_cal_subject(self,i):
        return _("Evaluation %d") % i
        
    def update_reminders(self):
        super(ContractBase,self).update_reminders()
        if self.applies_until:
            date = cal.DurationUnits.months.add_duration(self.applies_until,-1)
        else:
            date = None
        cal.update_auto_task(
          self.TASKTYPE_CONTRACT_APPLIES_UNTIL,
          self.user,
          date,
          _("Contract ends in a month"),
          self)
          #~ alarm_value=1,alarm_unit=DurationUnit.months)
        
                        
              
    #~ def overlaps_with(self,b):
        #~ if b == self: 
            #~ return False
        #~ a1 = self.applies_from
        #~ a2 = self.date_ended or self.applies_until
        #~ b1 = b.applies_from
        #~ b2 = b.date_ended or b.applies_until
        #~ return overlap(a1,a2,b1,b2)
        
    def active_period(self):
        return (self.applies_from, self.date_ended or self.applies_until)
        #~ r = (self.applies_from, self.date_ended or self.applies_until)
        #~ if isrange(r): return r
        #~ return None
        
        
    #~ def data_control(self):
        #~ msgs = []
        #~ for model in models_by_abc(ContractBase):
            #~ for con in model.objects.filter(person=self.person):
                #~ if self.overlaps_with(con):
                    #~ msgs.append(_("Dates overlap with %s") % con)
        #~ return msgs

#~ dd.update_field(ContractBase,'contact_person',verbose_name=_("represented by"))


class ContractBaseTable(dd.Table):
  
    parameters = dict(
      user = dd.ForeignKey(settings.LINO.user_model,blank=True),
      show_past = models.BooleanField(_("past contracts"),default=True),
      show_active = models.BooleanField(_("active contracts"),default=True),
      show_coming = models.BooleanField(_("coming contracts"),default=True),
      today = models.DateField(_("on"),blank=True,default=datetime.date.today),
    )
    
    params_layout = """user type show_past show_active show_coming today"""
    params_panel_hidden = True
    
    @classmethod
    def get_request_queryset(cls,rr):
        #~ logger.info("20120608.get_request_queryset param_values = %r",rr.param_values)
        qs = super(ContractBaseTable,cls).get_request_queryset(rr)
        #~ user = rr.param_values.get('user',None)
        if rr.param_values.user:
            qs = qs.filter(user=rr.param_values.user)
        if rr.param_values.type:
            qs = qs.filter(type=rr.param_values.type)
        today = rr.param_values.today or datetime.date.today()
        #~ today = rr.param_values.get('today',None) or datetime.date.today()
        #~ show_active = rr.param_values.get('show_active',True)
        if today:
            if not rr.param_values.show_active:
                flt = range_filter(today,'applies_from','applies_until')
                #~ logger.info("20120114 flt = %r",flt)
                qs = qs.exclude(flt)
            #~ show_past = rr.param_values.get('show_past',True)
            if not rr.param_values.show_past:
                qs = qs.exclude(applies_until__isnull=False,applies_until__lt=today)
            #~ show_coming = rr.param_values.get('show_coming',True)
            if not rr.param_values.show_coming:
                qs = qs.exclude(applies_from__isnull=False,applies_from__gt=today)
        return qs
    
    


class OverlappingContractsTest:
    """
    Volatile object used to test for overlapping contracts.
    """
    def __init__(self,client):
        """
        Test whether this client has overlapping contracts.
        """
        #~ from lino_welfare.modlib.isip.models import ContractBase
        self.client = client
        self.actives = []
        for model in models_by_abc(ContractBase):
            for con1 in model.objects.filter(client=client):
                p1 = con1.active_period()
                #~ if p1:
                self.actives.append((p1,con1))
        
    def check(self,con1):
        ap = con1.active_period()
        if ap[0] is None and ap[1] is None:
            return
        if False:
            cp = (self.client.coached_from,self.client.coached_until)
            if not encompass(cp,ap):
                return _("Date range %(p1)s lies outside of coached period %(p2)s.") \
                    % dict(p2=rangefmt(cp),p1=rangefmt(ap))
        for (p2,con2) in self.actives:
            if con1 != con2 and overlap2(ap,p2):
                return _("Date range overlaps with %(ctype)s #%(id)s") % dict(
                  ctype=con2.__class__._meta.verbose_name,
                  id=con2.pk
                )
        return None
        
    def check_all(self):
        messages = []
        for (p1,con1) in self.actives:
            msg = self.check(con1)
            if msg:
                messages.append(
                  _("%(ctype)s #%(id)s : %(msg)s") % dict(
                    msg=msg,
                    ctype=con1.__class__._meta.verbose_name,
                    id=con1.pk))
        return messages
        

            
    
class Contract(ContractBase):
    """
    ISIP = Individual Social Integration Project (VSE)
    """
    class Meta:
        verbose_name = _("ISIP")
        verbose_name_plural = _("ISIPs")
        
    type = models.ForeignKey("isip.ContractType",
        related_name="%(app_label)s_%(class)s_set_by_type",
        verbose_name=_("Contract Type"),blank=True)
    
    stages = dd.RichTextField(_("stages"),
        blank=True,null=True,format='html')
    goals = dd.RichTextField(_("goals"),
        blank=True,null=True,format='html')
    duties_asd = dd.RichTextField(_("duties ASD"),
        blank=True,null=True,format='html')
    duties_dsbe = dd.RichTextField(_("duties DSBE"),
        blank=True,null=True,format='html')
    duties_company = dd.RichTextField(_("duties company"),
        blank=True,null=True,format='html')
    duties_person = dd.RichTextField(_("duties person"),
        blank=True,null=True,format='html')
    
    @classmethod
    def site_setup(cls,lino):
        """
        Here's how to override the default verbose_name of a field.
        """
        #~ resolve_field('dsbe.Contract.user').verbose_name=_("responsible (DSBE)")
        Contract.user.verbose_name=_("responsible (DSBE)")
        #~ lino.CONTRACT_PRINTABLE_FIELDS = dd.fields_list(cls,
        cls.PRINTABLE_FIELDS = dd.fields_list(cls,
            'client company contact_person contact_role type '
            'applies_from applies_until '
            'language '
            'stages goals duties_dsbe duties_company '
            'duties_asd duties_person '
            'user user_asd exam_policy '
            'date_decided date_issued ')
        #~ super(Contract,cls).site_setup(lino)
        
    def disabled_fields(self,ar):
        #~ if self.must_build:
        if not self.build_time:
            return []
        #~ return df + settings.LINO.CONTRACT_PRINTABLE_FIELDS
        return self.PRINTABLE_FIELDS


class ContractDetail(dd.FormLayout):    
    general = dd.Panel("""
    id:8 client:25 user:15 user_asd:15 language:8
    type company contact_person contact_role
    applies_from applies_until exam_policy
    
    date_decided date_issued 
    date_ended ending
    cal.TasksByController cal.EventsByController
    """,label = _("General"))
    
    isip = dd.Panel("""
    stages        goals
    duties_asd    duties_dsbe
    duties_company duties_person
    """,label = _("ISIP"))
    
    main = "general isip"
    
    #~ def setup_handle(self,dh):
        #~ dh.general.label = _("General")
        #~ dh.isip.label = _("ISIP")


class Contracts(ContractBaseTable):
    required = dict(user_groups='integ')
    model = Contract
    column_names = 'id applies_from applies_until client user type *'
    order_by = ['id']
    #~ active_fields = ('company','contact')
    active_fields = ['company']
    detail_layout = ContractDetail()
    insert_layout = dd.FormLayout("""
    client
    type company
    """,window_size=(60,'auto'))    
    parameters = dict(
      type = models.ForeignKey(ContractType,blank=True,verbose_name=_("Only contracts of type")),
      **ContractBaseTable.parameters)
    

class MyContracts(Contracts):
#~ class MyContracts(Contracts,mixins.ByUser):
    #~ column_names = "applies_from client *"
    #~ label = _("My ISIP contracts")
    #~ label = _("My PIIS contracts")
    #~ order_by = "reminder_date"
    #~ column_names = "reminder_date client company *"
    #~ order_by = ["applies_from"]
    #~ filter = dict(reminder_date__isnull=False)
      
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(MyContracts,self).param_defaults(ar,**kw)
        kw.update(user=ar.get_user())
        return kw
      


    
class ContractsByPerson(Contracts):
    master_key = 'client'
    column_names = 'applies_from applies_until user type *'

        
class ContractsByType(Contracts):
    master_key = 'type'
    column_names = "applies_from client user *"
    order_by = ["applies_from"]



def setup_main_menu(site,ui,user,m): 
    m  = m.add_menu("integ",pcsw.INTEG_MODULE_LABEL)
    m.add_action(MyContracts)
    
def setup_master_menu(site,ui,user,m): pass

def setup_my_menu(site,ui,user,m): pass
    #~ m.add_action(MyContracts)
  
def setup_config_menu(site,ui,user,m): 
    #~ m  = m.add_menu("isip",_("ISIPs"))
    m  = m.add_menu("integ",pcsw.INTEG_MODULE_LABEL)
    m.add_action(ContractTypes)
    m.add_action(ContractEndings)
    m.add_action(ExamPolicies)
  
def setup_explorer_menu(site,ui,user,m):
    m.add_action(Contracts)
