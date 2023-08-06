"""Defines the TestSuite class.

Copyright 2013 by Rackspace Hosting, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import testtools

import falcon
from .srmock import StartResponseMock
from .helpers import create_environ


class TestSuite(testtools.TestCase):
    """Scaffolding around testtools.TestCase for testing a Falcon API endpoint.

    Inherit from this and write your test methods. If the child class defines
    a prepare(self) method, this method will be called before executing each
    test method.

    Attributes:
        api: falcon.API instance used in simulating requests.
        srmock: falcon.testing.StartResponseMock instance used in
            simulating requests.
        test_route: Randomly-generated route string (path) that tests can
            use when wiring up resources.


    """

    def setUp(self):
        """Initializer, unittest-style"""

        super(TestSuite, self).setUp()
        self.api = falcon.API()
        self.srmock = StartResponseMock()
        self.test_route = '/' + self.getUniqueString()

        prepare = getattr(self, 'prepare', None)
        if hasattr(prepare, '__call__'):
            prepare()

    def simulate_request(self, path, **kwargs):
        """ Simulates a request.

        Simulates a request to the API for testing purposes.

        Args:
            path: Request path for the desired resource
            kwargs: Same as falcon.testing.create_environ()

        """

        if not path:
            path = '/'

        return self.api(create_environ(path=path, **kwargs),
                        self.srmock)
