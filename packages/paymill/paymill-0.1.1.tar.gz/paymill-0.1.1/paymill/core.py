"""
Copyright (C) 2013 Client Side Web <rutherford@clientsideweb.net>
minimal API client library for Paymill API v2
"""

import urllib2
import urllib
import base64
import logging
import json

API_VERSION = 'v2'
BASE_URL = 'https://api.paymill.de/%s/'
API_URL = BASE_URL % API_VERSION

PAYMILL_TYPES = ['client', 'offer', 'payment', 'subscription', 'transaction']

class Paymill(object):
    """
    The object for encapsulating CRUD operations on the Paymill REST API
    """
    
    def __init__( self, private_key):
        """
        Initialize a new paymill interface connection.
        private_key: The private key to sign API calls with.
        """
        self.private_key = private_key
        
    def _apicall(self, cmd, params=None, req="POST", header=None):
        """
        Call an API endpoint.
        cmd: The URL endpoint of the entity to post to. Eg 'clients'
        params: a dict of (name: value) parameters
        req: The request type to be made. If parameters are passed, this will be ignored and treated as POST
        header: Optional HTTP headers to add
        Returns a dictionary object populated with the json returned.
        """
        json_dict = {}
        request = urllib2.Request(API_URL+cmd)
        base64string = base64.standard_b64encode('%s:' % self.private_key)
        request.add_header('Authorization', 'Basic %s' % base64string)
        if header:
            for k, val in header.iteritems():
                request.add_header(k, val)
        request.get_method = lambda: req
        params = urllib.urlencode(params) if params else {}        
        try:
            result = urllib2.urlopen(request, params)
            json_dict = json.load(result)
        except urllib2.URLError, err:
            logging.error(err.reason)
        return json_dict
    
    def create(self, obj, args):
        """
        Create an object.
        obj: Object type. One of PAYMILL_TYPES.
        args: Dict of fields for the newly created object and their values.
        """        
        if obj not in PAYMILL_TYPES:
            return None
        return self._apicall(obj+'s', args)
        
    def update(self, obj, oid, args):
        """
        Update an existing object.
        obj: Object type. One of PAYMILL_TYPES.
        oid: Unique identifier of the object.
        args: Dict of fields and their updated values.
        """
        if obj not in PAYMILL_TYPES:
            return None
        return self._apicall(obj+'/'+str(oid), args, 'PUT')
    
    def delete(self, obj, oid):
        """
        Delete an object.
        obj: Object type. One of PAYMILL_TYPES.
        oid: Unique identifier of the object.
        """
        if obj not in PAYMILL_TYPES:
            return None
        return self._apicall(obj+'/'+str(oid), req='DELETE')
        
    def list(self, obj, order=None, csv=False):
        """
        List all objects of a certain type
        obj: Object type. One of PAYMILL_TYPES
        order: Field on which to order returned data.
        csv: For type client specifically, returns data in CSV format.
        """
        if obj not in PAYMILL_TYPES:
            return None
        if order:
            args = {'order':order}
        else:
            args = {}
        if csv:
            header = {'Accept':'text/csv'}
        else:
            header = {}
        return self._apicall(obj+'s', args, header)
    
