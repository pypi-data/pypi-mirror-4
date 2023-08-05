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

import logging
logger = logging.getLogger(__name__)

import os
import sys
import cgi
import datetime
import decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.utils.encoding import force_unicode


from lino import tools
from lino import dd
from lino.core import changes
#~ from lino.utils.babel import default_language
#~ from lino import reports
#~ from lino import layouts
#~ from lino.core.perms import UserProfiles, UserLevels
from lino.utils.restify import restify
#~ from lino.utils import printable

from lino.utils.choosers import chooser
from lino.utils import babel
from lino import mixins
from django.conf import settings
#~ from lino import choices_method, simple_choices_method
#~ from lino.modlib.contacts import models as contacts
#~ from lino.modlib.users import models as users
from lino.modlib.cal.utils import amonthago


#~ from lino_welfare.models import Person
#~ from lino_welfare.modlib.pcsw import models as welfare
#~ from lino_welfare.modlib.pcsw import models as pcsw

users = dd.resolve_app('users')
contacts = dd.resolve_app('contacts')
pcsw = dd.resolve_app('pcsw')
outbox = dd.resolve_app('outbox')

MODULE_LABEL = _("Newcomers")

class Broker(dd.Model):
    """
    A Broker (Vermittler) is an external institution 
    who suggests newcomers.
    """
    class Meta:
        verbose_name = _("Broker")
        verbose_name_plural = _("Brokers")
        
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

class Brokers(dd.Table):
    """
    List of Brokers on this site.
    """
    required=dict(user_groups=['newcomers'],user_level='manager')
    #~ required_user_level = UserLevels.manager
    model = Broker
    column_names = 'name *'
    order_by = ["name"]



class Faculty(babel.BabelNamed):
    """
    A Faculty (Fachbereich) is a conceptual (not organizational)
    department of this PCSW. 
    Each Newcomer will be assigned to one and only one Faculty, 
    based on his/her needs.
    
    """
    class Meta:
        verbose_name = _("Faculty")
        verbose_name_plural = _("Faculties")
    #~ body = babel.BabelTextField(_("Body"),blank=True,format='html')
    

class Faculties(dd.Table):
    required=dict(user_groups=['newcomers'],user_level='manager')
    #~ required_user_groups = ['newcomers']
    #~ required_user_level = UserLevels.manager
    model = Faculty
    column_names = 'name *'
    order_by = ["name"]
    detail_layout = """
    id name
    CompetencesByFaculty
    ClientsByFaculty
    """

class Competence(mixins.AutoUser,mixins.Sequenced):
    """
    Deserves more documentation.
    """
    class Meta:
        #~ abstract = True
        verbose_name = _("Competence") 
        verbose_name_plural = _("Competences")
        
    faculty = models.ForeignKey(Faculty)
    
    def __unicode__(self):
        return u'%s #%s' % (self._meta.verbose_name,self.pk)
        
class Competences(dd.Table):
    required = dict(user_groups=['newcomers'],user_level='manager')
    #~ required_user_groups = ['newcomers']
    #~ required_user_level = UserLevels.manager
    model = Competence
    column_names = 'id *'
    order_by = ["id"]

class CompetencesByUser(Competences):
    #~ required = dict(user_groups=['newcomers'])
    required = dict()
    #~ required_user_level = None
    master_key = 'user'
    column_names = 'seqno faculty *'
    order_by = ["seqno"]

class CompetencesByFaculty(Competences):
    master_key = 'faculty'
    column_names = 'user *'
    order_by = ["user"]


class MyCompetences(mixins.ByUser,CompetencesByUser):
    pass

    
#~ class Newcomers(pcsw.Clients):
    #~ """
    #~ Clients who have the "Newcomer" checkbox on.
    #~ """
    #~ required = dict(user_groups=['newcomers'])
    
    #~ use_as_default_table = False
    #~ column_names = "name_column broker faculty address_column *"
    
    #~ label = _("Newcomers")
    
    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(Newcomers,self).param_defaults(ar,**kw)
        #~ kw.update(client_state=pcsw.ClientStates.newcomer)
        #~ kw.update(coached_on=None)
        #~ return kw
        
    
        
#~ class NewcomersByFaculty(Newcomers):
    #~ master_key = 'faculty'
    #~ column_names = "name_column broker address_column *"
        
