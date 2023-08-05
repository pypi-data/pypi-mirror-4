import base64
import hashlib
import logging
import math
import time

from django.conf import settings
from ebaysuds import EbaySuds, WSDL_URL, ebaysuds_config
from suds.plugin import PluginContainer
from suds.sax.parser import Parser


logging.basicConfig()
log = logging.getLogger(__name__)


class UnrecognisedPayloadTypeError(Exception):
    pass

class NotificationValidationError(Exception):
    pass

class TimestampOutOfBounds(NotificationValidationError):
    pass

class InvalidSignature(NotificationValidationError):
    pass


class NotificationHandler(object):
    def __init__(self, wsdl_url=WSDL_URL, token=None, sandbox=False):
        es_kwargs = {
            'wsdl_url': wsdl_url,
            'sandbox': sandbox,
        }
        if token is not None:
            es_kwargs['token'] = token
        self.client = EbaySuds(**es_kwargs)
        self.saxparser = Parser()

    def decode(self, payload_type, message):
        try:
            payload_method = getattr(self.client.sudsclient.service, payload_type)
        except AttributeError:
            raise UnrecognisedPayloadTypeError('Unrecognised payload type: %s' % payload_type)

        # don balaclava, hijack a suds SoapClient instance to decode our payload for us
        sc_class = payload_method.clientclass({})
        soapclient = sc_class(self.client.sudsclient, payload_method.method)
        
        # copy+pasted from SoapClient.send :(
        plugins = PluginContainer(soapclient.options.plugins)
        ctx = plugins.message.received(reply=message)
        result = soapclient.succeeded(soapclient.method.binding.input, ctx.reply)

        # `result` only contains the soap:Body of the response (parsed into objects)
        signature = self._parse_signature(message)

        if self.validate(result, signature):
            return result

    def _parse_signature(self, message):
        xml = self.saxparser.parse(string=message)
        return xml.getChild("Envelope").getChild("Header").getChild('RequesterCredentials').getChild('NotificationSignature').text

    def validate(self, message, signature):
        """
        As per:
        http://developer.ebay.com/DevZone/XML/docs/WebHelp/wwhelp/wwhimpl/common/html/wwhelp.htm?context=eBay_XML_API&file=WorkingWithNotifications-Receiving_Platform_Notifications.html
        """
        
        timestamp = time.mktime(message.Timestamp.timetuple())
        if not settings.DEBUG:
            # check timestamp is within 10 minutes of current time
            diff_seconds = math.fabs(time.time() - timestamp)
            if diff_seconds > 600:
                raise TimestampOutOfBounds("Payload timestamp was %s seconds away from current time." % diff_seconds)
        
        # make hash
        m = hashlib.md5()
        m.update(str(timestamp))
        m.update(ebaysuds_config.get('keys', 'dev_id'))
        if self.client.sandbox:
            conf_section = 'sandbox_keys'
        else:
            conf_section = 'production_keys'
        m.update(ebaysuds_config.get(conf_section, 'app_id'))
        m.update(ebaysuds_config.get(conf_section, 'cert_id'))
        computed_hash = base64.standard_b64encode(m.hexdigest())
        if computed_hash != signature:
            raise InvalidSignature(signature)

        return True
