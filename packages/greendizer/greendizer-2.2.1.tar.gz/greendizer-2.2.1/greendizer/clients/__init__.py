# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from greendizer.clients.http import ApiError, RateLimitError
from greendizer.clients.resources.buyers import Buyer
from greendizer.clients.resources.sellers import Seller
from greendizer.clients.resources.anonymous import Company, Invoice


__all__ = ('SellerClient', 'BuyerClient', 'AnonymousClient')  


class _ClientBase(object):
    '''
    Represents a generic client class with support for API limits, and
    authentication.
    '''
    def __init__(self):
        '''
        Initializes a new instance of the _ClientBase class.
        '''
        self.api_rate_limit = -1
        self.api_rate_limit_remaining = -1
        self.api_rate_limit_reset = datetime.now() + timedelta(seconds=600)
    
    @property
    def limit_exceeded(self):
        '''
        Gets a boolean indicating whether the API rate limit has been
        execeeded or not.
        @return: bool
        '''
        return (self.api_rate_limit_remaining == 0 and
                datetime.now() < self.api_rate_limit_reset)
        
    def sign_request(self, request):
        pass


class Client(_ClientBase):
    '''
    Represents a Greendizer API client
    '''
    def __init__(self, user, access_token=None, email=None, password=None):
        '''
        Initializes a new instance of the Client class.
        Either provide an email/password, or a valid access_token
        @param user:User User resource
        @param email:str Email
        @param password:str Password
        @param access_token:str OAuth access token
        '''
        self.__authorization_header = None
        self._user = user
        self._email = email
        self._password = password
        self._access_token = access_token
        self._generate_authorization_header()
        
        
    def __getattr__(self, attr):
        if attr in ['oauth_token', 'access_token']:
            return self._access_token
        raise AttributeError
        
    def __setattr__(self, attr, val):
        if attr in ['oauth_token', 'access_token']:
            self._access_token = val
            self._generate_authorization_header()
        return super(Client, self).__setattr__(attr, val)

    @property
    def email_address(self):
        '''
        Gets the email address of the user
        @return: str
        '''
        return self._email

    @property
    def user(self):
        '''
        Gets the current user
        @return: User
        '''
        return self._user

    def _generate_authorization_header(self):
        '''
        Generates an HTTP authorization header depending
        on the authentication method set at the instance
        initialization.
        '''
        if self._email and self._password:
            encoded = ("%s:%s" % (self._email,self._password)).encode('base64')
            self.__authorization_header = "BASIC " + encoded.strip("\n")
        else:
            self.__authorization_header = "BEARER " + (self._access_token or '')

    def sign_request(self, request):
        '''
        Signs a request to make it pass security.
        @param request:greendizer.http.Request
        @return: greendizer.http.Request
        '''
        request["Authorization"] = self.__authorization_header
        return request


class BuyerClient(Client):
    '''
    Represents a buyer oriented client of the Greendizer API
    '''
    def __init__(self, oauth_token=None, email=None, password=None):
        '''
        Initializes a new instance of the BuyerClient class
        '''
        super(BuyerClient, self).__init__(Buyer(self), oauth_token, email,
                                          password)

    @property
    def buyer(self):
        '''
        Gets the current buyer
        @return: Buyer
        '''
        return self.user


class SellerClient(Client):
    '''
    Represents a seller oriented client of the Greendizer API
    '''
    def __init__(self, oauth_token=None, email=None, password=None):
        '''
        Initializes a new instance of the SellerClient class
        '''
        self.__private_key = None
        self.__public_key = None
        super(SellerClient, self).__init__(Seller(self), oauth_token, email,
                                           password)

    @property
    def keys(self):
        '''
        Gets the private key that will be used to sign the XMLi sent from
        this computer.
        @return: str
        '''
        if self.__private_key and self.__public_key:
            return (self.__private_key, self.__public_key)

        return None, None

    @property
    def seller(self):
        '''
        Gets the current seller
        @return: Seller
        '''
        return self.user

    def import_keys(self, private, public, passphrase=None):
        '''
        Imports the private and public keys that will be used to sign
        invoices.
        @param private:file File-like object or stream
        @param public:file File-like object or stream
        @param passphrase:str Optional pass phrase to decrypt the private key.
        '''
        try:
            from Crypto.PublicKey import RSA
        except ImportError:
            raise ImportError('PyCrypto 2.5 module is required to enable ' \
                              'XMLi signing. Please visit:\n' \
                              'http://pycrypto.sourceforge.net/')

        self.__private_key = RSA.importKey(private.read(),
                                           passphrase=passphrase)
        self.__public_key = RSA.importKey(public.read())


class AnonymousClient(_ClientBase):
    '''
    Represents a client that can be used to access authentication-free
    resources.
    '''
    def get_company(self, id_):
        '''
        Retrieves a company by its ID.
        @returns: greendizer.resources.anonymous.Company
        '''
        return Company(self, id_)
    
    def get_invoice(self, secret_key):
        '''
        Retrieves an invoice by its secret key.
        @returns: greendizer.resources.anonymous.Invoice
        '''
        return Invoice(self, secret_key)