#~ class NewClientDetail(pcsw.ClientDetail):
    #~ main = "newcomers " + pcsw.ClientDetail.main
    
    #~ newcomers = dd.Panel("""
    #~ broker:12 faculty:12  
    #~ workflow_buttons
    #~ newcomers.AvailableCoachesByClient
    #~ """,label=_(newcomers.MODULE_LABEL))

#~ print pcsw, dir(pcsw)



class NewClients(pcsw.Clients):
    required = dict(user_groups=['newcomers'])
    #~ required_user_groups = ['newcomers']
    label = _("New Clients")
    use_as_default_table = False
    
    help_text = u"""\
Liste der neuen Klienten zwecks Zuweisung 
eines Begleiters oder Ablehnen des Hilfeantrags."""
    
    #~ detail_layout = NewClientDetail()
    
    column_names = "name_column:20 client_state broker faculty national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type language:10 *"
    
    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(NewClients,self).param_defaults(ar,**kw)
        #~ kw.update(new_since=amonthago())
        #~ return kw
        
        
    parameters = dict(
      also_refused = models.BooleanField(_("Also refused clients"),
          default=False),
      also_obsolete = models.BooleanField(
          _("Also deprecated clients"),
          default=False),
      #~ new_since = models.DateField(_("New clients since"),blank=True),
      new_since = models.DateField(_("Also newly coached clients since"),
          #~ default=amonthago,
          blank=True,null=True,help_text=u"""\
Auch Klienten, die erst seit Kurzem begleitet sind."""),
      coached_by = models.ForeignKey(users.User,
          blank=True,null=True,
          verbose_name=_("Coached by")),
      #~ coached_on = models.DateField(_("Coached on"),blank=True,null=True),
      )
    params_layout = 'also_refused also_obsolete new_since coached_by'
    
    @classmethod
    def get_request_queryset(self,ar):
        # Note that we skip pcsw.Clients mro parent
        #~ qs = super(pcsw.Clients,self).get_request_queryset(ar)
        qs = super(contacts.Persons,self).get_request_queryset(ar)
        #~ qs = dd.Table.get_request_queryset(ar)
        
        q = models.Q(client_state=pcsw.ClientStates.newcomer)
        
        if ar.param_values.also_refused:
            q = q | models.Q(client_state=pcsw.ClientStates.refused)
        #~ q = models.Q(client_state__in=(pcsw.ClientStates.new,pcsw.ClientStates.refused))
        if ar.param_values.new_since:
            q = q | models.Q(
                client_state=pcsw.ClientStates.coached,
                coachings_by_client__start_date__gte=ar.param_values.new_since)
        qs = qs.filter(q)

        if ar.param_values.coached_by:
            qs = pcsw.only_coached_by(qs,ar.param_values.coached_by)
        if not ar.param_values.also_obsolete:
            qs = qs.filter(is_obsolete=False)
        #~ if not ar.param_values.also_refused:
            #~ qs = qs.filter(client_status=False)
        #~ logger.info('20120914 Clients.get_request_queryset --> %d',qs.count())
        return qs

    @classmethod
    def get_title_tags(self,ar):
        if ar.param_values.also_refused:
            yield unicode(self.parameters['also_refused'].verbose_name)
        if ar.param_values.also_obsolete:
            yield unicode(self.parameters['also_obsolete'].verbose_name)
            #~ tags.append(unicode(_("obsolete")))
        if ar.param_values.new_since:
            yield unicode(self.parameters['new_since'].verbose_name) + ' ' + babel.dtos(ar.param_values.new_since)
        if ar.param_values.coached_by:
            yield unicode(self.parameters['coached_by'].verbose_name) + ' ' + unicode(ar.param_values.coached_by)
      
        
        
        
class ClientsByFaculty(pcsw.Clients):
    master_key = 'faculty'
    column_names = "name_column broker address_column *"
    
    
        
