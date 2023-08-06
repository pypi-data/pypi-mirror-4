from mailsanity.hackage import reformat
import email
import glob
import unittest

class TestHackage(unittest.TestCase):
    def test_robust(self):
        for mail in glob.iglob('./hackage/*.email'):
            with open(mail) as source:
                msg = email.message_from_file(source)
                reformat(msg)
                print(msg.as_string())

if __name__ == '__main__':
    unittest.main()
