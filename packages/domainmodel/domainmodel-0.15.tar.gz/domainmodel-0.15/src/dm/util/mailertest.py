import unittest

import dm.util.mailer

def suite():
    suites = [
        unittest.makeSuite(TestSend),
    ]
    return unittest.TestSuite(suites)


class TestSend(unittest.TestCase):

    def test_send(self):
        to = ['admin@localhost']
        from_address = to[0]
        subject = 'Testing the email system'

        # Todo: Add some SMTP account details for testing.
        # Todo: Reinstate the next line.
        #dm.util.mailer.send(from_address, to, subject, subject)

