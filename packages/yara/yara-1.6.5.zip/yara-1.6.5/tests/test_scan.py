import sys
import os
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import unittest

from yara import scan

TEST_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'rules')

class TestScanNamespace(unittest.TestCase):

    def test_list(self):
        sys.stdout = StringIO()
        try:
            scan.main(['--list'])
            sys.stdout.seek(0)
            out = sys.stdout.read()
        finally:
            sys.stdout = sys.__stdout__
        self.assertTrue("example.packer_rules" in out)

    def test_yara_file(self):
        sys.stderr = StringIO()
        try:
            scan.main(['-r', os.path.join(TEST_ROOT, 'meta.yar')])
            sys.stderr.seek(0)
            out = sys.stderr.read()
        finally:
            sys.stderr = sys.__stderr__
        
        self.assertTrue("does not exist" not in out, msg="got %s" % out)
