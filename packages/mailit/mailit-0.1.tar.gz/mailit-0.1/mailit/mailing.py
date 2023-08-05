from email.mime.text import MIMEText

class MassMail(object):

    def __init__(self, server):
        self.connection = server

    def send(self, fromaddr, subject, address_list, content):
        message = MIMEText(content)
        message['From'] = fromaddr
        message['Subject'] = subject

        for recipient in address_list:
            message['To'] = recipient['name'] + ' <' + recipient['email'] + '>'
            reply = self.connection.sendmail ( fromaddr, recipient, message.as_string() )
