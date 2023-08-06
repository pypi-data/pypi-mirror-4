import logging

from .urllib2client import Urllib2Client


__all__ = ("Client",)


logger = logging.getLogger("arango.client")
Client = Urllib2Client

try:
    from .pycurlclient import PyCurlClient
    Client = PyCurlClient
except Exception, e:
    logger.warning(
        u"Sorry, can't import PyCurlClient. Reason: %s", unicode(e))