class AvailableCoaches(users.Users):
    """
    A list of the Users that are susceptible to become responsible for a Newcomer.
    """
    use_as_default_table = False
    required = dict(user_groups=['newcomers'])
    #~ required_user_groups = ['newcomers']
    #~ model = users.User
    editable = False # even root should not edit here
    #~ filter = models.Q(profile__in=[p for p in UserProfiles.items() if p.integ_level])
    #~ label = _("Users by Newcomer")
    label = _("Available Coaches")
    column_names = 'name_column workflow_buttons:10 primary_clients active_clients new_clients newcomer_quota workload'
    parameters = dict(
        for_client = models.ForeignKey('contacts.Person',
            verbose_name=_("Show suggested agents for"),
            blank=True),
        since = models.DateField(_("Count Newcomers since"),
            blank=True,default=amonthago),
    )
    params_layout = "for_client since"
    
    @chooser()
    def for_client_choices(cls):
        return NewClients.request().data_iterator
        
    @classmethod
    def get_request_queryset(self,ar):
        profiles = [p for p in dd.UserProfiles.items() if p.integ_level]
        return super(AvailableCoaches,self,ar).filter(models.Q(profile__in=profiles))
        
        
        
    @classmethod
    def get_data_rows(self,ar):
        client = ar.param_values.for_client
        if client:
            if client.client_state != pcsw.ClientStates.newcomer:
                raise Warning(_("Only for newcomers"))
            if not pcsw.is_valid_niss(client.national_id):
                raise Warning(_("Only for newcomers with valid SSIN"))
            if not client.faculty:
                raise Warning(_("Only for newcomers with given `faculty`."))

        data = []
        qs = super(AvailableCoaches,self).get_request_queryset(ar)
        for user in qs:
            if client:
                r = Competence.objects.filter(user=user,faculty=client.faculty)
                if r.count() == 0:
                    continue
            #~ else:
                #~ logger.info("20120928 AvailableCoaches.get_data_rows : no for_client")
            user.new_clients = NewClients.request(
              ar.ui,param_values=dict(
                coached_by=user,
                new_since=ar.param_values.since))
            #~ yield user
            data.append(user)
            
        if client and len(data) == 0:
            raise Warning(_("No coaches available for %s.") % client.faculty)
            
        def fn(a,b):
            return cmp(self.compute_workload(ar,a),self.compute_workload(ar,b))
        data.sort(fn)
        return data
                
    #~ @dd.virtualfield('contacts.Person.coach1')
    #~ def user(self,obj,ar):
        #~ return obj
        
    @dd.requestfield(_("Primary clients"))
    def primary_clients(self,obj,ar):
        #~ return pcsw.ClientsByCoach1.request(ar.ui,master_instance=obj)
        return pcsw.CoachingsByUser.request(ar.ui,master_instance=obj)
        
    @dd.requestfield(_("Active clients"))
    def active_clients(self,obj,ar):
        #~ return pcsw.MyActiveClients.request(ar.ui,subst_user=obj)
        return pcsw.IntegClients.request(ar.ui,param_values=dict(coached_by=obj,only_active=True))
        
    @dd.requestfield(_("New Clients"))
    def new_clients(self,obj,ar):
        return obj.new_clients
        
    @dd.virtualfield(models.CharField(_("Workload"),max_length=6))
    def workload(self,obj,ar):
        return "%+6.2f%%" % self.compute_workload(ar,obj)
        
    #~ @dd.virtualfield(models.DecimalField(_("Workload"),max_digits=6,decimal_places=2))
    #~ def workload(self,obj,ar):
        #~ return self.compute_workload(ar,obj)
        
    #~ @dd.virtualfield(models.IntegerField(_("Quote")))
    #~ def workload(self,obj,ar):
        #~ if obj.new_clients.get_total_count():
            #~ return 100 * obj.newcomer_quota / obj.new_clients.get_total_count()
        #~ else:
            #~ return None
    @classmethod    
    def compute_workload(cls,ar,obj):
        delta = datetime.date.today() - ar.param_values.since
        quota = obj.newcomer_quota * delta.days / decimal.Decimal('7.0')
        return decimal.Decimal(obj.new_clients.get_total_count() - quota)
    
