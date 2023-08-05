#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import unittest

from mock import patch
from mock import MagicMock as Mock

import pyrax
import pyrax.exceptions as exc
import pyrax.utils as utils
from tests.unit import fakes



class PyraxInitTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        reload(pyrax)
        # Override any config settings that turn off services.
        for key, val in pyrax.services_to_start.items():
            pyrax.services_to_start[key] = True
        self.orig_connect_to_cloudservers = pyrax.connect_to_cloudservers
        self.orig_connect_to_cloudfiles = pyrax.connect_to_cloudfiles
        self.orig_connect_to_cloud_loadbalancers = pyrax.connect_to_cloud_loadbalancers
        self.orig_connect_to_cloud_databases = pyrax.connect_to_cloud_databases
        self.orig_get_service_endpoint = pyrax._get_service_endpoint
        super(PyraxInitTest, self).__init__(*args, **kwargs)
        self.username = "fakeuser"
        self.api_key = "fakeapikey"

    def setUp(self):
        pyrax.set_identity_class(fakes.FakeIdentity)
        pyrax.identity = pyrax.identity_class()
        pyrax.identity.authenticated = True
        pyrax.connect_to_cloudservers = Mock()
        pyrax.connect_to_cloudfiles = Mock()
        pyrax.connect_to_cloud_loadbalancers = Mock()
        pyrax.connect_to_cloud_databases = Mock()
        pyrax._get_service_endpoint = Mock(return_value="http://example.com/")

    def tearDown(self):
        pyrax.connect_to_cloudservers = self.orig_connect_to_cloudservers
        pyrax.connect_to_cloudfiles = self.orig_connect_to_cloudfiles
        pyrax.connect_to_cloud_loadbalancers = self.orig_connect_to_cloud_loadbalancers
        pyrax.connect_to_cloud_databases = self.orig_connect_to_cloud_databases
        pyrax._get_service_endpoint = self.orig_get_service_endpoint

    def test_require_auth(self):
        @pyrax._require_auth
        def testfunc(): pass
        pyrax.identity.authenticated = True
        testfunc()
        pyrax.identity.authenticated = False
        self.assertRaises(exc.NotAuthenticated, testfunc)

    def test_set_credentials(self):
        pyrax.set_credentials(self.username, self.api_key)
        self.assertEqual(pyrax.identity.username, self.username)
        self.assertEqual(pyrax.identity.api_key, self.api_key)
        self.assert_(pyrax.identity.authenticated)

    def test_set_bad_credentials(self):
        self.assertRaises(exc.AuthenticationFailed, pyrax.set_credentials, "bad", "creds")
        self.assertFalse(pyrax.identity.authenticated)

    def test_set_credential_file(self):
        with utils.SelfDeletingTempfile() as tmpname:
            with file(tmpname, "wb") as tmp:
                tmp.write("[rackspace_cloud]\n")
                tmp.write("username = %s\n" % self.username)
                tmp.write("api_key = %s\n" % self.api_key)
            pyrax.set_credential_file(tmpname)
            self.assertEqual(pyrax.identity.username, self.username)
            self.assertEqual(pyrax.identity.api_key, self.api_key)
            self.assert_(pyrax.identity.authenticated)

    def test_set_bad_credential_file(self):
        with utils.SelfDeletingTempfile() as tmpname:
            with file(tmpname, "wb") as tmp:
                tmp.write("[rackspace_cloud]\n")
                tmp.write("username = bad\n")
                tmp.write("api_key = creds\n")
            self.assertRaises(exc.AuthenticationFailed, pyrax.set_credential_file, tmpname)
            self.assertFalse(pyrax.identity.authenticated)

    def test_clear_credentials(self):
        pyrax.set_credentials(self.username, self.api_key)
        # These next lines are required to test that clear_credentials
        # actually resets them to None.
        pyrax.cloudservers = object()
        pyrax.cloudfiles = object()
        pyrax.cloud_loadbalancers = object()
        pyrax.cloud_databases = object()
        default_region = object()
        self.assert_(pyrax.identity.authenticated)
        self.assertIsNotNone(pyrax.cloudfiles)
        pyrax.clear_credentials()
        self.assertFalse(pyrax.identity.authenticated)
        self.assertIsNone(pyrax.identity.username)
        self.assertIsNone(pyrax.identity.api_key)
        self.assertIsNone(pyrax.cloudservers)
        self.assertIsNone(pyrax.cloudfiles)
        self.assertIsNone(pyrax.cloud_loadbalancers)
        self.assertIsNone(pyrax.cloud_databases)

    def test_set_default_region(self):
        orig_region = pyrax.default_region
        new_region = "test"
        pyrax.set_default_region(new_region)
        self.assertEqual(pyrax.default_region, new_region)

    def test_fix_uri_other(self):
        region = "abc"
        svc = "other"
        orig = "http://example.com/v1.0/fake"
        expected = "http://abc.example.com/v1.0/fake"
        fixed = pyrax._fix_uri(orig, region, svc)
        self.assertEqual(fixed, expected)

    def test_fix_uri_compute(self):
        region = "abc"
        svc = "compute"
        orig = "http://example.com/v1.0/fake"
        expected = "http://abc.example.com/v2/fake"
        fixed = pyrax._fix_uri(orig, region, svc)
        self.assertEqual(fixed, expected)

    def test_make_agent_name(self):
        test_agent = "TEST"
        ret = pyrax._make_agent_name(test_agent)
        self.assert_(ret.startswith(test_agent))
        self.assert_(ret.endswith(pyrax.USER_AGENT))

    def test_connect_to_services(self):
        pyrax.connect_to_services()
        pyrax.connect_to_cloudservers.assert_called_once_with()
        pyrax.connect_to_cloudfiles.assert_called_once_with()
        pyrax.connect_to_cloud_loadbalancers.assert_called_once_with()
        pyrax.connect_to_cloud_databases.assert_called_once_with()

    @patch('pyrax._cs_client.Client', new=fakes.FakeService)
    def test_connect_to_cloudservers(self):
        pyrax.cloudservers = None
        pyrax.connect_to_cloudservers = self.orig_connect_to_cloudservers
        pyrax.cloudservers = pyrax.connect_to_cloudservers()
        self.assertIsNotNone(pyrax.cloudservers)

    @patch('pyrax._cf.CFClient', new=fakes.FakeService)
    def test_connect_to_cloudfiles(self):
        pyrax.cloudfiles = None
        pyrax.connect_to_cloudfiles = self.orig_connect_to_cloudfiles
        pyrax.cloudfiles = pyrax.connect_to_cloudfiles()
        self.assertIsNotNone(pyrax.cloudfiles)

    @patch('pyrax.CloudLoadBalancerClient', new=fakes.FakeService)
    def test_connect_to_cloud_loadbalancers(self):
        pyrax.cloud_loadbalancers = None
        pyrax.connect_to_cloud_loadbalancers = self.orig_connect_to_cloud_loadbalancers
        pyrax.cloud_loadbalancers = pyrax.connect_to_cloud_loadbalancers()
        self.assertIsNotNone(pyrax.cloud_loadbalancers)

    @patch('pyrax.CloudDatabaseClient', new=fakes.FakeService)
    def test_connect_to_cloud_databases(self):
        pyrax.cloud_databases = None
        pyrax.connect_to_cloud_databases = self.orig_connect_to_cloud_databases
        pyrax.cloud_databases = pyrax.connect_to_cloud_databases()
        self.assertIsNotNone(pyrax.cloud_databases)

    def test_import_fail(self):
        import __builtin__
        sav_import = __builtin__.__import__
        def fake_import(nm, *args):
            if nm == "rax_identity":
                raise ImportError
            else:
                return sav_import(nm, *args)

        __builtin__.__import__ = fake_import
        self.assertRaises(ImportError, reload, pyrax)
        __builtin__.__import__ = sav_import
        reload(pyrax)



if __name__ == "__main__":
    unittest.main()
