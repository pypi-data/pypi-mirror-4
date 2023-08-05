from datetime import datetime
from decimal import Decimal
import json
import urllib
import urllib2
import logging

log = logging.getLogger('surebilling')

def http_post(url, args = {}):
#    print 'POSTing to ', url, args
    return urllib2.urlopen(url, urllib.urlencode(args)).read()

API_SERVER = 'http://test.flow.com:8001'

try:
    from django.conf import settings
    API_SERVER = settings.SUREBILLING_API_SERVER
except (ImportError, AttributeError):
    pass

def api_serialize(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise Exception("Unsupported type %s: %s", type(obj), str(obj))

class BillingException(Exception):
    pass

class Client(object):
    def __init__(self, apikey, apiserver = API_SERVER):
        self.apikey = apikey
        self.apiserver = apiserver.rstrip('/')

    def call(self, function, **kw):
        try:
            data = json.loads(http_post('%s/api/%s/' % (self.apiserver, function), dict(apikey = self.apikey, json = json.dumps(kw, default = api_serialize))))
        except urllib2.HTTPError, e:
            log.exception(e.fp.read())
            raise e

        if data['status'] != 0:
            raise BillingException("Server returned status %d: %s" % (data['status'], data['data']))
        return data['data']

    def recurring_add(self, **kw):
        return self.call('recurring_add', **kw)

    def recurring_add_pendingitem(self, **kw):
        return self.call('recurring_add_pendingitem', **kw)

    def recurring_get(self, **kw):
        return self.call('recurring_get', **kw)

    def recurring_list(self, **kw):
        return self.call('recurring_list', **kw)

    def recurring_delete(self, id):
        return self.call('recurring_delete', id = id)

    def recurring_mod_resource(self, id, resource, delta):
        """
        id - recurring invoice ID
        resource - ID of resource to be modified
        delta - delta to modify by
        """
        return self.call('recurring_mod_resource', id = id, resource = resource, delta = delta)

    def invoice_add(self, **kw):
        return self.call('invoice_add', **kw)

    def invoice_delete(self, id):
        return self.call('invoice_delete', id = id)

    def invoice_add_item(self, **kw):
        return self.call('invoice_add_item', **kw)

    def invoice_remove_item(self, **kw):
        return self.call('invoice_remove_item', **kw)

    def invoice_list_items(self, **kw):
        return self.call('invoice_list_items', **kw)

    def customer_add(self, **kw):
        return self.call('customer_add', **kw)

    def customer_get(self, id):
        return self.call('customer_get', id = id)

    def customer_update(self, **kw):
        return self.call('customer_update', **kw)

    def customer_delete(self, **kw):
        return self.call('customer_delete', **kw)

    def customer_balance(self, **kw):
        return self.call('customer_balance', **kw)

    def customer_balance_multi(self, **kw):
        return self.call('customer_balance_multi', **kw)

    def customer_invoices(self, **kw):
        return self.call('customer_invoices', **kw)

    def sso_token(self, **kw):
        return self.call('sso_token', **kw)

