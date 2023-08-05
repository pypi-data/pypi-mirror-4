from django.db import models
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser

from visitor import managers

from datetime import datetime

class Visitor(models.Model):
    visitor_key = models.CharField(max_length='50', db_index=True)
    created = models.DateTimeField(default=datetime.now())
    last_update = models.DateTimeField()
    num_visits = models.SmallIntegerField(default=0)
    last_session_key = models.CharField(max_length=40)
    
    objects = managers.VisitorManager()
    
    def __unicode__(self):
        return '#%d/%s' % (self.id, self.last_session_key)
        
    def generate_key(self, ip_address):
        if not self.visitor_key:
            from visitor.visitor_utils import create_uuid
            self.visitor_key = create_uuid(ip_address)
        return self.visitor_key

    def mark_visit(self):
        self.num_visits += 1

    def save(self, *args, **kws):
        self.last_update = datetime.now()
        super(Visitor, self).save(*args, **kws)
        
    @property
    def session(self):
        try:
            return Session.objects.get(session_key=self.last_session_key)
        except Session.DoesNotExist:
            return None
            
    @property      
    def user():
        """ 
            a backend-agnostic way to get the user from the session.
            
            Originally taken from http://djangosnippets.org/snippets/1276/ and
            changed a little. Thanks jdunck
            
        """
        session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        session_wrapper = session_engine.SessionStore(self.last_session_key)
        user_id = session_wrapper.get(SESSION_KEY)
        auth_backend = load_backend(session_wrapper.get(BACKEND_SESSION_KEY))

        if user_id and auth_backend:
          return auth_backend.get_user(user_id)
        else:
          return AnonymousUser()
    
