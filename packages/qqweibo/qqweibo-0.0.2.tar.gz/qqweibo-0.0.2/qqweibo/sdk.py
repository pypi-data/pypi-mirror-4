#encoding:utf-8

"""
qq weibo sdk
author:tianyu0915@gmail.com
date:2013-02-06
"""

import json
import urllib
import urllib2
import requests

class ClientError(Exception):
    pass

class Client(object):
    base_uri = 'https://open.t.qq.com/cgi-bin/oauth2/'
    api_base_uri = 'https://open.t.qq.com/api/'
    request = requests.session()

    def parseurl(self,urlstr):
        """
        parse the url 
        """
        return dict(urllib2.urlparse.parse_qsl(urlstr))

    def __init__(self,app_key,app_secret,redirect_uri='http://www.sample.com',response_type='code',
            forcelogin=False):

        self.app_key       = app_key
        self.app_secret    = app_secret
        self.redirect_uri  = redirect_uri
        self.response_type = response_type
        self.forcelogin    = forcelogin and 'true' or 'false' 

    def get_authorize_url(self):
        params = {'client_id':self.app_key,'response_type':self.response_type,'redirect_uri':self.redirect_uri,'forcelogin':self.forcelogin}
        return self.base_uri + 'authorize?' + urllib.urlencode(params)

    def get_access_token_from_code(self,code=''):
        """
        获取access token并存入
        """
        params = {'client_id':self.app_key,'client_secret':self.app_secret,'grant_type':'authorization_code',
                'code':code,'redirect_uri':self.redirect_uri}
        res_str = self.request.get(self.base_uri+'access_token',params=params).content
        if 'errorCode' in res_str:
            raise ClientError(res_str)

        if self.set_access_token(res_str):
            return res_str

    def set_access_token(self,access_token_str):
        res_dict = self.parseurl(access_token_str)
        for k,v in res_dict.items():
            setattr(self,k,v)
        return True

    def call(self,api_method,call_method='GET',clientip='127.0.0.1',scope='all',oauth_version='2.a'):
        params = {'access_token':self.access_token,'openid':self.openid,'oauth_consumer_key':self.app_key,
                'clientip':clientip,'scope':scope,'oauth_version':oauth_version}
        
        if call_method == 'GET':
            res = self.request.get(self.api_base_uri+api_method,params=params)
        elif call_method == 'POST':
            res = self.request.get(self.api_base_uri+api_method,params=params)

        if 'errorCode' in res.content:
            raise ClientError(res.content)
        return json.loads(res.content)

    def __getattr__(self,attr):
        return _CallApi(self,attr)

class _CallApi(object):
    """
    """

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        name = '%s/%s' % (self._name, attr)
        return _CallApi(self._client, name)

    def get(self):
        return self._client.call(self._name,'GET')

    def post(self):
        return self._client.call(self._name,'POST')

    def __str__(self):
        return '_Callable object<%s>' % self._name

