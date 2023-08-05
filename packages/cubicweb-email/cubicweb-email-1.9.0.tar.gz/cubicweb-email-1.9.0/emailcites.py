"""some utilities to process email information

:organization: Logilab
:copyright: 2007-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


def parse_body(body, quote='>'):
    """return a `ParsedMessage` instance where actual content is separated from
    cited content
    """
    res = []
    level = 0
    current = []
    seenlevels = set()
    for line in body.splitlines(True):
        newlevel = 0
        while line.startswith(quote):
            newlevel += 1
            line = line[1:].lstrip()
        if line.strip() == '--':
            break # ignore following signature
        if newlevel != level:
            # detect lines such as
            #   On Wed, Jan 23, 2008 at 06:48:22PM +0100, machin wrote:
            # preceding citation
            if not newlevel in seenlevels and res and res[-1][1] and \
                   res[-1][1][-1].rstrip().endswith(':'):
                current.insert(0, res[-1][1].pop())
            seenlevels.add(newlevel)
            res.append( (level, current) )
            current = []
        level = newlevel
        current.append(line)
    res.append( (level, current) )
    pmsg = ParsedMessage()
    for level, lines in res:
        para = ''.join(lines).strip()
        if not para:
            continue
        if level > 0 :
            pmsg.cites.append(para)
        else:
            pmsg.content.append(para)
    return pmsg

class ParsedMessage(object):
    def __init__(self):
        self.content = []
        self.cites = []

    @property
    def actual_content(self):
        return '\n'.join(self.content)
    @property
    def cited_content(self):
        return '\n'.join(self.cites)

# import sys
# from mailbox import UnixMailbox
# from maboa.umessage import message_from_file
# from cubicweb.web.uilib import remove_html_tags

# def ignore_cite(para):
#     para = para.lower()
#     if para == u'ok':
#         return True
#     return False

# class CitesDetector:
#     """XXX TODO
#     * unitttest :)
#     * limit search citations according to UTC date
#     * skip block under a reasonable size (['ok'])
#     * normalize block text
#     * enhance block detection (extract quote string in a first phase)
#     """
#     def _get_body(self, message):
#         body = []
#         for part in message.walk():
#             if part.get_content_maintype() == 'text':
#                 payload = part.get_payload(decode=True)
#                 if part.get_content_type().endswith('html'):
#                     payload = remove_html_tags(payload)
#                 body.append(payload)
#             elif part.get_content_type() == 'application/octet-stream':
#                 body.append(u'attached file: %s (%s)' %
#                             (part.get_filename(''), part.get_content_type()))
#             elif part.get_content_type() == 'multipart/mixed':
#                 pass
#         return u'\n\n--- part ---\n\n'.join(body)

#     def _parse_mailbox(self, mailbox):
#         """ don't match
#         """
#         for message in mailbox:
#             body = self._get_body(message)
#             yield parse_body(body)

#     def process_mailbox(self, filename):
#         """
#         """
#         mboxfile = open(filename)
#         mbox = UnixMailbox(mboxfile, message_from_file)
#         msgs = list(self._parse_mailbox(mbox))
#         mboxfile.close()
#         cites = {}
#         for index, msg in enumerate(msgs):
#             for index2, msg2 in enumerate(msgs):
#                 if index == index2 :
#                     continue
#                 for cite in msg.cites:
#                     if ignore_cite(cite):
#                         continue
#                     for para in msg2.content:
#                         if cite in para:
#                             cites.setdefault((index,index2), [])
#                             cites[(index, index2)].append( (cite, para) )
#         return msgs, cites

# if __name__ == '__main__':
#     from pprint import pprint
#     msgs, cites = CitesDetector().process_mailbox(sys.argv[1])
#     for index, msg in enumerate(msgs):
#         print '*'*80, index
#         pprint(msg.content)
#         pprint(msg.cites)
#     print
#     keys = cites.keys()
#     keys.sort()
#     for key in keys:
#         print '='*80, key
#         pprint( cites[key] )
