import itertools
import time
import uuid

from django.conf import settings

from visitor.models import Visitor
from visitor import visitor_constants as constants

# this is a counter to make sure our uuid's are unique.
counter = itertools.count(0).next

# pull settings from settings file, if not there, use reasonable defaults
COOKIE_DOMAIN = getattr(settings, 'COOKIE_DOMAIN', None) # local domain only 
COOKIE_MAX_AGE = getattr(settings, 'COOKIE_MAX_AGE', 31536000) # 1 year
VISITOR_IGNORE_IP_LIST = getattr(settings, 'VISITOR_IGNORE_IP_LIST', ('127.0.0.1',))

def create_uuid(*parts):
    """ create a uuid """
    name = '-'.join([str(counter())] + [str(time.time())] + [str(p) for p in parts])
    return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

def ip_address_from_request(request):
    """ get the ip address from the request added special logic for lots
    of different conditions, proxies, etc. """
    meta = request.META

  # figure out the IP
    if 'HTTP_TRUE_CLIENT_IP' in meta:
        # Akamai's Site accelorator's proxy header for real IP
        ip_address = meta.get('HTTP_TRUE_CLIENT_IP', '')
    elif 'REMOTE_ADDR' in meta and meta.get('REMOTE_ADDR', '') not in VISITOR_IGNORE_IP_LIST:
        # use the remote address unless it is one of the ones in the ignore list
        # then keep looking to see if we find a better one.
        ip_address = meta.get('REMOTE_ADDR', '')
    elif 'HTTP_X_REAL_IP' in meta:
        ip_address = meta.get('HTTP_X_REAL_IP', '')
    elif 'HTTP_X_FORWARDED_FOR' in meta:
        forwarded_list = meta.get('HTTP_X_FORWARDED_FOR', '')
        # forwarded for can have multiple IP's comma seperated
        # the newest is far left, oldest appended to the right
        # X-Forwarded-For: client1, proxy1, proxy2
        #
        # http://en.wikipedia.org/wiki/X-Forwarded-For
        # we want the first one since this is the client
        ip_address = forwarded_list.split(",")[0]
    else:
        ip_address = meta.get('REMOTE_ADDR', None)

    return ip_address

def get_visitor(visitor_key):
    """ get visitor by their visitor key"""
    return Visitor.objects.find_visitor(visitor_key)

def create_visitor(ip_address, session_key):
    """ Create the visitor given an ip_address """
    visitor = Visitor()
    visitor.generate_key(ip_address)
    visitor.mark_visit()
    visitor.last_session_key = session_key
    visitor.save()
    return visitor

def update_visitor(visitor_key, session_key=None):
    """ update the visitor using the visitor key """
    visitor = get_visitor(visitor_key)
    if visitor:
        visitor.mark_visit()
        if session_key:
            visitor.last_session_key = session_key
        visitor.save()
    return visitor

def get_visitor_cookie_key(request):
    """ look for the cookie and if we find one return the visitor key """
    if constants.COOKIE_VISITOR_KEY in request.COOKIES:
        return request.COOKIES[constants.COOKIE_VISITOR_KEY]
    else:
        return None

def get_visitor_from_request(request):
    """ look for the cookie and if we find one return the visitor key """
    if constants.COOKIE_VISITOR_KEY in request.COOKIES:
        return get_visitor(request.COOKIES[constants.COOKIE_VISITOR_KEY])
    else:
        return None

def set_visitor_cookie(response, visitor):
    """ set the visitor cookie using the visitor object """
    if response and visitor and visitor.visitor_key:
        response.set_cookie(
            constants.COOKIE_VISITOR_KEY, 
            visitor.visitor_key,
            max_age=COOKIE_MAX_AGE,
            domain=COOKIE_DOMAIN
        )

def set_visitor_cookie_from_key(response, visitor_key):
    """ set the cookie using the visitor_key"""
    if response and visitor_key:
        response.set_cookie(
            constants.COOKIE_VISITOR_KEY, 
            visitor_key,
            max_age=COOKIE_MAX_AGE,
            domain=COOKIE_DOMAIN
        )

def delete_visitor_cookie(response):
    """ delete the visitor cookie """
    if response:
        response.delete_cookie(
            constants.COOKIE_VISITOR_KEY,
            domain=COOKIE_DOMAIN
        )
