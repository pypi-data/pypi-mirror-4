# -*- coding: UTF-8 -*-
## Copyright 2009-2012 Luc Saffre
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


:func:`iif` (inline ``if``)
---------------------------

>>> iif(1>2,'yes','no')
'no'

:func:`str2hex` and :func:`hex2str`
-----------------------------------

>>> str2hex('-L')
'2d4c'

>>> hex2str('2d4c')
'-L'

>>> hex2str('')
''
>>> str2hex('')
''

:func:`join_words`
------------------

>>> print join_words('This','is','a','test')
This is a test

>>> print join_words('This','is','','another','test')
This is another test

>>> print join_words(None,None,None,'Third','test')
Third test


"""

#~ import logging
#~ logger = logging.getLogger(__name__)


import os, sys, locale, types, datetime
import re
import fnmatch
from dateutil import parser as dateparser
from decimal import Decimal
import stat

#~ import lino

def confirm(prompt=None):
    """
    Ask for user confirmation from the console.
    """
    while True:
        ln = raw_input(prompt)
        if ln.lower() in ('y','j','o'):
            return True
        if ln.lower() == 'n':
            return False
        print "Please anwer Y or N"

def iif(l,y,f): 
    """
    "Inline If" : an ``if`` statement as a function.
    """
    if l: return y 
    return f
    
def isiterable(x):
    "Returns `True` if the specified object is iterable."
    try:
        it = iter(x)
    except TypeError: 
        return False
    return True
    
    
def ispure(s):
    """Returns `True` if the specified string `s` is either a unicode 
    string or contains only ASCII characters."""
    if s is None: return True 
    if type(s) == types.UnicodeType:
        return True
    if type(s) == types.StringType:
        try:
            s.decode('ascii')
        except UnicodeDecodeError,e:
            return False
        return True
    return False

def assert_pure(s):
    assert ispure(s), "%r: not pure" % s
     

def join_words(*words):
    """
    Remove any empty item (None or ''), call unicode on each and 
    join the remaining word using a single space.
    """
    return ' '.join([unicode(x) for x in words if x])
      

def d2iso(d):
    "Supports also dates before 1900."
    return "%04d-%02d-%02d" % (d.year, d.month, d.day)

def i2d(i):
    d = dateparser.parse(str(i))
    d = datetime.date(d.year,d.month,d.day)
    #print i, "->", v
    return d
    
def get_class_attr(cl,name):
    value = getattr(cl,name,None)
    if value is not None:
        return value
    for b in cl.__bases__:
        value = getattr(b,name,None)
        if value is not None:
            return value
            
def class_dict_items(cl,exclude=None):
    if exclude is None:
        exclude = set()
    for k,v in cl.__dict__.items(): 
        if not k in exclude:
            yield k,v
            exclude.add(k)
    for b in cl.__bases__:
        for k,v in class_dict_items(b,exclude): 
            yield k,v


def call_optional_super(cls,self,name,*args,**kw):
    """
    Doesn't work. See :doc:`/blog/2011/0914`.
    """
    s = super(cls,self)
    m = getattr(s,'name',None)
    if m is not None:
        return m(*args,**kw)

def call_on_bases(cls,name,*args,**kw):
    """
    Doesn't work. See :doc:`/blog/2011/0914`.
    This is necessary because we want to call `setup_report`
    on the model and all base classes of the model.
    We cannot use super() for this because the `setup_report` 
    method is optional.
    """
    for b in cls.__bases__: call_on_bases(b,name,*args,**kw)
    if True:
        m = getattr(cls,name,None)
        # getattr will also return the classmethod defined on a base class, 
        # which has already been called. 
        if m is not None and m.im_class is cls:
            m(cls,*args,**kw)
        
    """Note: the following algorithm worked in Python 2.7 but not in 2.6,
    a classmethod object in 2.6 has no attribute `im_func`
    """
      
    #~ m = cls.__dict__.get(name)
    #~ if m:
        #~ func = getattr(m,'im_func',None)
        #~ if func is None:
            #~ raise Exception("Oops, %r in %s (%r) has no im_func" % (name,cls,m))
        #~ func(cls,*args,**kw)
        #~ # m.__func__(cls,*args,**kw)




def str2hex(s):
    """Convert a string to its hexadecimal representation."""
    r = ''
    for c in s:
        r += hex(ord(c))[2:]
    return r
    
def hex2str(value):
    """Convert the hexadecimal representation of a string to the original string."""
    if len(value) % 2 != 0:
        raise Exception("hex2str got value %r" % value)
    r = ''
    for i in range(len(value) / 2):
       s = value[i*2:i*2+2]
       h = int(s,16)
       r += chr(h)
    return r
    
# http://snippets.dzone.com/posts/show/2375
curry = lambda func, *args, **kw:\
            lambda *p, **n:\
                 func(*args + p, **dict(kw.items() + n.items()))
                 
    

#~ def codefiles(pattern='.*', flags=0):
def codefiles(pattern='*'):
    """
    Yield a list of the source files corresponding to the currently 
    imported modules which match the given pattern
    """
    #~ exp = re.compile(pattern, flags)
    
    for name,mod in sys.modules.items():
        if fnmatch.fnmatch(name, pattern):
        #~ if exp.match(name):
            filename = getattr(mod, "__file__", None)
            if filename is not None:
                if filename.endswith(".pyc") or filename.endswith(".pyo"):
                    filename = filename[:-1]
                if filename.endswith("$py.class"):
                    filename = filename[:-9] + ".py"
                if os.path.exists(filename): # File might be in an egg, so there's no source available
                    yield name,filename
            
def codetime():
    """
    Return the modification time of the youngest source code in memory.
    Used by :mod:`lino.ui.extjs3.ext_ui` to avoid generating lino.js files if not necessary.
    Inspired by the code_changed() function in `django.utils.autoreload`.
    """
    code_mtime = None
    for name,filename in codefiles():
        stat = os.stat(filename)
        mtime = stat.st_mtime
        #~ print filename, time.ctime(mtime)
        if code_mtime is None or code_mtime < mtime:
            code_mtime = mtime
    return code_mtime
    
    
class IncompleteDate:
    """
    Naive representation of an incomplete gregorian date.
    
    >>> print IncompleteDate(2011,0,0).strftime("%d.%m.%Y")
    00.00.2011
    >>> print IncompleteDate(1532,0,0)
    1532-00-00
    >>> print IncompleteDate(1990,0,1)
    1990-00-01
    >>> print IncompleteDate(0,6,1)
    0000-06-01
    
    Christ's birth date:
    
    >>> print IncompleteDate(-7,12,25)
    -7-12-25
    >>> print IncompleteDate(-7,12,25).strftime("%d.%m.%Y")
    25.12.-7
    
    An IncompleteDate is allowed to be complete:
    
    >>> d = IncompleteDate.parse('2011-11-19')
    >>> print d
    2011-11-19
    >>> d.is_complete()
    True
    
    """
    
    def __init__(self,year,month,day):
        self.year, self.month, self.day = year, month, day
        
    @classmethod
    def parse(cls,s):
        if s.startswith('-'):
            bc = True
            s = s[1:]
        else:
            bc = False
        y,m,d = map(int,s.split('-'))
        if bc: y = - y
        return cls(y,m,d)
        
    @classmethod
    def from_date(cls,date):
        return cls(date.year,date.month,date.day)
        
        
    def is_complete(self):
        if self.year and self.month and self.day:
            return True
        return False
        
    def __eq__(self,other):
        return str(self) == str(other)
        
    def __ne__(self,other):
        return str(self) != str(other)

    def __len__(self):
        return len(str(self))
        
    def __repr__(self):
        return "IncompleteDate(%r)" % str(self)
        
    def __str__(self):
        return self.strftime()
        
    def strftime(self,fmt="%Y-%m-%d"):
        #~ s = fmt.replace("%Y",iif(self.bc,'-','')+str(self.year))
        if self.year == 0:
            s = fmt.replace("%Y",'0000')
        else:
            s = fmt.replace("%Y",str(self.year))
        s = s.replace("%m","%02d" % self.month)
        s = s.replace("%d","%02d" % self.day)
        return s
        
        #~ return self.strftime_(fmt,
            #~ iif(self.bc,-1,1)*self.year,
            #~ self.month,
            #~ self.day)
        
    def as_date(self):
        return datetime.date(
            #~ (self.year * iif(self.bc,-1,1)) or 1900, 
            self.year or 1900, 
            self.month or 1, 
            self.day or 1)
        

class AttrDict(dict):
    """
    Usage example:
    
    >>> a = AttrDict()
    >>> a.define('foo',1)
    >>> a.define('bar','baz',2)
    >>> print a
    {'foo': 1, 'bar': {'baz': 2}}
    >>> print a.foo
    1
    >>> print a.bar.baz
    2
    >>> print a.resolve('bar.baz')
    2
    >>> print a.bar
    {'baz': 2}
    
    """
  
    def __getattr__(self, name):
        return self[name]
        
    def define2(self,name,value):
        return self.define(*name.split('.')+[value])
        
    def define(self,*args):
        "args must be a series of names followed by the value"
        assert len(args) >= 2
        d = s = self
        for n in args[:-2]:
            d = s.get(n,None)
            if d is None:
                d = AttrDict()
                s[n] = d
            s = d
        oldvalue = d.get(args[-2],None)
        #~ if oldvalue is not None:
            #~ print 20120217, "Overriding %s from %r to %r" % (
              #~ '.'.join(args[:-1]),
              #~ oldvalue,
              #~ args[-1]
              #~ )
        d[args[-2]] = args[-1]
        return oldvalue
    
    def resolve(self,name,default=None):
        """
        return an attribute with dotted name
        """
        o = self
        for part in name.split('.'):
            o = getattr(o,part,default)
            # o = o.__getattr__(part)
        return o
        

class Cycler:
    """
    Turns a list of items into an endless loop.
    Useful when generating demo fixtures.
    
    >>> def myfunc():
    ...     yield "a"
    ...     yield "b"
    ...     yield "c"
    
    >>> c = Cycler(myfunc())
    >>> s = ""
    >>> for i in range(10):
    ...     s += c.pop()
    >>> print s
    abcabcabca
    
    A Cycler on an empty list will endlessly pop None values:
    
    >>> c = Cycler([])
    >>> print c.pop(), c.pop(), c.pop()
    None None None
    
    """
    def __init__(self,*args):
        if len(args) == 0:
            raise ValueError()
        elif len(args) == 1:
            self.items = list(args[0])
        else:
            self.items = args
        self.current = 0
        
    def pop(self):
        if len(self.items) == 0: return None
        item = self.items[self.current]
        self.current += 1
        if self.current >= len(self.items):
            self.current = 0
        if isinstance(item,Cycler):
            return item.pop()
        return item
        
    def __len__(self):
        return len(self.items)
        
    def reset(self):
        self.current = 0
        



#~ class Warning(Exception): 
    #~ """
    #~ An Exception whose message is meant to be 
    #~ understandable by the user.
    #~ """
    
# unmodified copy from http://docs.python.org/library/decimal.html#recipes
def moneyfmt(value, places=2, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """
    Convert Decimal to a money formatted string.

    | places:   required number of places after the decimal point
    | curr:     optional currency symbol before the sign (may be blank)
    | sep:      optional grouping separator (comma, period, space, or blank)
    | dp:       decimal point indicator (comma or period)
    |           only specify as blank when places is zero
    | pos:      optional sign for positive numbers: '+', space or blank
    | neg:      optional sign for negative numbers: '-', '(', space or blank
    | trailneg: optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))
    
    
def unicode_string(x):
    """
    When we want unicode strings (e.g. translated exception messages) 
    to appear in an Exception, 
    we must first encode them using a non-strict errorhandler.
    Because the message of an Exception may not be a unicode string.
    
    """
    return unicode(x).encode(sys.getdefaultencoding(),'backslashreplace')
    # Python 2.6.6 said "Error in formatting: encode() takes no keyword arguments"
    #~ return unicode(x).encode(errors='backslashreplace')
    


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