class AssignCoach(dd.NotifyingAction):
    label=_("Assign")
    show_in_workflow = True
    help_text = u"""\
Diesen Benutzer als Begleiter für diesen Klienten eintragen 
und den Zustand des Klienten auf "Begleitet" setzen.
Anschließend wird der Klient in der Liste "Neue Klienten" 
nicht mehr angezeigt."""
    
    def get_notify_subject(self,ar,obj,**kw):
        #~ return _('New client for %s') % obj
        client = ar.master_instance
        if client:
            return _('%(client)s assigned to %(coach)s ') % dict(
                client=client,coach=obj)
            
    def get_notify_body(self,ar,obj,**kw):
        client = ar.master_instance
        if client:
            #~ return _("%(coach)s has been assigned as %(faculty)s coach for client %(client)s.") % dict(
                #~ client=client,coach=obj,faculty=client.faculty)
            return _("%(client)s is now coached by %(coach)s for %(faculty)s.") % dict(
                client=client,coach=obj,faculty=client.faculty)
            
    def unused_get_action_permission(self,ar,obj,state):
        #~ logger.info("20121020 get_action_permission %s",ar.master_instance)
        if not pcsw.is_valid_niss(ar.master_instance.national_id):
            #~ logger.info("20121016 %s has invalid NISS ",ar.master_instance)
            return False
            #~ _("Cannot assign client %(client)s with invalid NISS %(niss)s.") 
                #~ % dict(client=client,niss=client.national_id))
        return super(AssignCoach,self).get_action_permission(ar,obj,state)
        #~ return super(AssignCoach,self).get_row_permission(ar,state,ba)
        
    def run(self,obj,ar,**kw):
        """
        Assign a coach to a newcomer.
        """
        client = ar.master_instance
        watcher = changes.Watcher(client)
        #~ if not pcsw.is_valid_niss(client.national_id):
            #~ return ar.error_response(alert=True,
                #~ message=_("Cannot assign client %(client)s with invalid NISS %(niss)s.") 
                #~ % dict(client=client,niss=client.national_id))
                
        #~ ar.confirm(msg,_("Are you sure?"))
        
        coaching = pcsw.Coaching(client=client,user=obj,
            start_date=datetime.date.today(),
            type=obj.coaching_type)
            #~ state=pcsw.CoachingStates.active)
        #~ if not obj.profile:
            #~ coaching.state = pcsw.CoachingStates.active
        coaching.save()
        changes.log_create(ar.request,coaching)
        client.client_state = pcsw.ClientStates.coached
        client.full_clean()
        client.save()
        watcher.log_diff(ar.request)
        
        self.add_system_note(ar,coaching)
        
        #~ msg = _("Client %(client)s has been assigned to %(coach)s") % dict(client=client,coach=obj)
        #~ return ar.success_response(refresh_all=True,message=msg,alert=True,**kw)
        return ar.success_response(ar.action_param_values.notify_body,alert=True,refresh_all=True,**kw)
        #~ kw.update(refresh_all=True)
        #~ return kw
    

class AvailableCoachesByClient(AvailableCoaches):
    #~ master_key = 'for_client'
    master = pcsw.Client
    label = _("Available Coaches")
    
    assign_coach = AssignCoach()
    
    #~ slave_grid_format = 'html'
    editable = False
    hide_sums = True

    @classmethod
    def get_data_rows(self,ar):
        ar.param_values.for_client = ar.master_instance
        return super(AvailableCoachesByClient,self).get_data_rows(ar)
        
    #~ @dd.action(label=_("Assign"))
    #~ def assign_coach(obj,ar,**kw):
        #~ """
        #~ Assign a coach to a newcomer.
        #~ """
        #~ client = ar.master_instance
        #~ if not pcsw.is_valid_niss(client.national_id):
            #~ return ar.error_response(alert=True,
                #~ message=_("Cannot assign client %(client)s with invalid NISS %(niss)s.") 
                #~ % dict(client=client,niss=client.national_id))
        #~ msg = _("Assign client %(client)s for coaching by %(user)s.") % dict(client=client,user=obj)
        #~ ar.confirm(msg,_("Are you sure?"))
        
        
        #~ coaching = pcsw.Coaching(client=client,user=obj,
            #~ start_date=datetime.date.today(),
            #~ type=obj.coaching_type,
            #~ state=pcsw.CoachingStates.suggested)
        #~ if not obj.profile:
            #~ coaching.state = pcsw.CoachingStates.active
        #~ coaching.save()
        #~ client.client_state = pcsw.ClientStates.coached
        #~ client.full_clean()
        #~ client.save()
        #~ msg = _("Client %(client)s has been assigned to %(user)s") % dict(client=client,user=obj)
        
        #~ recipients = []
        #~ recipients.append(
            #~ dict(name=unicode(obj),address=obj.email,type=outbox.RecipientType.to))
        #~ for u in settings.LINO.user_model.objects.filter(coaching_supervisor=True):
            #~ recipients.append(
                #~ dict(name=unicode(u),address=u.email,type=outbox.RecipientType.to))
            
        #~ if len(recipients):
            #~ m = outbox.Mail(user=ar.get_user(),
                #~ subject=_('Newcomer has been assigned'),
                #~ body = """Hallo Kollege,\n%s""" % msg,
                #~ project=client,
                #~ owner=coaching)
            #~ m.full_clean()
            #~ m.save()
            #~ # for t,p in [(outbox.RecipientType.to,obj.partner)]:
            #~ for rec in recipients:
                #~ r = outbox.Recipient(mail=m,**rec)
                #~ r.full_clean()
                #~ r.save()
            #~ m.send_mail.run(m,ar)
            #~ interactive = (ar.get_user().profile.office_level > dd.UserLevels.user)
            #~ if interactive:
                #~ js = ar.renderer.instance_handler(ar,m)
                #~ kw.update(eval_js=js)
        #~ return ar.success_response(refresh_all=True,message=msg,alert=True,**kw)
        
        



