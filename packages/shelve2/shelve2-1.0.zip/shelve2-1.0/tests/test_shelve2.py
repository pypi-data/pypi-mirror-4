"""Tests against the new shelve2 API and JSON encoding.

The implementation is mostly copied from test_shelve.py.
"""

import shelve2

from test_shelve import byteskeydict
import glob
from test import support
from test import mapping_tests
from test.test_dbm import dbm_iterator

class TestShelveBase(mapping_tests.BasicTestMappingProtocol):
    fn = "shelftemp.db"
    counter = 0
    _args = {}

    def __init__(self, *args, **kw):
        mixin = shelve2.get_mixin(self._protocol)
        class ShelfClass(mixin, shelve2.AbstractShelf):
            def __init__(self, dict, writeback=False, keyencoding="utf-8",
                         *args, **kwargs):
                shelve2.AbstractShelf.__init__(self, dict, writeback,
                                               keyencoding)
                mixin.__init__(self, *args, **kwargs)
        self.type2test = ShelfClass

        self._db = []
        mapping_tests.BasicTestMappingProtocol.__init__(self, *args, **kw)

    def _reference(self):
        return { "key1": "value1", "key2": 2, "key3": False }

    def _empty_mapping(self):
        if self._in_mem:
            x = self.type2test(byteskeydict(), **self._args)
        else:
            self.counter += 1
            x = shelve2.open2(self.fn + str(self.counter),
                              serialisation_protocol=self._protocol,
                              **self._args)
        self._db.append(x)
        return x

    def tearDown(self):
        for db in self._db:
            db.close()
        self._db = []
        if not self._in_mem:
            for f in glob.glob(self.fn + "*"):
                support.unlink(f)

class TestPickleFileShelve(TestShelveBase):
    _protocol = "pickle"
    _in_mem = False
class TestJsonFileShelve(TestShelveBase):
    _protocol = "json"
    _in_mem = False
class TestPickleMemShelve(TestShelveBase):
    _protocol = "pickle"
    _in_mem = True
class TestJsonMemShelve(TestShelveBase):
    _protocol = "json"
    _in_mem = True

TESTCASES = [
    TestPickleFileShelve,
    TestJsonFileShelve,
    TestPickleMemShelve,
    TestJsonMemShelve
]

def test_main():
    for module in dbm_iterator():
        support.run_unittest(*TESTCASES)

if __name__ == "__main__":
    test_main()
