import logging

from adhocracy import model
from pylons import config
from paste.deploy.converters import asbool

log = logging.getLogger(__name__)


class InstanceDiscriminatorMiddleware(object):

    def __init__(self, app, domain):
        self.app = app
        self.domain = domain
        log.debug("Host name: %s." % domain)

    def __call__(self, environ, start_response):
        environ['adhocracy.domain'] = self.domain
        instance_key = config.get('adhocracy.instance')
        if instance_key is None:
            if asbool(config.get('adhocracy.relative_urls', 'false')):
                path = environ.get('PATH_INFO', '')
                if path.startswith('/i/'):
                    instance_key = path.split('/')[2]
                    environ['PATH_INFO'] = path[len('/i/' + instance_key):]
            else:
                host = environ.get('HTTP_HOST', "")
                host = host.replace(self.domain, "")
                host = host.replace('localhost', "")
                host = host.split(':', 1)[0]
                host = host.strip('.').strip()
                instance_key = host

        if instance_key: # instance key is set (neither None nor "")
            instance = model.Instance.find(instance_key)
            if instance is None:
                log.debug("No such instance: %s, defaulting!" % instance_key)
            else:
                model.instance_filter.setup_thread(instance)
        try:
            return self.app(environ, start_response)
        finally:
            model.instance_filter.setup_thread(None)


def setup_discriminator(app, config):
    # warn if abdoned adhocracy.domains is used
    if config.get('adhocracy.domains') is not None:
        raise AssertionError('adhocracy.domains is not supported anymore. '
                             'use adhocracy.domain (without the s) with only '
                             'one domain')
    domain = config.get('adhocracy.domain').strip()
    return InstanceDiscriminatorMiddleware(app, domain)
