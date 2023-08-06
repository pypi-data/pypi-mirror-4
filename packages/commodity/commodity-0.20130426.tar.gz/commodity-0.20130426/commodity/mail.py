#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import imaplib
import email

from .pattern import memoized
from .str_ import Printable

OK = 'OK'


def all_ok(results):
    return all(x == OK for x in results)


class Account(Printable):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password


class GmailAccount(Account):
    host = 'imap.gmail.com'
    port = 993

    def __init__(self, username, password):
        Account.__init__(self, self.host, self.port, username, password)


class IMAP(Printable):
    """
    IMAP4 mailbox.
    See search operators at http://tools.ietf.org/html/rfc2060.html#section-6.4.4

    >>> account = GmailAccount(username='<user>', password='<pass>')
    >>> mailbox = IMAP(account)
    >>> mailbox.connect()
    >>> mailbox.messages()
    [...]
    >>> mailbox.messages('(SUBJECT {hi})')
    [...]
    >>> mailbox.messages('(ON 17-Feb-2013)')
    [...]
    """

    def __init__(self, account):
        self.account = account
        self.connection = None

    def connect(self):
        self.connection = imaplib.IMAP4_SSL(self.account.host, self.account.port)
        assert self.connection is not None

        results = (
            self.connection.login(self.account.username,
                                  self.account.password)[0],
            self.connection.select()[0])

        return all_ok(results)

    @memoized
    def messages(self, query='ALL'):
        assert self.connection, 'not connected to server'

        result, msg_ids = self.connection.search(None, query)
        assert all_ok([result])

        results = []
        retval = []
        for num in msg_ids[0].split():
            result, msg = self.connection.fetch(num, '(RFC822)')
            retval.append(email.message_from_string(msg[0][1]))
            results.append(result)

        assert all_ok(results)
        return retval

    def __unicode__(self):
        return unicode(self.account['username'])
