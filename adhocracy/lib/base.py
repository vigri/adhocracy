"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging

from paste.deploy.converters import asbool
from pylons import config
from pylons.controllers import WSGIController
from pylons import request, tmpl_context as c
from pylons.i18n import _
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.orm.exc import DetachedInstanceError

from adhocracy import i18n, model
from adhocracy.lib import helpers as h
from adhocracy.lib.templating import ret_abort

log = logging.getLogger(__name__)


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        
        do_logging = asbool(config.get('adhocracy.enable_request_logging', 'false'))
        if do_logging:
            self.log_request(environ)
        
        c.instance = model.instance_filter.get_instance()
        if c.instance is not None:
            # setup a global variable to mark the current item in
            # the global navigation
            c.active_global_nav = 'instances'
        else:
            c.active_global_nav = 'home'
        c.user = environ.get('repoze.who.identity', {}).get('user')
        try:
            if c.user and (c.user.banned or c.user.delete_time):
                c.user = None
        except DetachedInstanceError, e:
            log.exception(e)
        c.active_controller = request.environ.get('pylons.routes_dict')\
            .get('controller')
        c.debug = asbool(config.get('debug'))
        i18n.handle_request()

        h.add_rss("%s News" % h.site.name(),
                  h.base_url('/feed.rss', None))
        if c.instance:
            h.add_rss("%s News" % c.instance.label,
                      h.base_url('/instance/%s.rss' % c.instance.key))

        h.add_meta("description",
                   _("A liquid democracy platform for making decisions in "
                     "distributed, open groups by cooperatively creating "
                     "proposals and voting on them to establish their "
                     "support."))
        h.add_meta("keywords",
                   _("adhocracy, direct democracy, liquid democracy, liqd, "
                     "democracy, wiki, voting,participation, group decisions, "
                     "decisions, decision-making"))

        try:
            return WSGIController.__call__(self, environ, start_response)
        except Exception, e:
            log.exception(e)
            model.meta.Session.rollback()
            raise
        finally:
            if isinstance(model.meta.Session, ScopedSession):
                model.meta.Session.remove()

    def bad_request(self, format='html'):
        log.debug("400 Request: %s" % request.params)
        return ret_abort(_("Invalid request. Please go back and try again."),
                         code=400, format=format)

    def not_implemented(self, format='html'):
        return ret_abort(_("The method you used is not implemented."),
                         code=400, format=format)

    def log_request(self, environ):
        req_cookies = environ.get('HTTP_COOKIE')
        req_user_agent = environ.get('HTTP_USER_AGENT')
        req_ip = None
        req_xff = None
        if asbool(config.get('adhocracy.request_logging.enable_ip_logging')):
        	#CHECK IF XFF PROXY AND TRANSMIT THE REAL IP TO THE DATABASE
        	req_xff = environ.get('X-Forwarded-For')
        	req_ip = environ.get('REMOTE_ADDR')
        	if req_xff:
        		req_ip = req_xff.split(',', 1)[0]

        req = model.Request(req_cookies, req_ip, req_user_agent, environ['PATH_INFO'], req_xff)
        req.save_request()
        
        return req
