import sys
from test.test_dbm import dbm_iterator
from test import support

def test_main():
    sys.path.insert(0, "tests")
    import test_shelve, test_shelve2
    for module in dbm_iterator():
        support.run_unittest(*(test_shelve.TESTCASES + test_shelve2.TESTCASES))

if __name__ == "__main__":
    test_main()
