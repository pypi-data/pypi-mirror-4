##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import tempfile
import email.MIMEText
import email.Header
import email.MIMEBase
import email.MIMEMultipart
from email import Encoders
from ConfigParser import ConfigParser
from zope.sendmail.mailer import SMTPMailer
from zope.sendmail.delivery import QueuedMailDelivery, QueueProcessorThread
import transaction
from logger import LOG


def getMailConfiguration():
    """ read the email configuration from an INI file and
        return it as dict
    """

    mail_config = os.environ.get('EMAIL_CONFIG')
    if not mail_config:
        raise RuntimeError('No email configuration found')

    if not os.path.exists(mail_config):
        raise RuntimeError('Configured email configuration file not available (%s)' % mail_config)

    CP = ConfigParser()
    CP.read('email.ini')

    hostname = 'localhost'
    username = None
    password = None
    no_tls = False
    force_tls = False
    maildir = tempfile.mkdtemp(prefix='zopyx.smartprintng.server')

    if CP.has_option('mail', 'hostname'): hostname = CP.get('mail', 'hostname')
    if CP.has_option('mail', 'username'): username = CP.get('mail', 'username')
    if CP.has_option('mail', 'password'): password = CP.get('mail', 'password')
    if CP.has_option('mail', 'maildir'): maildir = CP.get('mail', 'maildir')
    if CP.has_option('mail', 'no_tls'): no_tls = CP.getboolean('mail', 'no_tls')
    if CP.has_option('mail', 'force_tls'): force_tls = CP.getboolean('mail', 'force_tls')

    # setup maildir structure
    if not os.path.exists(maildir):
        os.makedirs(maildir)
    for subdir in ('cur', 'tmp', 'new'):
        destdir = os.path.join(maildir, subdir)
        if not os.path.exists(destdir):
            os.makedirs(destdir)

    return dict(hostname=hostname,
                username=username,
                password=password,
                maildir=maildir,
                force_tls=force_tls,
                no_tls=no_tls)


def setupMailer():
    """ Set up zope.sendmail delivery thread """

    config = getMailConfiguration()
    thread = QueueProcessorThread()
    thread.setMailer(makeMailer())
    thread.setQueuePath(config['maildir'])
    thread.start()
    return config

def makeMailer():
    """ Create an SMTP mailer """
    config = getMailConfiguration().copy()
    del config['maildir']
    return SMTPMailer(**config)


def send_email(sender, recipient, subject, body, attachments=[]):
    """ Asynchronous mail delivery """

    msg = email.MIMEMultipart.MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = email.Header.Header(subject, 'UTF-8')
    msg.attach(email.MIMEText.MIMEText(body.encode('UTF-8'), 'plain', 'UTF-8'))

    for att in attachments:
        part = email.MIMEBase.MIMEBase('application', "octet-stream")
        part.set_payload(file(att, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                        'attachment; filename="%s"' % os.path.basename(att))
        msg.attach(part)

    config = getMailConfiguration()
    delivery = QueuedMailDelivery(config['maildir'])
    delivery.send(sender, [recipient], msg.as_string())
    transaction.commit()

