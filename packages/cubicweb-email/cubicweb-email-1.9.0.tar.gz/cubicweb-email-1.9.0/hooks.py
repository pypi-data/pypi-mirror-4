"""hooks triggered on email entities creation:

* look for state change instruction (XXX security)
* set email content as a comment on an entity when comments are supported and
  linking information are found

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import TransformError

from cubicweb import UnknownEid, typed_eid
from cubicweb.mail import parse_message_id
from cubicweb.selectors import is_instance
from cubicweb.server import hook


def fix_ownership(session, eid, email):
    sender = email.senderaddr.email_of
    if sender and sender.e_schema == 'CWUser' and sender.eid != session.user.eid:
        # match a user which is not the session's user, set owned_by / created_by
        session.execute('SET X owned_by U WHERE X eid %(x)s, U eid %(u)s',
                        {'x': eid, 'u': sender.eid})
        session.execute('SET X created_by U WHERE X eid %(x)s, U eid %(u)s',
                        {'x': eid, 'u': sender.eid})


class ExtractEmailInformation(hook.Operation):
    """generate a comment on the original entity if supported"""

    def precommit_event(self):
        email = self.email
        # should create a Comment ?
        info = self.info
        origeid = typed_eid(info['eid'])
        try:
            origetype = self.session.describe(origeid)[0]
        except UnknownEid:
            self.error('email %s is referencing an unknown eid %s',
                       email.messageid, origeid)
            return
        if origetype in self.session.vreg.schema['comments'].objects('Comment'):
            try:
                part = email.parts_in_order(prefered_mime_type='text/plain')[0]
            except IndexError:
                pass
            else:
                try:
                    self.insert_comment(origeid, part)
                except:
                    self.exception('while generating comment on %s from email %s',
                                   origeid, email)

    def insert_comment(self, eid, emailpart):
        com = self.session.execute(
            'INSERT Comment C: C content %(content)s, '
            'C content_format %(format)s, C comments X, C generated_by E '
            'WHERE X eid %(x)s, E eid %(e)s',
            {'x': eid, 'e': self.email.eid, 'format': u'text/plain',
             'content': emailpart.actual_content()})
        fix_ownership(self.session, com[0][0], self.email)


class AnalyzeEmailText(hook.Operation):
    """check if there are some change state instruction in the mail content"""

    def precommit_event(self):
        text = self.email.subject
        for part in self.email.parts_in_order(prefered_mime_type='text/plain'):
            try:
                text += ' ' + part.actual_content()
            except TransformError:
                continue
        # XXX use user session if gpg signature validated
        parser = self.session.vreg['components'].select('textanalyzer', self.session)
        parser.parse(self, text)

    def fire_event(self, event, evargs):
        if event == 'state-changed':
            evargs['trinfo'].set_relations(generated_by=self.email)
            fix_ownership(self.session, evargs['trinfo'].eid, self.email)


class AddEmailHook(hook.Hook):
    """an email has been added, check if associated content should be created
    """
    __regid__ = 'extractmailcontent'
    __select__ = hook.Hook.__select__ & is_instance('Email')
    events = ('after_add_entity',)

    def __call__(self):
        if 'comments' in self._cw.repo.schema:
            for msgid in self.entity.references():
                info = parse_message_id(msgid, self._cw.vreg.config.appid)
                self.info('extracted information from message id %s: %s',
                          msgid, info)
                if info:
                    ExtractEmailInformation(self._cw, email=self.entity, info=info)
                    break
        AnalyzeEmailText(self._cw, email=self.entity)
