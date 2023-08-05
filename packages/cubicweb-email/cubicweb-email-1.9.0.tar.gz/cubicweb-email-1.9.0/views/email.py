"""Specific views for email related entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import is_instance
from cubicweb.uilib import soup2xhtml
from cubicweb.view import EntityView
from cubicweb.web import uicfg, formwidgets
from cubicweb.web.views import baseviews, primary

for rtype in ('sender', 'recipients', 'cc', 'parts'):
    uicfg.primaryview_section.tag_subject_of(('Email', rtype, '*'), 'hidden')

uicfg.autoform_field_kwargs.tag_attribute(('Email', 'subject'),
                                          {'widget': formwidgets.TextInput})

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Email', 'attachment', '*'),
                                                 True)

uicfg.actionbox_appearsin_addmenu.tag_object_of(('EmailThread', 'forked_from', 'EmailThread'),
                                                True)


def formated_sender(email):
    if email.sender:
        return email.sender[0].view('oneline')
    # sender address has been removed, look in email's headers
    message = email.umessage_headers()
    if message:
        return xml_escape(message.get('From', ''))
    return email._cw._('unknown sender')

class EmailPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Email')

    def render_entity_attributes(self, entity):
        self.w(u'<div class="emailheader"><table>')
        self.w(u'<tr><td>%s</td><td>%s</td></tr>' %
               (self._cw._('From'), formated_sender(entity)))
        self.w(u'<tr><td>%s</td><td>%s</td></tr>' %
               (self._cw._('To'), ', '.join(ea.view('oneline') for ea in entity.recipients)))
        if entity.cc:
            self.w(u'<tr><td>%s</td><td>%s</td></tr>' %
                   (self._cw._('CC'), ', '.join(ea.view('oneline') for ea in entity.cc)))
        self.w(u'<tr><td>%s</td><td>%s</td></tr>' %
               (self._cw._('Date'), self._cw.format_date(entity.date, time=True)))
        self.w(u'<tr><td>%s</td><td>%s</td></tr>' %
               (self._cw._('Subject'), xml_escape(entity.subject)))
        self.w(u'</table></div><div class="emailcontent">')
        for part in entity.parts_in_order():
            content, mime = part.content, part.content_format
            if mime == 'text/html':
                content = soup2xhtml(content, self._cw.encoding)
            elif 'pgp-signature' in mime:
                content = entity._cw_mtc_transform(content, mime, 'text/html', self._cw.encoding)
            elif mime != 'text/xhtml':
                content = xml_escape(content)
                if mime == 'text/plain':
                    content = content.replace('\n', '<br/>').replace(' ', '&nbsp;')
            # XXX some headers to skip if html ?
            self.w(content)
            self.w(u'<br class="partseparator"/>')
        self.w(u'</div>')

    def render_entity_title(self, entity):
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), xml_escape(entity.dc_title())))


class EmailHeadersView(baseviews.EntityView):
    """display email's headers"""
    __regid__ = 'headers'
    __select__ = is_instance('Email')
    title = _('headers')
    templatable = False
    content_type = 'text/plain'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.headers)


class EmailOneLineView(baseviews.OneLineView):
    """short view usable in the context of the email sender/recipient (in which
    case the caller should specify its context eid) or outside any context
    """
    __select__ = is_instance('Email')
    title = _('oneline')

    def cell_call(self, row, col, contexteid=None):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="email">')
        self.w(u'<i>%s&nbsp;%s</i> ' % (
            self._cw._('email_date'), self._cw.format_date(entity.date, time=True)))
        sender = entity.senderaddr
        if sender is None or contexteid != sender.eid:
            self.w(u'<b>%s</b>&nbsp;%s '
                   % (self._cw._('email_from'), formated_sender(entity)))
        if contexteid not in (r.eid for r in entity.recipients):
            recipients = ', '.join(r.view('oneline') for r in entity.recipients)
            self.w(u'<b>%s</b>&nbsp;%s'
                   % (self._cw._('email_to'), recipients))
        self.w(u'<br/>\n<a href="%s">%s</a>' % (
            xml_escape(entity.absolute_url()), xml_escape(entity.subject)))
        self.w(u'</div>')


class EmailOutOfContextView(EmailOneLineView):
    """short view outside the context of the email"""
    __regid__ = 'outofcontext'
    title = _('out of context')


class EmailInContextView(EmailOneLineView):
    """short view inside the context of the email"""
    __regid__ = 'incontext'

class EmailTreeItemView(EmailOutOfContextView):
    __regid__ = 'treeitem'
    title = None

class EmailPartOutOfContextView(baseviews.OutOfContextView):
    """out of context an email part is redirecting to related email view"""
    __select__ = is_instance('EmailPart')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        entity.reverse_parts[0].view('outofcontext', w=self.w)


class EmailThreadView(EntityView):
    __regid__ = 'emailthread'
    __select__ = is_instance('EmailThread')

    def entity_call(self, entity):
        # get top level emails in this thread (ie message which are not a reply
        # of a message in this thread)
        #
        # Warn: adding Y in_thread E changes the meaning of the query since it joins
        # with messages which are not a direct reply (eg if A reply_to B, B reply_to C
        # B is also retreived since it's not a reply of C
        #
        # XXX  union with
        #   DISTINCT Any X,D ORDERBY D WHERE X date D, X in_thread E, X reply_to Y,
        #   NOT Y in_thread E, E eid %(x)s'
        # to get message which are a reply of a message in another thread ?
        # we may get duplicates in this case
        rset =  self._cw.execute('DISTINCT Any X,D ORDERBY D '
                                 'WHERE X date D, X in_thread E, '
                                 'NOT X reply_to Y, E eid %(x)s',
                                 {'x': entity.eid})
        if rset:
            self.w(u'<ul>')
            self.w(u'\n'.join(email.view('tree') for email in rset.entities()))
            self.w(u'</ul>')


class EmailThreadPrimaryView(primary.PrimaryView):
    __select__ = is_instance('EmailThread')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<h1>%s</h1>' % xml_escape(entity.title))
        entity.view('emailthread', w=self.w)