#~ def customize_pcsw():
    #~ pcsw.ClientDetail.main.replace('general status_tab','general newcomers status_tab')
    #~ pcsw.ClientDetail.newcomers = dd.Panel("""
    #~ broker:12 faculty:12  
    #~ workflow_buttons
    #~ newcomers.AvailableCoachesByClient
    #~ """,label=MODULE_LABEL,required=dict(user_groups='newcomers'))
    




#~ settings.LINO.add_user_field('newcomers_level',UserLevels.field(MODULE_LABEL))
#~ settings.LINO.add_user_group('newcomers',MODULE_LABEL)
settings.LINO.add_user_field('newcomer_quota',models.IntegerField(
          _("Newcomers Quota"),
          default=0,
          help_text=u"""\
Wieviele Neuanträge dieser Benutzer pro Monat verkraften kann."""))


dd.inject_field(pcsw.Client,
    'broker',
    models.ForeignKey(Broker,
        blank=True,null=True),
    """The Broker who sent this Newcomer.
    """)
dd.inject_field(pcsw.Client,
    'faculty',
    models.ForeignKey(Faculty,
        blank=True,null=True),
    """The Faculty this client has been attributed to.
    """)

def site_setup(site):
    #~ site.modules.users.Users.add_detail_tab('newcomers.CompetencesByUser')
    #~ site.modules.pcsw.Clients.add_detail_tab('newcomers',"""
    #~ broker:12 faculty:12  
    #~ workflow_buttons
    #~ newcomers.AvailableCoachesByClient
    #~ """,MODULE_LABEL,required=dict(user_groups='newcomers'))
    
    #~ site.modules.pcsw.Clients.detail_layout.coaching.replace('coaching_left',"""
    #~ coaching_left
    #~ newcomers_left newcomers.AvailableCoachesByClient
    #~ """)
    
    site.modules.pcsw.Clients.detail_layout.coaching.replace('workflow_buttons',"""
    newcomers_left:20 newcomers.AvailableCoachesByClient:40
    """)
    
    site.modules.pcsw.Clients.detail_layout.update(newcomers_left="""
    workflow_buttons
    broker:12 
    faculty:12  
    """)
    
    #~ coaching = dd.Panel("""
    #~ pcsw.ContactsByClient:40 pcsw.CoachingsByClient:40
    #~ """,label=_("Coaching"))
    
    #~ coaching_left = """
    #~ group:16 job_agents
    #~ """
    
    
  
def setup_main_menu(site,ui,user,m):
    #~ if user.profile.newcomers_level < UserLevels.user:
        #~ return
    m  = m.add_menu("newcomers",MODULE_LABEL)
    #~ m  = m.add_menu("pcsw",pcsw.MODULE_LABEL)
    #~ m.add_action(Newcomers)
    m.add_action(NewClients)
            
  
def setup_master_menu(site,ui,user,m): pass
  
def setup_my_menu(site,ui,user,m): 
    pass
    
def setup_config_menu(site,ui,user,m): 
    #~ if user.profile.newcomers_level < UserLevels.manager:
        #~ return
    m  = m.add_menu("newcomers",MODULE_LABEL)
    m.add_action(Brokers)
    m.add_action(Faculties)
  
def setup_explorer_menu(site,ui,user,m):
    #~ if user.profile.newcomers_level < UserLevels.manager:
        #~ return
    m.add_action(Competences)

def setup_reports_menu(site,ui,user,m):
    m.add_action(AvailableCoaches)
  
dd.add_user_group('newcomers',MODULE_LABEL)

#~ customize_pcsw()