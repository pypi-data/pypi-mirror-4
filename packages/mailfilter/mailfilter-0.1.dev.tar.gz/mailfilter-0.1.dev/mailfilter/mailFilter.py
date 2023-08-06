#!/usr/bin/env python

"""
Filter HTML and blacklisted attachments.


- An HTML attachment is discarded if a text equivalent is found, otherwise the
  attachment is converted to text.
- Attachments that have a blacklisted md5sum are discarded.

Note that the input and output file can be specified as - in which case
standard input or standard output is used respectively.
"""

import re
import os
import md5
import bs4
import argparse
#import html2text
import Levenshtein
from email import parser, MIMEText, MIMEMultipart

def distance(m1, m2):
    """
    Calculate the distance between two messages.

    @arg m1: The first message.
    @type m1: str
    @arg m2: The second message.
    @type m2: str

    @returns: The distance between {m1} and {m2}.
    @rtype: float
    """
    # Remove newlines and multiple spaces from both messages.
    s1, s2 = map(lambda x: re.sub(" +", " ", x.replace('\n', ' ')), (m1, m2))

    return Levenshtein.distance(s1, s2) / float(max(len(s1),
        len(s2)))
#distance

def h2t(html):
    """
    Convert HTML to text.

    @arg html: Am HTML document.
    @type html: str

    @returns: Text version of {html}.
    @rtype: str
    """
    #replace = [
    #    ("&nbsp_place_holder;", " ")
    #]

    #text = html2text.html2text(html)
    #for i in replace:
    #    text = text.replace(i[0], i[1])

    #return text #.encode("utf-8")
    soup = bs4.BeautifulSoup(html)

    if soup.style:
        soup.style.extract()

    return soup.get_text()
#h2t

class MailFilter(object):
    """
    Class for the filtering of HTML and blacklisted attachments.
    """
    blacklistFile = "%s/%s" % (os.getenv("HOME"), ".config/mailFilter_bl")
    __blacklistMessage = "removed blacklisted attachment: %s"
    __dropMessage = "discarded HTML attachment: distance=%.2f"
    __convertMessage = "converted HTML to text"

    def __init__(self, inputHandle, blacklistHandle, threshold, reportDrop):
        """
        Initialise the class.

        @arg inputHandle: Open readable handle to the input file.
        @type inputHandle: stream
        @arg blacklistHandle: Open readable handle to the blacklist file.
        @type blacklistHandle: stream
        @arg threshold: Threshold for the distance function.
        @type threshold: float
        @arg drop: Silently drop a blacklisted attachment if True.
        @type drop: bool
        """
        self.message = parser.Parser().parse(inputHandle)
        self.__threshold = threshold
        self.__reportDrop = reportDrop
        self.__text = []

        # Make a dictionary with the md5sum as key and the comment as value.
        self.__blacklist = dict(map(lambda x: x.strip().split(None, 1),
            blacklistHandle.readlines()))

        self.__inspect(self.message)
        headers = self.message._headers
        self.message = self.__messageFilter(self.message)
        new_headers = list(self.message._headers)
        self.message._headers = headers
        for i in new_headers:
            if i[0] in self.message.keys():
                self.message.replace_header(i[0], i[1])
            else:
                self.message.add_header(i[0], i[1])
        #for
    #__init__

    def __decodeContent(self, message):
        """
        Decode the content of a message.

        @arg message: A message.
        @type message: object

        @returns: Decoded content of a message.
        @rtype: str
        """
        content = message.get_payload(decode=True)
        charset = message.get_content_charset()

        if charset:
            return content.decode(charset)
        return content.decode()
    #__decodeContent

    def __replacePart(self, note, payload=None):
        """
        Manipulate the payload of a message.
        - A note can be added depening on the choice of dropping.

        @arg note: Note to add.
        @type note: str
        @arg payload: Payload of a message.
        @type payload: object

        @returns: 
        @rtype: object
        """
        if self.__reportDrop:
            if payload:
                part = MIMEMultipart.MIMEMultipart()
                part.attach(payload)
                part.attach(MIMEText.MIMEText(note, "unknown"))
                return part
            #if

            return MIMEText.MIMEText(note, "unknown")
        #if

        return payload
    #__replacePart

    def __inspect(self, message):
        """
        Extract all plain text attachments for later use.

        @arg message: A message.
        @type message: object
        """
        if not message.is_multipart():
            contentType = message.get_content_type()

            if contentType == "text/plain":  # Store text attachment.
                self.__text.append(self.__decodeContent(message))
        #if
        else:
            for i in message.get_payload():
                self.__inspect(i)
    #__inspect

    def __messageFilter(self, message):
        """
        Filter HTML and blacklisted attachments.

        @arg message: A message.
        @type message: object

        @returns: A filtered message.
        @rtype: object
        """
        if not message.is_multipart():
            contentType = message.get_content_type()
            content = message.get_payload(decode=True)
            md5sum = md5.new(content).hexdigest()

            if md5sum in self.__blacklist:   # Blacklisted attachments.
                return self.__replacePart(self.__blacklistMessage %
                    self.__blacklist[md5sum])
            elif contentType == "text/html": # HTML attachments.
                text = h2t(self.__decodeContent(message))
                dist = min(map(lambda x: distance(text, x), self.__text) +
                    [1.0])

                if dist > self.__threshold: # Not discardable.
                    return self.__replacePart(self.__convertMessage,
                        payload=MIMEText.MIMEText(text.encode("utf-8")))
                else:                       # Discardable.
                    return self.__replacePart(self.__dropMessage % dist)
            #elif
            return message
        #if
        else:
            payload = []
            
            for part in message.get_payload():
                filtered = self.__messageFilter(part)

                if filtered:
                    payload.append(filtered)
            #for
            message.set_payload(payload)

            return message
        #else
    #__messageFilter
#MailFilter

def main():
    """
    Main entry point.
    """
    usage = __doc__.split('\n\n\n')

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument("-r", dest="drop", default=False, action="store_true",
        help="report dropped attachments")
    parser.add_argument("-t", dest="threshold", type=float, default=0.05,
        help="distance threshold (%(type)s default=%(default)s)")
    parser.add_argument("-b", dest="blacklist", type=argparse.FileType("r"),
        default=open(MailFilter.blacklistFile, "a+"), help="blacklist file")
    parser.add_argument("INPUT", type=argparse.FileType("r"),
        help="input file")
    parser.add_argument("OUTPUT", type=argparse.FileType("w"),
        help="output file")
    args = parser.parse_args()

    # Write filtered message.
    args.OUTPUT.write(str(MailFilter(args.INPUT, args.blacklist,
        args.threshold, args.drop).message))
    args.OUTPUT.write("\n")
#main

if __name__ == '__main__':
    main()
