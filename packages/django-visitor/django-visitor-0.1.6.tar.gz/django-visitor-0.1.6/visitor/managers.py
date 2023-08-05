from django.db import models

class VisitorManager(models.Manager):
    
    def find_visitor(self, visitor_key):
        try:
            return self.get(visitor_key=visitor_key)
        except self.model.DoesNotExist:
            return None