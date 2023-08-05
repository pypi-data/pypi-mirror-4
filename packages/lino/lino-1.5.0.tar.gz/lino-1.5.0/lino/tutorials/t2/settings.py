from lino.apps.std.settings import *

class Lino(Lino):
  
    title = "Lino Tutorial"
    
    def setup_menu(self,ui,user,main):
        m = main.add_menu("polls","~Polls")
        m.add_action('polls.Polls')
        
        m = main.add_menu("config","~Configure")
        m.add_action('users.Users')
        
    
    
LINO = Lino(__file__,globals()) 

DEBUG = True


#~ LOGGING = dict(filename=join(LINO.project_dir,'log','system.log'),level='DEBUG')
#~ LOGGING = dict(filename=None,level='INFO')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': abspath(join(
            dirname(__file__),'..','..','..','tmp','t1.db')),
    }
}

INSTALLED_APPS = (
  'django.contrib.contenttypes',
  #~ 'django.contrib.auth',
  #~ 'django.contrib.admin',
  'lino.modlib.users',
  'lino',
  'lino.tutorials.t2.polls'
)


#~ ROOT_URLCONF = 'lino.tutorials.t2.urls'
#~ ROOT_URLCONF = 'lino.tutorials.t2.urls2'
#~ ROOT_URLCONF = 'lino.tutorials.t2.urls3'


