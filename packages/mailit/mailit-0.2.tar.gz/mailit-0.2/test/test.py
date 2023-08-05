import unittest
import sys
import os.path
from StringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage
from email.mime.text import MIMEText

sys.path.append( os.path.realpath(__file__) + "../" )

import mailit

sample_csv_address_list_1 = """email,name,extra_data_1,extra_data_2
person1@host.pl,"Person 1",x,y
person2@host.pl,"Person 2",1,4
person3@host.pl,"Person,3",1,5
"""

sample_csv_address_list_2 = """email;name;extra_data_1;extra_data_2
person1@host.pl;"Person 1";x;y
person2@host.pl;"Person "2"";1;4
person3@host.pl;"Person,3";1;5
"""

class MyTestCase(unittest.TestCase):


    def test_samples(self):
        addr_list_1 = mailit.addresses.CSVAddressList(StringIO(sample_csv_address_list_1))
        addr_list_2 = mailit.addresses.CSVAddressList(StringIO(sample_csv_address_list_2))

        self.assertEqual( len(addr_list_1), 3)
        self.assertEqual( len(addr_list_2), 3)

        self.assertEqual( addr_list_1[0]["email"], "person1@host.pl")
        self.assertEqual( addr_list_2[0]["email"], "person1@host.pl")

    def test_sending(self):
        import mock
        smtp = mock.MockSMTPConnection()
        mailer = mailit.mailing.MassMail(smtp)
        addr_list = mailit.addresses.CSVAddressList(StringIO(sample_csv_address_list_1))
        mailer.send ( "TEST <test@localhost>", "TEST", addr_list, "TEST MESSAGE FROM MASS MAILER")
        self.assertEqual( smtp.received_messages_count(), 3)

if __name__ == '__main__':
    unittest.main()
