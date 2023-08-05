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


import logging
logger = logging.getLogger(__name__)

import sys
import decimal
#import logging ; logger = logging.getLogger('lino.apps.finan')

#~ from django import forms

from lino import dd

from django.db import models
#~ from lino import fields
from lino.core.modeltools import resolve_model

contacts = dd.resolve_app('contacts')
#~ ledger = dd.resolve_app('ledger')
from lino.modlib.ledger import models as ledger
journals = dd.resolve_app('journals')

Contact = resolve_model('contacts.Contact')
#~ Person = resolve_model('contacts.Person')
#~ Company = resolve_model('contacts.Company')

def _functionId(nFramesUp):
    # thanks to:
    # http://nedbatchelder.com/blog/200410/file_and_line_in_python.html
    """ Create a string naming the function n frames up on the stack.
    """
    co = sys._getframe(nFramesUp+1).f_code
    return "%s (%s:%d)" % (co.co_name, co.co_filename, co.co_firstlineno)


def todo_notice(msg):
    print "[todo] in %s :\n       %s" % (_functionId(1),msg)
  
class BankStatement(journals.Journaled,ledger.Booked):
    
    #~ # implements Journaled:
    #~ journal = journals.JournalRef()
    #~ number = journals.DocumentRef()
    
    #~ # implements Booked:
    #~ value_date = models.DateField(auto_now=True)
    #~ ledger_remark = models.CharField("Remark for ledger",
      #~ max_length=200,blank=True)
    #~ booked = models.BooleanField(default=False)
    
    date = models.DateField()
    balance1 = dd.PriceField()
    balance2 = dd.PriceField()
    
    def full_clean(self,*args,**kw):
    #~ def before_save(self):
        if not self.booked:
            if self.value_date is None:
                self.value_date = self.date
            #journals.AbstractDocument.before_save(self)
            #ledger.LedgerDocumentMixin.before_save(self)
            balance = self.balance1
            if self.id is not None:
                for i in self.docitem_set.all():
                    balance += i.debit - i.credit
            self.balance2 = balance
        super(BankStatement,self).full_clean(*args,**kw)
        
    #~ def after_save(self):
        #~ logger.info("Saved document %s (balances=%r,%r)",self,self.balance1,self.balance2)
        
    def collect_bookings(self):
        sum_debit = 0 # decimal.Decimal(0)
        for i in self.docitem_set.all():
            b = self.create_booking(
              pos=i.pos,
              account=i.account,
              contact=i.contact,
              #~ person=i.person,
              #~ company=i.company,
              date=i.date,
              debit=i.debit,
              credit=i.credit)
            sum_debit += i.debit - i.credit
            yield b
        #todo_notice("BankStatement.balance1 and 2 are strings?!")
        #http://code.google.com/p/lino/issues/detail?id=1
        #logger.info("finan.BankStatement %r %r",self.balance1, sum_debit)
        self.balance2 = self.balance1 + sum_debit
        #jnl = self.get_journal()
        #~ acct = ledger.Account.objects.get(id=self.journal.account)
        #~ b = self.create_booking(account=acct)
        b = self.create_booking(account=self.journal.account)
        if sum_debit > 0:
            b.debit = sum_debit
        else:
            b.credit = - sum_debit
        yield b
        
    def add_item(self,account=None,contact=None,
        #~ company=None,person=None,
        **kw):
        pos = self.docitem_set.count() + 1
        if account is not None:
            if not isinstance(account,ledger.Account):
                account = ledger.Account.objects.get(match=account)
        if contact is not None:
            if not isinstance(contact,Contact):
                contact = Contact.objects.get(pk=contact)
        #~ if person is not None:
            #~ if not isinstance(person,Person):
                #~ person = Person.objects.get(pk=person)
        #~ if company is not None:
            #~ if not isinstance(company,Company):
                #~ company = Company.objects.get(pk=company)
        kw['account'] = account
        kw['contact'] = contact
        #~ kw['person'] = person
        #~ kw['company'] = company
        for k in ('debit','credit'):
            v = kw.get(k,None)
            if isinstance(v,basestring):
                kw[k] = decimal.Decimal(v)
        #~ return self.docitem_set.create(**kw)
        kw['document'] = self
        return DocItem(**kw)
        #~ return self.docitem_set.create(**kw)
    
  
class DocItem(dd.Model):
    document = models.ForeignKey(BankStatement) 
    pos = models.IntegerField("Position")
    date = models.DateField(blank=True,null=True)
    debit = dd.PriceField(default=0)
    credit = dd.PriceField(default=0)
    remark = models.CharField(max_length=200,blank=True)
    account = models.ForeignKey(ledger.Account)
    contact = models.ForeignKey(Contact,blank=True,null=True)
    #~ person = models.ForeignKey(Person,blank=True,null=True)
    #~ company = models.ForeignKey(Company,blank=True,null=True)
    
    def full_clean(self,*args,**kw):
        if self.pos is None:
            self.pos = self.document.docitem_set.count() + 1
        return super(DocItem,self).full_clean(*args,**kw)
        
    def __unicode__(self):
        return u"DocItem %s.%d" % (self.document,self.pos)
        
#~ class Booking(dd.Model):
    #~ #journal = models.ForeignKey(journals.Journal)
    #~ #number = models.IntegerField()
    #~ document = models.ForeignKey(LedgerDocument) 
    #~ pos = models.IntegerField("Position")
    #~ date = fields.MyDateField() 
    #~ account = models.ForeignKey(Account)
    #~ contact = models.ForeignKey(contacts.Contact,blank=True,null=True)
    #~ debit = fields.PriceField(default=0)
    #~ credit = fields.PriceField(default=0)
    

        

    
class BankStatements(journals.DocumentsByJournal):
    model = BankStatement
    column_names = "number date balance1 balance2 ledger_remark value_date"
    
    
    
class DocItems(dd.Table):
    column_names = "document pos:3 "\
                  "date account contact remark debit credit" 
    model = DocItem
    order_by = ["pos"]

class ItemsByDocument(DocItems):
    column_names = "pos:3 date account contact remark debit credit" 
    #master = BankStatement
    master_key = 'document'
    
BankStatement.content = ItemsByDocument

journals.register_doctype(BankStatement,BankStatements)
