"""entity classes for entity types provided by the cubicweb email package

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import re

from logilab.common import umessage

from cubicweb.entities import AnyEntity, fetch_config, adapters
from cubicweb.selectors import is_instance
from cubes.email.emailcites import parse_body


class Email(AnyEntity):
    """customized class for Email entities"""
    __regid__ = 'Email'
    fetch_attrs, fetch_order = fetch_config(['subject'])

    def dc_title(self):
        return self.subject

    @property
    def senderaddr(self):
        return self.sender and self.sender[0] or None

    @property
    def in_reply_to(self):
        return self.reply_to and self.reply_to[0] or None

    @property
    def thread(self):
        return self.in_thread and self.in_thread[0] or None

    def parts_in_order(self, prefered_mime_type='text/html'):
        """sort an email parts in order, selecting among alternatives according to a
        prefered mime type
        """
        parts_by_eid = {}
        alternatives = []
        result = []
        for part in self.parts:
            parts_by_eid[part.eid] = part
            if part.alternative:
                for altset in alternatives:
                    if part.eid in altset:
                        break
                else:
                    alternatives.append(set(p.eid for p in part.alternative))
                    alternatives[-1].add(part.eid)
            else:
                result.append(part)
        if alternatives:
            for altset in alternatives:
                selected = [parts_by_eid[peid] for peid in altset
                            if parts_by_eid[peid].content_format == prefered_mime_type]
                if selected:
                    selected = selected[0]
                else:
                    selected = parts_by_eid[altset.pop()]
                result.append(selected)
        return sorted(result, key=lambda x: x.ordernum)

    def references(self):
        result = set()
        message = self.umessage_headers()
        if not message:
            return result
        replyto = message.get('In-reply-to')
        if replyto:
            result.add(replyto)
        for refs in message.get_all('References', ()):
            result.update(refs.split())
        return result

    lines_rgx = re.compile('^Lines:\s*\d+\s*\n', re.I|re.U|re.M)
    clength_rgx = re.compile('^Content-Length:\s*\d+\s*\n', re.I|re.U|re.M)
    ctype_rgx = re.compile('^Content-Type:[^:]', re.I|re.U|re.M)

    def umessage_headers(self):
        if not self.headers:
            return None
        headers = self.lines_rgx.sub('', self.headers)
        headers = self.clength_rgx.sub('', headers)
        headers = self.ctype_rgx.sub('Content-type: text/plain; charset=utf8', headers)
        headers = headers.encode('utf8')
        return umessage.message_from_string(headers + '\n\n')



class EmailPart(AnyEntity):
    """customized class for EmailPart entities"""
    __regid__ = 'EmailPart'

    def dc_title(self):
        return '%s (%s %s)' % (self.email.subject,
                               self._cw._('part'), self.ordernum)

    @property
    def email(self):
        return self.reverse_parts[0]

    def parent(self):
        """for breadcrumbs"""
        return self.email

    def actual_content(self):
        """return content of this part with citations and signature removed

        this method may raise `TransformError` exception if the part can't
        be displayed as text/plain.
        """
        content = self.printable_value('content', format='text/plain')
        return parse_body(content).actual_content


class EmailThread(AnyEntity):
    """customized class for EmailThread entities"""
    __regid__ = 'EmailThread'
    fetch_attrs, fetch_order = fetch_config(['title'])

    def dc_title(self):
        return self.title


class EmailITreeAdapter(adapters.ITreeAdapter):
    __select__ = is_instance('Email')
    tree_relation = 'reply_to'


class EmailPartIFTIAdapter(adapters.IFTIndexableAdapter):
    """customize EmailPart IFTI adapter so we don't index pgp signature"""
    __select__ = adapters.IFTIndexableAdapter.__select__ & is_instance('EmailPart')

    def get_words(self):
        try:
            if self.entity.contenttype == 'application/pgp-signature':
                return []
        except AttributeError:
            return super(EmailPartIFTIAdapter, self).get_words()

