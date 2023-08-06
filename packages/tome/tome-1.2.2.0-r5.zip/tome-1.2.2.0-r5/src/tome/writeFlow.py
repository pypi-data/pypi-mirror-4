#!/usr/bin/python
"""
Copyright 2013 Brian Mearns

This file is part of Tome.

Tome is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tome is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Tome.  If not, see <http://www.gnu.org/licenses/>.
"""
import Tome
import cStringIO
import wrapUtil


class FlowWriter(object):
    def __init__(self, ostream, linewidth = 78):
        self.__linewidth = linewidth
        self.__colnum = 0
        self.__writer = wrapUtil.TextFormatter(ostream, linewidth)


    def writeBlockSegment(self, segment, pre=False):
        first = True
        for par in segment:
            if not first:
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
            first = False
            
            for child in par:
                self.writeSegment(child, pre)


    def writeSegment(self, segment, pre=False):
        if isinstance(segment, Tome.TaggedSegment):
            tag = segment.tag()

            #Paragraphs
            if tag == "p":
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
                for child in segment:
                    self.writeSegment(child, pre)
                return

            elif tag == "pre":
                pre = True
                self.__writer.writeLnbrk()
                self.__writer.setPreformatted(True)
                self.__writer.write("=")
                for child in segment:
                    self.writeSegment(child, pre)
                self.__writer.setPreformatted(False)
                self.__writer.writeLnbrk()
                return

            #Formatting
            elif tag == "b":
                self.__writer.write("*{")
                close = "}*"
            elif tag == "i":
                self.__writer.write("/{")
                close = "}/"
            elif tag == "em":
                self.__writer.write("!{")
                close = "}!"
            elif tag == "u":
                self.__writer.write("_{")
                close = "}_"

            #Text objects
            elif tag == "ellips":
                self.__writer.write("...")
                return
            elif tag == "md":
                self.__writer.write("---")
                return
            elif tag == "nd":
                self.__writer.write("--")
                return
            elif tag == "sp":
                self.__writer.write(" ")
                return
            elif tag == "lnbrk":
                self.__writer.writeLnbrk()
                if pre:
                    self.__writer.write("=")
                return

            #Block elements
            elif tag == "q":
                self.__writer.write("\"{")
                self.writeBlockSegment(segment, pre)
                self.__writer.write("}\"")
                return
            elif tag == "sq":
                self.__writer.write("'{")
                self.writeBlockSegment(segment, pre)
                self.__writer.write("}'")
                return
            elif tag == "n":
                self.__writer.write("^{")
                self.__writer.writeLnbrk()
                self.__writer.indent()
                self.writeBlockSegment(segment, pre)
                self.__writer.outdent()
                self.__writer.writeLnbrk()
                self.__writer.write("}^")
                return
            elif tag == "bq":
                self.__writer.writeLnbrk()
                self.__writer.write("|{")
                self.__writer.writeLnbrk()
                self.__writer.indent()
                self.writeBlockSegment(segment, pre)
                self.__writer.outdent()
                self.__writer.writeLnbrk()
                self.__writer.write("}|")
                return

            else:
                raise Exception("Unhandled tag: %s" % tag)

            for seg in segment:
                self.writeSegment(seg, pre)
                
            self.__writer.write(close)

        elif isinstance(segment, Tome.TextSegment):
            content = segment.text()
            self.__writer.write(content)

        else:
            raise TypeError("Unexpected type for segment: %s" % type(segment).__name__)



    def writeFlow(self, tome):

        for title in tome.allTitles():
            self.__writer.writePre(":Title: %s" % title)
            self.__writer.writeLnbrk()
        self.__writer.writeLnbrk()

        for author in tome.authors():
            self.__writer.writePre(":Author: %s" % author)
            self.__writer.writeLnbrk()
        self.__writer.writeLnbrk()

        for name in tome.metaIter():
            for value in tome.getMeta(name):
                self.__writer.writePre(":Meta: %s %s" % (name, value))
                self.__writer.writeLnbrk()

        self.__writer.writeLnbrk()
        self.__writer.writeLnbrk()
        self.__writer.writePre("%"*self.__linewidth)



        for part in tome:
            title = part.title()
            if title is not None:
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
                self.__writer.writeLnbrk()
                self.__writer.writePre(":Part: %s" % title)
                self.__writer.writeLnbrk()
                for title in part.allTitles()[1:]:
                    self.__writer.writePre(":Title: %s" % title)
                    self.__writer.writeLnbrk()

            for book in part:
                title = book.title()
                if title is not None:
                    self.__writer.writeLnbrk()
                    self.__writer.writeLnbrk()
                    self.__writer.writeLnbrk()
                    self.__writer.writeLnbrk()
                    self.__writer.writeLnbrk()
                    self.__writer.writePre(":Book: %s" % title)
                    self.__writer.writeLnbrk()
                    for title in book.allTitles()[1:]:
                        self.__writer.writePre(":Title: %s" % title)
                        self.__writer.writeLnbrk()

                for chapter in book:
                    title = chapter.title()
                    if title is not None:
                        self.__writer.writeLnbrk()
                        self.__writer.writeLnbrk()
                        self.__writer.writeLnbrk()
                        self.__writer.writeLnbrk()
                        self.__writer.writeLnbrk()
                        self.__writer.writePre(":Chapter: %s" % title)
                        self.__writer.writeLnbrk()
                        for title in chapter.allTitles()[1:]:
                            self.__writer.writePre(":Title: %s" % title)
                            self.__writer.writeLnbrk()

                    scCount = len(chapter)
                    lastScene = scCount - 1
                    for i in xrange(scCount):
                        scene = chapter[i]

                        for child in scene:
                            self.writeSegment(child)

                        if i < lastScene:
                            self.__writer.writeLnbrk()
                            self.__writer.writeLnbrk()
                            self.__writer.writePre("***")

        self.__writer.writeLnbrk()
        self.__writer.writeLnbrk()


