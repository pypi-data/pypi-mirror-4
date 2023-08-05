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
"Presto" means "quick" in Italian and reminds the French "prestations de service".

It is a Lino application for managing the work of service providers such 
as software developers, tax consultants, accountants, ...

Status: not yet usable

Presto manages Projects, Tickets, Sessions, Blog Entries. 
A Session is when a user works on a Ticket. 

Presto combines the following modules:

- :mod:`lino.modlib.contacts`
- :mod:`lino.modlib.tickets`
- :mod:`lino.modlib.blogs`
- :mod:`lino.modlib.uploads`
- :mod:`lino.modlib.cal`
- :mod:`lino.modlib.outbox`

"""
