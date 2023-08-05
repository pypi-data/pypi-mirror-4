#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os import popen


class NoSender(Exception):
    def __str__(self):
        return "No sender specified"


class NoRecipient(Exception):
    def __str__(self):
        return "No recipient specified"


class NoSendmail(Exception):
    def __str__(self):
        return "No sendmail path specified"


class NoSubject(Exception):
    def __str__(self):
        return "No subject specified"


class NoBody(Exception):
    def __str__(self):
        return "No body specified"


class SendmailError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "error %s" % self.value


class Simplemail(object):
    """ This object sets up the email sending procedure.  Subject and
    the message body are both encoded in utf-8 for non-ascii charsets.

    The following arguments are required to set the default procedure:

    sender -- contains the string with the sender information in the
              "Sender Name <email@domain.tld> format.
    recipient -- contains a list with the recipients addresses like
                 ["user1@domain.tld", "user2@domain.tld"].
    subject -- contains a string with the email subject like "Subject".

    The following arguments are optional:

    sendmail -- contains a string with the sendmail path.  The default
                value is "/usr/sbin/sendmail"
    cc -- contains a tuple with the cc-recipients addresses.  Format is
          the same as recipient.
    bcc -- contains a tuple with the bcc-recipients addresses.  Format
           is the same as recipient.
    """

    def __init__(self, sendmail="/usr/sbin/sendmail", **kwargs):
        self.defaults = {}
        if sendmail:
            self.defaults["sendmail"] = sendmail
        self.defaults.update(kwargs)

    def send(self, **kwargs):
        """ This method actually sends the email.  But it allows you to
        override all the default values from the object constructor.

        For example:
                   Simplemail.send(sender="John Doe <jdoe@domain.tld>")
        It will use all the values from the initial object definition,
        but it will override the sender value.
        """
        settings = self.defaults.copy()
        settings.update(kwargs)
        if not "sendmail" in settings.keys():
            raise NoSendmail
        if not "sender" in settings.keys():
            raise NoSender
        if not "recipient" in settings.keys():
            raise NoRecipient
        if not "subject" in settings.keys():
            raise NoSubject
        if not "body" in settings.keys():
            raise NoBody
        sm = popen("%s -t" % settings["sendmail"], "w")
        sm.write("From: %s\n" % settings["sender"])
        sm.write("To: %s\n" % ", ".join(settings["recipient"]))
        if "cc" in settings.keys():
            sm.write("Cc: %s\n" % ", ".join(settings["cc"]))
        if "bcc" in settings.keys():
            sm.write("Bcc: %s\n" % ", ".join(settings["bcc"]))
        sm.write("Subject: %s\n" % settings["subject"])
        sm.write("Content-Type: text/plain; charset=UTF-8; format=flowed\n")
        sm.write("Content-Transfer-Encoding: 8bit\n")
        sm.write("\n")
        sm.write("%s\n" % settings["body"])
        status = sm.close()
        if status:
            raise SendmailError(status)
