# Copyright 2010-2011 Isotoma Limited
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
from yay.nodes import *


class TestSequenceOperations(unittest.TestCase):

    def test_sequence(self):
        l = Sequence([Boxed(1), Boxed(2), Boxed(3)])

        self.failUnlessEqual(l.resolve(), [1, 2, 3])

    def test_sequence_append(self):
        l = Sequence([Boxed(1), Boxed(2), Boxed(3)])
        a = Append(Sequence([Boxed(4), Boxed(5)]))
        a.chain = l

        self.failUnlessEqual(a.resolve(), [1, 2, 3, 4, 5])

    def test_sequence_remove(self):
        l = Sequence([Boxed(1), Boxed(2), Boxed(3)])
        r = Remove(Sequence([Boxed(2)]))
        r.chain = l

        self.failUnlessEqual(r.resolve(), [1, 3])


class TestMapping(unittest.TestCase):

    ctx = None

    def test_get_set(self):
        d = Mapping(None)
        d.set("foo", Boxed(1))

        self.failUnlessEqual(d.get("foo").value, 1)

