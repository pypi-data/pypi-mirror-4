# -*- coding: utf-8 -*-
from datetime import datetime
from greendizer.clients import http
from greendizer.clients.resources import Company


class Invoice(object):
    '''
    Represents an invoice retrieved using its secret key.
    '''
    def __init__(self, client, secret_key):
        '''
        Initializes a new instance of the Invoice class.
        @param client:AnonymousClient
        @param secret_key:str Invoice secret key
        '''
        self.client = client
        self._last_modified = datetime(1970, 1, 1)
        self._secret_key = secret_key
    
    @property
    def uri(self):
        '''
        Gets the relative URI of the invoice.
        @returns: str
        '''
        return 'invoices/%s/' % self._secret_key
    
    @property
    def absolute_uri(self):
        '''
        Gets the absolute uri of the invoice.
        @returns: str
        '''
        return http.API_ROOT +  self.uri
    
    @property
    def etag(self):
        '''
        Gets the ETag of the invoice.
        @returns: greendizer.clients.http.Etag
        '''
        return http.Etag(self._last_modified, self.id)
    
    @property
    def id(self):
        '''
        Gets the secret key used to retrieve this invoice.
        @returns: str
        '''
        return self._secret_key
    
    def _load(self, accept, head=False):
        request  = http.Request(client=self.client,
                                method='HEAD' if head else 'GET',
                                uri=self.uri,)
        request['Accept'] = accept
        response = request.get_response()
        self._last_modified = response['etag'].last_modified
        return response
    
    def get_xmli(self, head=False):
        '''
        Returns the XMLi representation of the invoice
        @returns: str
        '''
        return self._load(accept='application/xml+xmli', head=head).raw_data
    
    def get_pdf_url(self, accept='application/pdf', head=False):
        '''
        Returns the URL to a PDF representation of the invoice.
        @returns: tuple (str, dict)
        '''
        response = self._load(accept=accept, head=head)
        return response['Location'], response.data