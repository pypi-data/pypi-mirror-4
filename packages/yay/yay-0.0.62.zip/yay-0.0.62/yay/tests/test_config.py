# Copyright 2012 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from yay.config import Config

class TestConfig(unittest.TestCase):

    def test_lookup(self):
        c = Config()
        c.load("""
            foo: 1
            bar: 2
            baz: 3
            """)

        self.failUnlessEqual(c.lookup("foo").resolve(), 1)
        self.failUnlessEqual(c.lookup("bar").resolve(), 2)
        self.failUnlessEqual(c.lookup("baz").resolve(), 3)

