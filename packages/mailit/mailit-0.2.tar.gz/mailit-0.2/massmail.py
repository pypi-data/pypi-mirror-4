#!/bin/env python
import mailit
import sys
import os
from optparse import OptionParser, Values
import logging
import urlparse
import smtplib
import getpass
from email.mime.text import MIMEText

def main():
    parser = OptionParser(usage="""\
Send the contents of a file to a selection of email addresses.

Usage: %prog [options]

-r, -f ,-t, -b, -s - all options are required.
If you do not provide username/password in the server URL, you will be
prompted for them.
""")
    parser.add_option('-r', '--recipients',
        type='string', action='store', metavar='FILE', default=[], dest='recipients',
        help="CSV file with a list of e-mail recipients. The file must include a header "
             "with at least two defined fields: 'email' and 'name'."
    )

    parser.add_option('-f', '--from',
        type='string', action='store', metavar='EMAIL', dest='from_address',
        help="""The value of the 'From' header field (required)""" )

    parser.add_option('-t', '--subject',
        type='string', action='store', metavar='SUBJECT', dest='subject',
        help="""The value of the 'Subject' header field (required)""" )

    parser.add_option('-b', '--body',
        type='string', action='store', metavar='FILE',
        dest='body_source_file',
        help='A file containing the message body.')

    parser.add_option('-s', '--server',
        type='string', action='store', metavar='URL',
        dest='server_url',
        help='An SMTP server URL. (eg. smtp://login:password@smtp.google.com:25/, ssl://login:pass@smtp.yahoo.com:465/')

    opts, args = parser.parse_args()

    if  opts.server_url is None or \
        opts.body_source_file is None or \
        opts.subject is None or opts.from_address is None or opts.recipients is None:
        'Exit printing help, when a mandatory parameter is missing.'
        parser.print_help()
        sys.exit()

    url = urlparse.urlparse(opts.server_url)

    if url.port is None:
        if url.scheme == 'ssl': url.port = 465
        else: url.port = 25

    #Prompt user for credentials if not supplied on the command line
    username, password = url.username, url.password
    if username is None:
        username = raw_input("{0.hostname} login:".format(url))

    if password is None:
        password = getpass.getpass("{1}@{0.hostname} password:".format(url, username))

    try:
        with open(opts.recipients, 'r') as f:
            address_list = mailit.addresses.CSVAddressList(f)
    except:
        print "Error reading", opts.recipients
        sys.exit(1)

    try:
        with open(opts.body_source_file, 'r') as f:
            body = f.read()
    except:
        print "Error reading", opts.body_source_file
        sys.exit(1)

    print "-" * 80
    print body
    print "-" * 80

    confirm = raw_input("Sending message [{0.subject}] from [{0.from_address}] to {1} recipients. "
                    "Confirm (Y/N)?".format(opts, len(address_list)))

    if confirm.upper() != "Y":
        sys.exit(1)

    try:
        if url.scheme == 'ssl':
            connection = smtplib.SMTP_SSL( url.hostname, url.port )
        else:
            connection = smtplib.SMTP( url.hostname, url.port )

        connection.login(username, password)

    except Exception, e:
        print e
        sys.exit()

    errors = []
    try:
        for recipient in address_list:
            message = MIMEText(body, 'plain', 'utf8')
            message['From'] = opts.from_address
            message['Subject'] = opts.subject
            message['To'] = "{name} <{email}>".format(**recipient)
            print "Sending to ", message['To'],
            try:
                reply = connection.sendmail(opts.from_address, message['To'], message.as_string() )
                print "[Sent]"
            except Exception, e:
                print '[Error] ', `e`
                errors.append((`e`, recipient['email']))
    finally:
        connection.close()

    if len(errors) > 0:
        print
        print "The message could not be sent to the following recipients:"
        for (msg, email) in errors:
            print email, msg



if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        logging.exception("Unhandled error!")

