import csv
from UserList import UserList

class AddressList(UserList):
    pass


class CSVAddressList(AddressList):

    def __init__(self, fp, fieldnames=None, email_column="email", name_column="name"):
        #detect input file format
        super(CSVAddressList, self).__init__(self)

        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(fp.read(1024))
        fp.seek(0)

        #parse input
        reader = csv.DictReader(fp, fieldnames=fieldnames, dialect=dialect )
        for row in reader:
            self.append({
                "email" : row[email_column],
                "name" : row[name_column],
                "extra" : row,
            })

