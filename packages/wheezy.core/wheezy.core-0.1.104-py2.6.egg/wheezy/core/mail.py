
""" ``mail`` module.
"""

from mimetypes import guess_type
from os.path import split as path_split
from smtplib import SMTP
from time import time

from wheezy.core.comp import ntob

try:
    from email.charset import CHARSETS
    from email.encoders import encode_base64
    from email.header import Header
    from email.message import Message
    from email.utils import formataddr
    from email.utils import formatdate
    from email.utils import make_msgid
except ImportError:  # pragma: nocover, python2.4
    from email.Charset import CHARSETS  # noqa
    from email.Encoders import encode_base64  # noqa
    from email.Header import Header  # noqa
    from email.Message import Message  # noqa
    from email.Utils import formataddr  # noqa
    from email.Utils import formatdate  # noqa
    from email.Utils import make_msgid  # noqa


# Do not apply Base64 encoding to utf-8 messages
CHARSETS['utf-8'] = (3, None, 'utf-8')


def mail_address(addr, name=None, charset='utf8'):
    """ Returns mail address formatted string.
    """
    try:
        addr.encode('us-ascii')
    except UnicodeEncodeError:
        addr = '@'.join([p.encode('idna').decode('us-ascii')
                         for p in addr.split('@', 1)])
    return name and formataddr((mime_header(name, charset), addr)) or addr


class MailMessage(object):
    """ Mail message.
    """

    def __init__(self, subject='', content='',
                 from_addr=None, to_addrs=None,
                 cc_addrs=None, bcc_addrs=None, reply_to_addrs=None,
                 content_type='text/plain', charset='us-ascii'):
        self.subject = subject
        self.content = content
        self.from_addr = from_addr
        self.to_addrs = to_addrs or []
        self.cc_addrs = cc_addrs or []
        self.bcc_addrs = bcc_addrs or []
        self.reply_to_addrs = reply_to_addrs or []
        self.content_type = content_type
        self.charset = charset
        self.date = time()
        self.attachments = []
        self.alternatives = []

    def recipients(self):
        return set(self.to_addrs + self.cc_addrs + self.bcc_addrs)


class Attachment(object):
    """ An attachment to mail message.
    """

    def __init__(self, name, content, content_type=None, disposition=None,
                 name_charset=None, content_charset=None):
        self.name = name
        self.content = content
        self.content_type = content_type
        self.disposition = disposition
        self.name_charset = name_charset
        self.content_charset = content_charset

    @classmethod
    def from_file(cls, path):
        """ Creates an attachment from file.
        """
        ignore, name = path_split(path)
        f = open(path, 'rb')
        try:
            return cls(name, f.read())
        finally:
            f.close()


class Alternative(object):
    """ Represents alternative mail message.
    """

    def __init__(self, content, content_type='text/html', charset=None):
        self.content = content
        self.content_type = content_type
        self.charset = charset
        self.related = []


class Related(object):
    """ A resource related to alternative mail message.
    """

    def __init__(self, content_id, content, content_type):
        self.content_id = content_id
        self.content = content
        self.content_type = content_type

    @classmethod
    def from_file(cls, path):
        """ Creates a related mail resource from file.
        """
        ignore, name = path_split(path)
        content_type, ignore = guess_type(name)
        if content_type is None:
            content_type = 'application/octet-stream'
        f = open(path, 'rb')
        try:
            return cls(name, f.read(), content_type)
        finally:
            f.close()


class SMTPClient(object):
    """ SMTP client that can be used to send mail.
    """

    def __init__(self, host='127.0.0.1', port=25, use_tls=False,
                 username=None, password=None):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password

    def send(self, message):
        """ Sends a single mail message.
        """
        recepients = message.recipients()
        content = ntob(mime(message).as_string(), message.charset)
        # keep connection scope minimal
        client = self.connect()
        try:
            client.sendmail(message.from_addr, recepients, content)
        finally:
            client.quit()

    def send_multi(self, messages):
        """ Sends multiple mail messages.
        """
        args = [(message.from_addr, message.recipients(),
                 ntob(mime(message).as_string(), message.charset))
                for message in messages]
        # keep connection scope minimal
        client = self.connect()
        try:
            for arg in args:
                client.sendmail(*arg)
        finally:
            client.quit()

    def connect(self):
        smtp = SMTP()
        #smtp.set_debuglevel(1)
        smtp.connect(self.host, self.port)
        if self.use_tls:
            smtp.starttls()
        if self.username:
            smtp.login(self.username, self.password)
        return smtp


# region: internal details

def mime(message):
    charset = message.charset
    m = mime_part(message.content, message.content_type, charset)
    subparts = message.content and [m] or []
    if message.alternatives:
        subparts += [mime_alternative(a) for a in message.alternatives]
        if len(subparts) > 1:
            m = mime_multipart('multipart/alternative', subparts)
            subparts = [m]
        else:
            m = subparts[0]
    if message.attachments:
        subparts += [mime_attachment(a) for a in message.attachments]
        m = mime_multipart('multipart/mixed', subparts)
    m['Message-ID'] = make_msgid()
    m['Subject'] = message.subject
    m['Date'] = formatdate(message.date, localtime=True)
    m['From'] = message.from_addr
    m['To'] = ', '.join(message.to_addrs)
    if message.cc_addrs:
        m['Cc'] = ', '.join(message.cc_addrs)
    if message.bcc_addrs:
        m['Bcc'] = ', '.join(message.bcc_addrs)
    if message.reply_to_addrs:
        m['Reply-To'] = ', '.join(message.reply_to_addrs)
    return m


def mime_header(value, charset):
    try:
        value.encode('us-ascii')
    except UnicodeEncodeError:
        return Header(value, charset).encode()
    else:
        return value


def mime_part(content, content_type, content_charset=None):
    m = Message()
    m.add_header('Content-Type', content_type)
    m.set_payload(content, content_charset)
    if not content_type.startswith('text'):
        encode_base64(m)
    return m


def mime_multipart(content_type, subparts):
    m = Message()
    m.add_header('Content-Type', content_type)
    m.set_payload(subparts)
    return m


def mime_alternative(a):
    m = mime_part(a.content, a.content_type, a.charset)
    if a.related:
        subparts = [m]
        for r in a.related:
            m = mime_part(r.content, r.content_type)
            m.add_header('Content-ID', r.content_id)
            subparts.append(m)
        m = mime_multipart('multipart/related', subparts)
    return m


def mime_attachment(attachment):
    content_type = attachment.content_type
    if not content_type:
        content_type, ignore = guess_type(attachment.name)
        if content_type is None:
            content_type = 'application/octet-stream'
    m = mime_part(attachment.content, content_type,
                  attachment.content_charset)
    name = attachment.name
    if attachment.name_charset:
        name = (attachment.name_charset, '', name)
    # see http://www.ietf.org/rfc/rfc2183.txt
    m.add_header('Content-Disposition',
                 attachment.disposition or 'attachment',
                 filename=name)
    return m
