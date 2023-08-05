"""import an mbox or a single email into an cubicweb application

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import re

from cubicweb import Binary

CLEANUP_RGX = re.compile(r'\bre\s*:', re.I|re.U)
def cleanup_subject(string):
    return CLEANUP_RGX.sub('', string).strip()

def combinaison(list):
    """given a list return an iterator on possible combinaisons between all the
    elements in the list but without identity:

    >>> list(combinaison([1,2,3]))
    [(1, 2), (2, 3), (1, 3)]
    >>> list(combinaison([1,2,3,4]))
    [(1, 2), (2, 3), (3, 4), (1,3), (1,4), (2,4)]

    note: in python 2.6, this can be written:
    >>> import itertools
    >>> itertools.combinations([1,2,3], 2)
    """
    list = list[:]
    while len(list) > 1:
        first = list.pop()
        for i in list:
            yield (first, i)

class MBOXImporter(object):
    """import content of a Unix mailbox into cubicweb as Email (and related) objects"""

    def __init__(self, cnx, verbose=False, interactive=False,
                 skipsign=False, autocommit=False):
        self.cnx = cnx
        self.schema = cnx.get_schema()
        self.req = cnx.request()
        self.execute = self.req.execute
        self._verbose = verbose
        self._interactive = interactive
        self._skipsign = skipsign
        self.created = {}
        self.skipped = []
        self.error = []
        self.autocommit = autocommit

    def autocommit_mode(self):
        self.autocommit = True

    def _notify_created(self, etype, eid):
        if self._verbose:
            print 'create', etype, eid
        self.created.setdefault(etype, []).append(eid)

    def _notify_skipped(self, messageid):
        if self._verbose:
            print 'skipping', messageid
        self.skipped.append(messageid)

    def import_mbox_stream(self, stream):
        from mailbox import UnixMailbox as Mailbox
        from rfc822 import parsedate
        from logilab.common.umessage import message_from_file
        for message in sorted(Mailbox(stream, message_from_file),
                              key=lambda x:parsedate(x['Date'])):
            try:
                self.import_message(message)
                if self.autocommit:
                    self.cnx.commit()
            except Exception, ex:
                import traceback
                traceback.print_exc()
                if self.autocommit:
                    msgid = message.get('message-id')
                    self.error.append(msgid)
                    self.cnx.rollback()
                    if self._interactive:
                        quest = 'failed to import message %s (%s). Continue [N/y] ?\n'
                        if raw_input(quest % (msgid, ex)).lower() != 'y':
                            break
                else:
                    raise

    def import_message(self, message):
        # check this email hasn't been imported
        msgid = message.get('message-id')
        rset = self.execute('Email X WHERE X messageid %(id)s', {'id': msgid})
        if rset:
            self._notify_skipped(msgid)
            return
        # Email entity
        subject = message.get('subject') or u'(no subject)'
        sender = message.multi_addrs('from')[0]
        sendereid = self.address_eid(sender[1], sender[0])
        email = self.req.create_entity('Email', messageid=msgid,
                                       subject=subject, date=message.date(),
                                       headers=message.headers(),
                                       sender=sendereid)
        self._notify_created('email', email.eid)
        # link to mailing list
        self.mailinglist_link(message, email.eid)
        # link to recipients
        for name, addr in message.multi_addrs('to'):
            self.execute('SET X recipients Y WHERE X eid %(x)s, Y eid %(y)s',
                         {'x': email.eid, 'y': self.address_eid(addr, name)})
        for name, addr in message.multi_addrs('cc'):
            self.execute('SET X cc Y WHERE X eid %(x)s, Y eid %(y)s',
                         {'x': email.eid, 'y': self.address_eid(addr, name)})
        # link to replied email if any
        replyto = message.get('in-reply-to')
        replyeid = None
        if replyto:
            rset = self.execute('Email X WHERE X messageid %(id)s', {'id': replyto})
            if rset:
                replyeid = rset[0][0]
                self.execute('SET X reply_to Y WHERE X eid %(x)s, Y eid %(y)s',
                             {'x': email.eid, 'y': replyeid})
        # link to an EmailThread
        self.execute('SET X in_thread Y WHERE X eid %(x)s, Y eid %(y)s',
                     {'x': email.eid, 'y': self.thread_eid(subject, replyeid)})
        self._part_index = 0
        self._context = None
        self._alternatives = []
        self.import_message_parts(message, email.eid)

    def mailinglist_link(self, message, eid):
        if not 'MailingList' in self.schema:
            return
        try:
            listid = message.multi_addrs('list-id')[0][1]
        except IndexError:
            return
        mlrset = self.execute('MailingList X WHERE X mlid %(id)s', {'id': listid})
        if mlrset:
            self.execute('SET X sent_on Y WHERE X eid %(x)s, Y eid %(y)s',
                         {'x': eid, 'y': mlrset[0][0]})

    def import_message_parts(self, message, emaileid):
        # XXX only parts and attachments are used not content, alternative...
        if message.is_multipart():
            self._context = message.get_content_type().split('/')[1]
            if self._context == 'alternative':
                self._alternatives.append([])
            for part in message.get_payload():
                self.import_message_parts(part, emaileid)
            if self._context == 'alternative':
                alternatives = self._alternatives.pop()
                for eid1, eid2 in combinaison(alternatives):
                    self.execute('SET X alternative Y WHERE X eid %(x)s, Y eid %(y)s',
                                  {'x': eid1, 'y': eid2})
            self._context = None
        else:
            self._import_message_part(message, emaileid)

    def _import_message_part(self, part, emaileid):
        """finally import a non multipart message (ie non MIME message or a
        not compound part of a MIME message
        """
        assert not part.is_multipart()
        contenttype = part.get_content_type()
        main, sub = contenttype.split('/')
        data = part.get_payload(decode=True)
        if main == 'text':
            encoding = u'UTF-8'
        elif contenttype == 'application/pgp-signature':
            if self._skipsign:
                return
            encoding = u'ascii'
            if isinstance(data, str):
                data = unicode(data, encoding)
            self.req.set_shared_data('raw_content_%s_%s' %
                                     (emaileid, self._part_index + 1),
                                     str(part.message))
        else:
            encoding = None
        name = part.get_filename()
        if name or main != 'text' and contenttype != 'application/pgp-signature':
            # suppose if we have a name, this is an attachement else this is a
            # part/alternative
            name = name or u'no name'
            if isinstance(data, unicode):
                data = data.encode('utf8')
            epart = self.req.create_entity('File', data=Binary(data),
                                           data_name=name,
                                           data_format=contenttype,
                                           data_encoding=encoding)
            self._notify_created('file', epart.eid)
            self.execute('SET X attachment Y WHERE X eid %(x)s, Y eid %(y)s',
                         {'x': emaileid, 'y': epart.eid})
        else:
            self._part_index += 1
            epart = self.req.create_entity('EmailPart',
                                           content=data,
                                           content_format=contenttype,
                                           ordernum=self._part_index)
            self._notify_created('emailpart', epart.eid)
            self.execute('SET X parts Y WHERE X eid %(x)s, Y eid %(y)s',
                         {'x': emaileid, 'y': epart.eid})
            if self._context == 'alternative':
                self._alternatives[-1].append(epart.eid)

    def address_eid(self, address, alias=None):
        rql = 'Any X WHERE X is EmailAddress, X address %(addr)s'
        rset = self.execute(rql, {'addr': address})
        if not rset:
            address = address.lower()
            rset = self.execute(rql, {'addr': address})
        if not rset:
            # create a new email address to link to
            alias = alias or None
            # XXX could try to link created address to a person
            eaddress = self.req.create_entity('EmailAddress', address=address,
                                              alias=alias)
            self._notify_created('emailaddress', eaddress.eid)
            return eaddress.eid
        # check for a prefered form if any
        return rset.get_entity(0, 0).prefered.eid

    def thread_eid(self, subject, replyeid):
        if replyeid is not None:
            rset = self.execute('EmailThread X WHERE Y in_thread X, Y eid %(y)s',
                                {'y': replyeid})
            if rset:
                return rset[0][0]
        subject = cleanup_subject(subject)
        rset = self.execute('EmailThread X WHERE X title %(title)s',
                            {'title': subject})
        if rset:
            return rset[0][0]
        thread = self.req.create_entity('EmailThread', title=subject)
        self._notify_created('emailthread', thread.eid)
        return thread.eid

