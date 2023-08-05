#!/usr/bin/env python

import unittest
import json
from personis.server import base, mkmodel
from personis import client
import os
import shutil
import sys
import logging
import tempfile
import httplib2
from urllib import urlencode
import json
import pprint

class TestPersonisApps(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR)
        client_secrets = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json')
        p = httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, proxy_host='www-cache.it.usyd.edu.au', proxy_port=8000)
        cls.um = client.util.LoginFromClientSecrets(filename=client_secrets, 
            http=httplib2.Http(proxy_info=p, disable_ssl_certificate_validation=True), 
            credentials='server_test_cred.dat')
        cobj = client.Context(Identifier='test', Description='a test component')
        t = cls.um.mkcontext(context=[''], contextobj=cobj)
        cobj = client.Component(Identifier="firstname", component_type="attribute", Description="First name", value_type="string")
        res = cls.um.mkcomponent(context=["test"], componentobj=cobj)
        cobj = client.Component(Identifier="lastname", component_type="attribute", Description="Last name", value_type="string")
        res = cls.um.mkcomponent(context=["test"], componentobj=cobj)
        cobj = client.Component(Identifier="gender", component_type="attribute", Description="Gender", value_type="enum", value_list=['male','female'])
        res = cls.um.mkcomponent(context=["test"], componentobj=cobj)
        cobj = client.Component(Identifier="email", component_type="attribute", Description="email address", value_type="string")
        res = cls.um.mkcomponent(context=["test"], componentobj=cobj)

        vobj = client.View(Identifier="fullname", component_list=["firstname", "lastname"])
        cls.um.mkview(context=["test"], viewobj=vobj)

    @classmethod
    def tearDownClass(cls):
        #cls.stopq.put('exit')
        #print 'here1'
        #cls.serverp.join()
        #print 'here2' 
        #shutil.rmtree('models')
        cls.um.delcontext(context=["test"])

    def test_register_app(self):
        appdetails = self.um.registerapp(app="MyHealth", desc="My Health Manager", password="pass9")
        self.assertEqual(appdetails['description'], u'My Health Manager')
        apps = self.um.listapps()
        self.assertIn(u'MyHealth', apps.keys())

        self.um.setpermission(context=["test"], app="MyHealth", permissions={'ask':True, 'tell':False})

        perms = self.um.getpermission(context=["test"], app="MyHealth")
        self.assertEquals(perms, {'ask': True, 'tell': False})

        p = httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, proxy_host='www-cache.it.usyd.edu.au', proxy_port=8000)
        h = httplib2.Http(proxy_info=p, disable_ssl_certificate_validation=True)
        data = {'modelname': 'jamesuther', 'context': ['test'], 'view': ['email'], 'version': '11.2', 'user': 'MyHealth', 
        'resolver': {'evidence_filter': 'all'}, 'password': 'pass9', 'showcontexts': True}
        resp, content = h.request("https://s0.personis.name/ask", "POST", json.dumps(data))
        c = json.loads(content)
        self.assertEquals(c['val'][0][0]['Description'], 'email address')
        self.um.deleteapp(app="MyHealth")

        apps = self.um.listapps()
        self.assertNotIn(u'MyHealth', apps)



if __name__ == '__main__':
    unittest.main()
