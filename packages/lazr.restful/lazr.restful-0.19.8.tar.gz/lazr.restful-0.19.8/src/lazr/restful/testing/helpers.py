import sys
from types import ModuleType

from zope.configuration import xmlconfig
from zope.interface import implements

from lazr.restful import metazcml
from lazr.restful.interfaces import IWebServiceConfiguration
from lazr.restful.metazcml import webservice_sanity_checks
from lazr.restful.simple import (
    Request,
    RootResource,
    )
from lazr.restful.testing.webservice import WebServiceTestPublication
from lazr.restful.utils import tag_request_with_version_name


def create_test_module(name, *contents):
    """Defines a new module and adds it to sys.modules."""
    new_module = ModuleType(name)
    sys.modules['lazr.restful.' + name] = new_module
    for object in contents:
        setattr(new_module, object.__name__, object)
    return new_module


def register_test_module(name, *contents):
    new_module = create_test_module(name, *contents)
    # Clear out any registrations from other imports that weren't
    # sanity-checked.
    metazcml.REGISTERED_OPERATIONS = []
    metazcml.REGISTERED_ENTRIES = []

    try:
        xmlconfig.string("""
            <configure
                xmlns:webservice=
                    "http://namespaces.canonical.com/webservice">
              <include package="lazr.restful" file="meta.zcml" />
              <webservice:register module="lazr.restful.%s" />
            </configure>
            """ % name)
        webservice_sanity_checks(None)
    except Exception, e:
        del sys.modules['lazr.restful.' + name]
        raise e
    return new_module


def encode_response(response):
    """Encode a response that may contain weird Unicode characters.

    The resulting string will (eg.) contain the six characters
    "\u2603" instead of the single Unicode character SNOWMAN.

    :param response: an httplib HTTPResponse object.
    """
    response_unicode = str(response).decode("utf-8")
    return encode_unicode(response_unicode)


def encode_unicode(unicode_string):
    """Encode a Unicode string so it can be used in tests.

    The resulting string will (eg.) contain the six characters
    "\u2603" instead of the single Unicode character SNOWMAN.

    :param unicode_string: A Unicode string.
    """
    return unicode_string.encode("ascii", "backslashreplace")


class TestWebServiceConfiguration:
    implements(IWebServiceConfiguration)
    view_permission = "lazr.View"
    active_versions = ["beta", "1.0"]
    last_version_with_mutator_named_operations = "1.0"
    code_revision = "1.0b"
    default_batch_size = 50
    hostname = 'example.com'
    require_explicit_versions = False

    def get_request_user(self):
        return 'A user'

    def createRequest(self, body_instream, environ):
        request = Request(body_instream, environ)
        request.setPublication(WebServiceTestPublication(RootResource))
        return request
