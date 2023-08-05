"""
Visitor's Middleware, it will look to see if we already registered this visitor
if not, it will create a cookie, and create a visitor record for future tracking. 
If we already know about them we get their visitor record and update it.
"""
from django import http

import visitor.visitor_utils as utils
from visitor import visitor_constants as constants


class VisitorMiddleware(object):
    """ 
    Visitors middleware it will look to see if we already registered this 
    visitor if not, it will create a cookie, and create a visitor record for 
    future tracking. If we already know about them we get their visitor record 
    and update it.
    """

    def process_request(self, request):
        """ get or set the visitor cookie """
        # figure out the IP
        ip_address = utils.ip_address_from_request(request) or 'Unknown'

        # we check to see if they have a cookie, if they do we update the stats
        # for the cookie if they don't have a cookie, we create the cookie.
        # then we associate that cookie to the web request 
        # later on in the response if we haven't set the cookie yet, we will 
        # set the cookie in the browser.
        
        cookie_saved = request.session.get(constants.COOKIE_SAVED, None)
        visitor_key = request.session.get(constants.VISITOR_KEY, None)
        visitor_key_cookie = utils.get_visitor_cookie_key(request)
        
        # print("cookie saved = %s" % cookie_saved)
        # print("visitor_key = %s" % visitor_key)
        # print("visitor_key_cookie = %s" % visitor_key_cookie)
        
        # if we have a visitor key, and cookie_saved from session
        # and we get a cookie and the cookie's visitor key matches the one 
        # in the session then we don't need to continue, everything is all
        # set.
        #
        # if we wanted to update the visitor every time they made a request
        # we wouldn't do this, but that would take a lot of resources for
        # large sites, so we will defer that to a future version for now.
        if (visitor_key and 
            cookie_saved and 
            visitor_key_cookie and 
            visitor_key == visitor_key_cookie):
                return None
        
        session_key = request.session.session_key
        # print("session_key = %s" % session_key)
        
        if visitor_key_cookie:
            request.session[constants.COOKIE_SAVED] = True
            visitor = utils.update_visitor(visitor_key_cookie, 
                                     session_key=session_key)
                                     
            if not visitor:
                # we couldn't find their old cookie, so create a new one.
                request.session[constants.COOKIE_SAVED] = False
                visitor = utils.create_visitor(ip_address, session_key)
                                         
        else:
            request.session[constants.COOKIE_SAVED] = False
            visitor = utils.create_visitor(ip_address, session_key)

        request.session[constants.VISITOR_KEY] = visitor.visitor_key
        return None

    def process_response(self,request, response):
        """ look if we need to save the visitor cookie """
        if hasattr(request, 'session'):
            cookie_saved = request.session.get(constants.COOKIE_SAVED, None)
            visitor_key = request.session.get(constants.VISITOR_KEY, None)
            if not cookie_saved and visitor_key:
                utils.set_visitor_cookie_from_key(response, visitor_key)
                request.session[constants.COOKIE_SAVED] = True
        return response