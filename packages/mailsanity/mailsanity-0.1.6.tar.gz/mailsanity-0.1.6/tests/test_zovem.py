#!/usr/bin/env python
from mailsanity.zovem import reformat
import email
import glob
import unittest

class TestZovem(unittest.TestCase):
    def test_robust(self):
        for mail in glob.iglob('./zovem/*.email'):
            with open(mail) as source:
                msg = email.message_from_file(source)
                reformat(msg)

if __name__ == '__main__':
    unittest.main()
