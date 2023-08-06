"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Copyright (C) 2013 CERN
"""
import sys
import unittest

from mtb.conf import unify_keys, TreeDict
from mtb.string import u_
from mtb.test import parametrized


UNIFY_KEYS_SETS_NAMES = "error given result".split()
UNIFY_KEYS_SETS = (
    (None, None, None),
    (None, "", ""),
    (None, {'hello': 'world'}, {'hello': 'world'}),
    (None, {u_('hello'): 'world'}, {'hello': 'world'}),
    (None, {u_('hello'): 'world', 'foo': {u_('hello'): 'world'}},
     {'hello': 'world', 'foo': {'hello': 'world'}}),
)


class ConfTest(unittest.TestCase):
    """ Test :py:mod:`mtb.conf` utilities module. """

    def test_unicode_keywords_function(self):
        """ Test unicode keywords function. """
        error = None
        unicode_dict = {u_('hello'): 'world'}
        try:
            some_function(**unicode_dict)
        except Exception:
            error = sys.exc_info()[1]
        if type(error) is TypeError:
            unify_keys(unicode_dict)
            some_function(**unicode_dict)

    @parametrized(UNIFY_KEYS_SETS_NAMES, UNIFY_KEYS_SETS)
    def test_unify_keys(self, error, given, result):
        """ Test unify keys. """
        print("running unify keys for %s" % (given, ))
        got = None
        result_got = None
        try:
            result_got = unify_keys(given)
        except Exception:
            got = type(sys.exc_info()[1])
        if got == error:
            if result_got != result:
                raise AssertionError(
                    "%s was expected to return %s, it returned %s" %
                    (given, result, result_got, ))
        else:
            raise AssertionError(
                "%s was expected to fail with error: %s" %
                (given, error, ))
        print("...test unify keys ok")

    def test_treedict(self):
        """ Test TreeDict. """
        print("running TreeDict tests")
        example = TreeDict()
        example["foo"] = "bar"
        example["foo4-bar"] = "value4"
        example["foo5-bar-next"] = "value6"
        example.setdefault("foo2", "bar2")
        example.setdefault("foo3-bar", "value3")
        example.setdefault("foo3-bar", "value5")
        self.assertEquals("bar", example["foo"])
        self.assertEquals("value4", example["foo4-bar"])
        self.assertEquals("value4", example["foo4"]["bar"])
        self.assertEquals("value6", example["foo5-bar-next"])
        self.assertEquals("value6", example["foo5"]["bar"]["next"])
        self.assertEquals("value6", example["foo5-bar"]["next"])
        self.assertEquals("bar2", example["foo2"])
        self.assertEquals("value3", example["foo3-bar"])
        self.assertEquals("bar", example.get("foo"))
        self.assertEquals("value4", example.get("foo4-bar"))
        self.assertEquals("value4", example.get("foo4").get("bar"))
        self.assertEquals("value6", example.get("foo5-bar-next"))
        self.assertEquals("value6", example.get("foo5").get("bar").get("next"))
        self.assertEquals("value6", example.get("foo5-bar").get("next"))
        self.assertEquals("bar2", example.get("foo2"))
        self.assertEquals("value3", example.get("foo3-bar"))
        self.assertEquals(None, example.get("foo-notebar"))
        self.assertRaises(KeyError, lambda: example["foo-notebar"])
        print("...test TreeDict ok")


if __name__ == "__main__":
    unittest.main()
