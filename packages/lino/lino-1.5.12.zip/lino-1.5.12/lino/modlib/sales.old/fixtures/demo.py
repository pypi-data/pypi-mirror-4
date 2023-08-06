# -*- coding: UTF-8 -*-
## Copyright 2008-2011 Luc Saffre
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

import time
from datetime import date
from dateutil import parser as dateparser

from lino import dd
from lino.modlib.sales import utils
from lino.utils.instantiator import Instantiator, i2d

def objects():
  
    Company = dd.resolve_model("contacts.Company")
    Customer = dd.resolve_model('sales.Customer')

    products = dd.resolve_app('products')
    sales = dd.resolve_app('sales')

    salesrule = Instantiator(sales.SalesRule).build
    #customer = Instantiator(Customer).build

    imode = Instantiator(sales.InvoicingMode,
      "id channel name advance_days journal").build

    for c in Company.objects.filter(country_id='BE'):
        yield c.contact_ptr.insert_child(Customer)
        
    paymentterm = Instantiator(sales.PaymentTerm,"id name").build
    yield paymentterm("pp","Prepayment",days=7)
    yield paymentterm("cash","Cash")
    yield paymentterm("7","7 days net",days=7)
    pt15 = paymentterm("15","15 days net",days=15)
    yield pt15
    yield paymentterm("30","30 days net",days=30)


    shippingmode = Instantiator(sales.ShippingMode,"id name").build
    yield shippingmode("ta","take away")
    yield shippingmode("rm","regular mail")

    #~ for company in Company.objects.all():
        #~ yield Customer(company=company)
    #~ for person in Person.objects.all():
        #~ yield Customer(person=person)
    
    #ORD = journals.get_journal_by_docclass(Order)
    #INV = journals.get_journal_by_docclass(Invoice)
        
    ORD = sales.Order.create_journal("ORD",name="Orders",printed_name="Order # %d")
    #ORD = journals.get_journal("ORD")
    #INV = journals.get_journal("INV")
    yield ORD
    INV = sales.Invoice.create_journal("INV",\
      account=ledger.Account.objects.get(match="4000"),
      name="Invoices",printed_name="Invoice # %d")
    #~ INV = sales.Invoice.create_journal("INV",account="4000",name="Invoices")
    yield INV
    
    
    imode_e = imode('e','E','By e-mail',2,INV,template='order_invoice.odt',build_method='appyodt')
    yield imode_e
    imode_p = imode('p','P','By snail mail',10,INV,template='order_invoice.odt',build_method='appyodt')
    yield imode_p
        
    yield salesrule(imode='e',shipping_mode="ta",payment_term="7")
    
    #~ Company = resolve_model('contacts.Company')
    #Person = resolve_model('contacts.Person')
    #company1 = Company.objects.get(name__startswith="Ausdemwald")
    #dubois = Person.objects.get(last_name__startswith="Dubois")
    furniture = products.ProductCat.objects.get(pk=1) # name="Furniture")
    hosting = products.Product.objects.get(pk=5)
    
    #~ order = Instantiator(sales.Order,
        #~ "company creation_date start_date cycle imode",
        #~ payment_term="30",journal=ORD).build
    #~ invoice = Instantiator(sales.Invoice,
      #~ "company creation_date imode",
      #~ payment_term="30",journal=INV).build
    
    o = ORD.create_document(
        customer=Customer.objects.all()[0],
        #~ company=Company.objects.get(pk=1),
        creation_date=i2d(20080923),start_date=i2d(20080924),
        cycle="M",imode=imode_e,
        sales_remark="monthly order")
    #~ o = order(1,"2008-09-23","2008-09-24","M","e",sales_remark="monthly order")
    o.add_item(hosting,1)
    yield o

    o = ORD.create_document(
        customer=Customer.objects.all()[1],
                #~ company=Company.objects.get(pk=2),
        creation_date=i2d(20080923),start_date=i2d(20080924),
        cycle="M",imode=imode_e,
        sales_remark="Customer 2 gets 50% discount")
        
    #~ o = order(2,"2008-09-23","2008-09-24","M","e",
        #~ sales_remark="Company 2 gets 50% discount")
    o.add_item(hosting,1,discount=50)
    yield o  

    utils.make_invoices(make_until=date(2008,10,28))
        

    i = INV.create_document(
        customer=Customer.objects.all()[1],
        #~ company=Company.objects.get(pk=2),
        creation_date=i2d(20081029),
        imode=imode_e,
        sales_remark="first manual invoice")
    #~ i = invoice(2,"2008-10-29","e",
      #~ sales_remark="first manual invoice")
    i.add_item(1,1)
    i.add_item(2,4)
    yield i
    
    utils.make_invoices(make_until=date(2009,04,11))
        
    i = INV.create_document(
        customer=Customer.objects.all()[2],
        #~ company=Company.objects.get(pk=3),
        creation_date=i2d(20090411),
        imode=imode_e,
        sales_remark="second manual invoice")
    #~ i = invoice(3,date(2009,04,11),"e",
        #~ sales_remark="second manual invoice")
    i.add_item(3,1)
    i.add_item(4,4)
    yield i
    
    #d = '2009-04-12'
    #d = '20090412'
    d = i2d(20090412)
    #d = date(2009,4,12)
    #~ o2 = order(4,d,d,"Y","p",sales_remark="yearly order")
    o2 = ORD.create_document(
        customer=Customer.objects.all()[3],
        #~ company=Company.objects.get(pk=4),
        creation_date=d,start_date=d,
        cycle="Y",imode=imode_p,
        sales_remark="yearly order")
    
    o2.add_item(3,1)
    o2.add_item(4,4)
    #print o2
    #o2.save()
    yield o2
    utils.make_invoices(make_until=d)
    
    #~ i = invoice(4,date(2009,04,13),"e",
      #~ sales_remark="third manual invoice with discount")
    i = INV.create_document(
        customer=Customer.objects.all()[3],
        #~ company=Company.objects.get(pk=4),
        creation_date=i2d(20090413),
        imode=imode_e,
        sales_remark="third manual invoice with discount")
    i.add_item(3,1,discount=10)
    i.add_item(4,4,discount=5)
    yield i
    
    utils.make_invoices(make_until=date(2009,05,14))

    #~ order = Instantiator(sales.Order,journal=ORD,cycle='M',imode='e',payment_term="15").build
    i = 0 
    for cust in Customer.objects.order_by('id'):
        i += 1
    #~ for i in range(10):
    #for i in range(29):
        #~ o = order(
            #~ company=i+1,creation_date=date(2009,6,1+i),
            #~ sales_remark="range demo #%d" % i)
        o = ORD.create_document(
            cycle='M',imode=imode_e,payment_term=pt15,
            customer=cust,
            #~ company=Company.objects.get(pk=i+1),
            creation_date=date(2009,6,i),
            sales_remark="range demo #%d" % i)
        yield o
        yield o.add_item(5,1,unit_price=1.7*i)
        
    utils.make_invoices(make_until=date(2009,7,1))
    utils.make_invoices(make_until=date(2009,8,1))
    utils.make_invoices(make_until=date(2009,10,1))
