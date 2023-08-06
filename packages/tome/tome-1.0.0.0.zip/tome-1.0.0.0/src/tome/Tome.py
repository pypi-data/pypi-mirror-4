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
import xml.dom
import xml.dom.minidom
import abc
import sys
import version


#These live here because they refer to the output format of the XML serialization.
FMT_VERSION_MAJOR = 1
FMT_VERSION_MINOR = 0
FMT_VERSION_PATCH = 0


class ParsingError(Exception):
    pass

class SyntaxError(Exception):
    def __init__(self, message, linenum=None, charnum=None, filename=None):
        self.__message = message
        self.__linenum = linenum
        self.__charnum = charnum
        self.__filename = filename
        super(SyntaxError, self).__init__(self.__str__())

    def __str__(self):
        prefix = ""
        on = "On"
        if self.__filename is not None:
            prefix = "In " + self.__filename
            on = " on"
        if self.__linenum is not None:
            prefix += on + " line %d" % self.__linenum
            if self.__charnum is not None:
                prefix += " col %d" % self.__charnum

        if len(prefix) > 0:
            prefix += ": "
        return prefix + str(self.__message)


class Position(object):
    def __init__(self, filename=None, linenum=None, colnum=None):
        self.__filename = filename
        self.__linenum = linenum
        self.__colnum = colnum
        if filename is None:
            self.__filename = ""
        if linenum is None:
            self.__linenum = -1
        if colnum is None:
            self.__colnum = -1

    def __str__(self):
        return "%s:%d:%d" % (self.__filename, self.__linenum, self.__colnum)

    def filename(self):
        return self.__filename

    def linenum(self):
        return self.__linenum

    def colnum(self):
        return self.__colnum

class Positioned(object):
    def __init__(self, filename=None, linenum=None, colnum=None):
        self.setPosition(filename, linenum, colnum)

    def setPosition(self, filename, linenum, colnum):
        if filename is None and linenum is None and colnum is None:
            self.__position = None
        else:
            self.__position = Position(filename, linenum, colnum)

    def parsePosition(self, node):
        if node.hasAttribute("p:p"):
            parts = node.getAttribute("p:p").strip().split(":")
            if len(parts) != 3:
                raise ParsingError("Invalid position attribute (\"p:p\").")
            filename, linenum, colnum = parts
            if len(filename) == 0:
                filename = None

            try: linenum = int(linenum)
            except ValueError:  linenum = None
            if linenum <= 0:
                linenum = None

            try: colnum = int(colnum)
            except ValueError:  colnum = None
            if colnum <= 0:
                colnum = None

            self.setPosition(filename, linenum, colnum)

        else:
            self.__position = None

    def position(self):
        return self.__position

    def filename(self):
        return self.__position.filename()

    def linenum(self):
        return self.__position.linenum()

    def colnum(self):
        return self.__position.colnum()

    def addPosAttribute(self, element):
        if self.__position is not None:
            element.setAttribute("p:p", str(self.__position))

    

class Segment(Positioned):
    def __init__(self, filename=None, linenum=None, colnum=None):
        super(Segment, self).__init__(filename, linenum, colnum)

    @abc.abstractmethod
    def isTextSegment(self):
        pass

    @abc.abstractmethod
    def serializeToNode(self, doc):
        pass

class TaggedSegment(Segment):
    def __init__(self, tag, filename=None, linenum=None, colnum=None):
        super(TaggedSegment, self).__init__(filename, linenum, colnum)
        self.__tag = tag
        self.__children = []

    def __str__(self):
        return "TaggedSegment(%s)[#%d]" % (self.__tag, len(self.__children))

    def tag(self):
        return self.__tag

    def isTextSegment(self):
        return False

    def serializeToNode(self, doc):
        ele = doc.createElement(self.__tag)
        spaceCount = 0
        last = None
        for seg in self.__children:
            isSpace = (isinstance(seg,TaggedSegment)) and (seg.tag() == "sp")
            if isSpace:
                spaceCount += 1
                if spaceCount > 1:
                    last.setAttribute("cnt", str(spaceCount))
                    continue
            else:
                spaceCount = 0

            last = seg.serializeToNode(doc)
            ele.appendChild(last)
        self.addPosAttribute(ele)
        return ele

    def __len__(self):
        return len(self.__children)

    def __getitem__(self, idx):
        return self.__children[idx]

    def __iter__(self):
        return iter(self.__children)

    def append(self, segment):
        if not isinstance(segment, Segment):
            raise TypeError("Only Segments can be appended to a Segment.")
        if isinstance(segment, TextSegment) and len(self.__children) > 0 and isinstance(self.__children[-1], TextSegment):
            segment = TextSegment(self.__children[-1].text() + segment.text())
            self.__children[-1] = segment
        else:
            self.__children.append(segment)


class TextSegment(Segment):
    def __init__(self, text, filename=None, linenum=None, colnum=None):
        super(TextSegment, self).__init__(filename, linenum, colnum)
        self.__text = text

    def __str__(self):
        return "TextSegment(%r)" % (self.__text)

    def text(self):
        return self.__text

    def isTextSegment(self):
        return True

    def serializeToNode(self, doc):
        return doc.createTextNode(self.__text)



class Scene(Positioned):
    def __init__(self, filename=None, linenum=None, colnum=None):
        super(Scene, self).__init__(filename, linenum, colnum)
        self.__paragraphs = []

    def appendParagraph(self, par):
        if not isinstance(par, TaggedSegment) or par.tag() not in ("p", "pre"):
            raise TypeError("Invalid paragraph type: expected a \"p\" TaggedSegment.")
        self.__paragraphs.append(par)

    def serializeToNode(self, doc):
        scene = doc.createElement("scene")
        for par in self.__paragraphs:
            scene.appendChild(par.serializeToNode(doc))
        self.addPosAttribute(scene)
        return scene

    def __iter__(self):
        return iter(self.__paragraphs)

    def __len__(self):
        return len(self.__paragraphs)

    def __getitem__(self, index):
        return self.__paragraphs[index]

        
class TitledDivision(Positioned):
    def __init__(self, title=None, filename=None, linenum=None, colnum=None):
        super(TitledDivision, self).__init__(filename, linenum, colnum)
        self.__titles = []
        if title is not None:
            self.__titles.append(title)
        self.__shortMark = None
        self.__children = []

    def serializeTitlesToNode(self, doc):
        titles = doc.createElement("titles")
        for title in self.__titles:
            ele = doc.createElement("title")
            ele.appendChild(doc.createTextNode(title))
            titles.appendChild(ele)
        if self.__shortMark is not None:
            titles.setAttribute("shortmark", self.__shortMark)
        return titles

    def serializeAppendContent(self, doc, parent):
        for child in self.__children:
            cnode = child.serializeToNode(doc)
            parent.appendChild(cnode)

    def serializeToNode(self, doc):
        ele = doc.createElement(self.nodeName())
        ele.appendChild(self.serializeTitlesToNode(doc))
        self.serializeAppendContent(doc, ele)
        self.addPosAttribute(ele)
        return ele

    @abc.abstractmethod
    def nodeName(self):
        """
        Returns the node name for this object in XML. E.g., "chapter", "book", "part", etc.
        """
        pass

    def title(self):
        """
        Returns the first title, or None if there are no titles.
        """
        if len(self.__titles) == 0:
            return None
        else:
            return self.__titles[0]

    def allTitles(self):
        """
        Returns a tuple of all the titles.
        """
        return tuple(self.__titles)

    def titleCount(self):
        """
        Returns the number of titles.
        """
        return len(self.__titles)

    def getTitle(self, idx):
        """
        Returns a specific title by index.
        """
        return self.__titles[idx]

    def appendTitle(self, title):
        """
        Append a title to the end of the title list.
        """
        self.__titles.append(title)


    def shortMark(self):
        """
        Returns the short mark, which is a short form of the title, typically used in page headers
        and sometimes used in tables of contents. If no short mark has been set, returns None.
        """
        return self.__shortMark

    def setShortMark(self, shortMark):
        """
        Set the short mark. See <shortMark>.
        """
        self.__shortMark = shortMark

    def append(self, child):
        """
        Adds a child to the division.
        """
        self.__children.append(child)

    def __iter__(self):
        """
        Returns an iterator over the children.
        """
        return iter(self.__children)

    def __len__(self):
        """
        Returns the number of children.
        """
        return len(self.__children)

    def __getitem__(self, index):
        """
        Gets a child at a specific index.
        """
        return self.__children[index]

class Chapter(TitledDivision):
    def append(self, scene):
        if not isinstance(scene, Scene):
            raise TypeError("Can only append scenes to a chapter.")
        super(Chapter, self).append(scene)

    def appendScene(self, scene):
        self.append(scene)

    def nodeName(self):
        return "chapter"

class Book(TitledDivision):
    def append(self, chapter):
        if not isinstance(chapter, Chapter):
            raise TypeError("Can only append chapters to a book.")
        super(Book, self).append(chapter)

    def appendChapter(self, chapter):
        self.append(chapter)

    def nodeName(self):
        return "book"

class Part(TitledDivision):
    def append(self, book):
        if not isinstance(book, Book):
            raise TypeError("Can only append books to a part.")
        super(Part, self).append(book)

    def appendBook(self, book):
        self.append(book)

    def nodeName(self):
        return "part"


class Tome(TitledDivision):
    def __init__(self):
        super(Tome, self).__init__()
        self.__authors = []
        self.__srcfileMap = {}
        self.__meta = {}

    def mapSrcFile(self, filename):
        if filename not in self.__srcfileMap:
            num = str(len(self.__srcfileMap)+1)
            self.__srcfileMap[filename] = num
            return num
        else:
            return self.__srcfileMap[filename]

    def serializeToDom(self, debug=False):
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, "tome", None)
        root = doc.documentElement

        root.setAttribute("ver", "%d.%d.%d" % (FMT_VERSION_MAJOR, FMT_VERSION_MINOR, FMT_VERSION_PATCH))
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.setAttribute("xmlns:p", "https://www.barrenmains.com/xmlns/tome/position")
        root.setAttribute("xmlns", "https://www.barrenmains.com/xmlns/tome")
        root.setAttribute("xsi:schemaLocation", "https://www.barrenmains.com/xmlns/tome tome.xsd")
        self.serializeToNode(doc, root)
        return doc

    def serializeToNode(self, doc, root=None):

        if root is None:
            root = doc.createElement("tome")

        meta = doc.createElement("meta")
        root.appendChild(meta)

        fileListEle = doc.createElement("sourceFiles")
        for filename in self.__srcfileMap:
            node = doc.createElement("src")
            node.setAttribute("key", self.__srcfileMap[filename])
            node.appendChild(doc.createTextNode(filename))
            fileListEle.appendChild(node)
        meta.appendChild(fileListEle)

        meta.appendChild(self.serializeTitlesToNode(doc))

        authors = doc.createElement("authors")
        for author in self.authors():
            ele = doc.createElement("author")
            ele.appendChild(doc.createTextNode(author))
            authors.appendChild(ele)
        meta.appendChild(authors)

        for key in self.__meta:
            for val in self.__meta[key]:
                ele = doc.createElement("userdata")
                ele.setAttribute("name", key)
                ele.appendChild(doc.createTextNode(val))
                meta.appendChild(ele)

        self.serializeAppendContent(doc, root)

        return root

    def nodeName(self):
        return "content"

    def append(self, part):
        if not isinstance(part, Part):
            raise TypeError("Can only append parts to a Tome object.")
        super(Tome, self).append(part)

    def appendPart(self, part):
        self.append(part)

    def authors(self):
        return tuple(self.__authors)

    def author(self, idx):
        return self.__authors[idx]

    def authorCount(self):
        return len(self.__authors)

    def appendAuthor(self, author):
        self.__authors.append(author)


    def appendMeta(self, name, value):
        if name not in self.__meta:
            self.__meta[name] = []
        self.__meta[name].append(value)

    def hasMeta(self, meta):
        """
        Indicates whether or not the specified meta-data key exists.
        """
        return meta in self.__meta

    def getMeta(self, meta):
        """
        Returns a tuple of all the meta values for the associated key, or an empty sequence if there is no such key.
        """
        if meta in self.__meta:
            return tuple(self.__meta[meta])
        else:
            return tuple()

    def metaIter(self):
        """
        Returns an iterator over the metadata keys.
        """
        return iter(self.__meta)


class TomeXmlParser(object):
    """
    Given a DOM document object representing a Tome document in XML, parses it into
    a Tome object. Use the <tome> method to get the populated object.
    """
    def __init__(self, doc):
        self.__tome = Tome()

        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName.lower() == "meta":
                    self.__parseMeta(node)
                elif node.tagName.lower() == "part":
                    self.__tome.appendPart(self.__parsePart(node))

    @staticmethod
    def parseStream(stream):
        doc = xml.dom.minidom.parse(stream)
        return TomeXmlParser(doc)

    def tome(self):
        return self.__tome

    def __parseMeta(self, node):
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "titles":
                    self.__parseTitles(child, self.__tome)
                elif child.tagName.lower() == "authors":
                    for author in self.__parseAuthors(child):
                        self.__tome.appendAuthor(author)
                elif child.tagName.lower() == "userdata":
                    if not child.hasAttribute("name"):
                        raise Exception("Missing required \"name\" attribute on \"userdata\" element.")
                    name = child.getAttribute("name").strip().lower()
                    value = child.firstChild.nodeValue.strip()
                    self.__tome.appendMeta(name, value)


    def __parseAuthors(self, node):
        authors = []
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "author":
                    authors.append(child.firstChild.nodeValue.strip())
        return tuple(authors)

    def __parseTitles(self, node, titled):
        if node.hasAttribute("shortmark"):
            titled.setShortMark(node.getAttribute("shortmark"))
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "title":
                    titled.appendTitle(child.firstChild.nodeValue.strip())
        
    def __parsePart(self, node):
        part = Part()
        part.parsePosition(node)
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "titles":
                    self.__parseTitles(child, part)
                elif child.tagName.lower() == "book":
                    part.appendBook(self.__parseBook(child))
        return part

    def __parseBook(self, node):
        book = Book()
        book.parsePosition(node)
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "titles":
                    self.__parseTitles(child, book)
                elif child.tagName.lower() == "chapter":
                    book.appendChapter(self.__parseChapter(child))
        return book

    def __parseChapter(self, node):
        chapter = Chapter()
        chapter.parsePosition(node)
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "titles":
                    self.__parseTitles(child, chapter)
                elif child.tagName.lower() == "scene":
                    chapter.appendScene(self.__parseScene(child))
        return chapter

    def __parseScene(self, node):
        scene = Scene()
        scene.parsePosition(node)
        for child in node.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName.lower() == "p":
                    scene.appendParagraph(self.__parseParagraph(child))
                elif child.tagName.lower() == "pre":
                    scene.appendParagraph(self.__parsePreformatted(child))
                    
        return scene

    def __parsePreformatted(self, node):
        par = TaggedSegment("pre")
        par.parsePosition(node)
        for child in node.childNodes:
            self.__appendParsedSegment(par, child)
        return par

    def __parseParagraph(self, node):
        par = TaggedSegment("p")
        par.parsePosition(node)
        for child in node.childNodes:
            self.__appendParsedSegment(par, child)
        return par

    def __appendParsedSegment(self, parent, node):
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            if node.tagName == "sp":
                cnt = 1
                if node.hasAttribute("cnt"):
                    cnt = int(node.getAttribute("cnt"))
                    try:
                        cnt = int(cnt)
                    except e:
                        raise Exception("Invalid \"cnt\" attribute on %s element: \"%s\"" % (node.tagName, cnt), e) 
                for i in xrange(cnt):
                    parent.append(TaggedSegment(node.tagName))

            else:
                seg = TaggedSegment(node.tagName)
                seg.parsePosition(node)
                for child in node.childNodes:
                    self.__appendParsedSegment(seg, child)
                parent.append(seg)

        elif node.nodeType == xml.dom.Node.TEXT_NODE:
            text = node.nodeValue
            text = text.strip()
            if len(text) != 0:
                parent.append(TextSegment(text))

        

class TomeOtlParser(object):
    """
    .. warning::
        This syntax is somewhat tentative and may not be supported in the long run.
        It is suggested that you use the `TomeFlowParser` and the tome-flow syntax instead.
    
    Given an input stream which has a Tome document described in OTL format,
    parses the document and create a new Tome object popualted witht the data.
    """

    __DEPTH_PART = 1
    __DEPTH_BOOK = 2
    __DEPTH_CHAPTER = 3
    __DEPTH_SCENE = 4
    __DEPTH_PARAGRAPH = 5

    __FORMATTING_MAP = {
        '*': 'b',
        '/': 'i',
        '_': 'u',
        '!': 'em',
    }

    __BLOCK_MAP = {
        "'": 'sq',
        '"': 'q',
        ':': 'bq',
        '~': 'n'
    }


    def __init__(self, istream, debug=False, filename="<unknown>", linenum=0, colnum=0):
        self.__debug = debug

        self.__tome = Tome()
        self.__filemap = {}
        self.__preformatted = False
        self.__stack = []

        self.parse(istream, filename, linenum, colnum)

    def _stack(self):
        return self.__stack

    def tome(self):
        return self.__tome

    def debug(self):
        return self.__debug

    def getFilenum(self, filename):
        return self.__filemap[filename]

    def getScene(self, filename, linenum, colnum):
        chapter = self.getChapter(filename, linenum, colnum)

        if len(self.__stack) < TomeOtlParser.__DEPTH_SCENE:
            ele = Scene()
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            chapter.append(ele)
            #At this point, we know that chapter exists.
            self.__stack.append(ele)

        return self.__stack[TomeOtlParser.__DEPTH_SCENE-1]
            
    def getPre(self, filename, linenum, colnum):
        #Make sure we at least have a scene.
        scene = self.getScene(filename, linenum, colnum)

        if len(self.__stack) >= TomeOtlParser.__DEPTH_PARAGRAPH and self.__stack[-1].tag() != "pre":
            raise ParsingError("Preformatted blocks must be at the top level of a scene, they cannot be included in other block elements (such as quotes or notes).")
                        
        #We either have a pre at the bottom of the stack already, or we have a scene there.
        if len(self.__stack) == TomeOtlParser.__DEPTH_SCENE:
            #Lowest element is a scene: append a new pre to it.
            ele = self.createElement("pre", filename, linenum, colnum)
            self.__stack[-1].appendParagraph(ele)
            self.__stack.append(ele)
            return ele
        else:
            #Already have a pre segment open, reuse it.
            return self.__stack[-1]
        
                


    def getLeaf(self, filename, linenum, colnum):
        """
        Returns an element to which textual content should be appended.
        """
        scene = self.getScene(filename, linenum, colnum)

        if len(self.__stack) < TomeOtlParser.__DEPTH_PARAGRAPH:
            ele = TaggedSegment("p")
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            #At this point, we know that scene exists, so if paragraph doesn't, then scene is the TOS.
            self.__stack[-1].appendParagraph(ele)
            self.__stack.append(ele)

        leaf = self.__stack[-1]
        if isinstance(leaf, TaggedSegment) and TomeOtlParser.isBlockElement(leaf.tag()):
            #Can't append directly to a block element, has to be inside a sub paragraph.
            ele = TaggedSegment("p")
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            leaf.append(ele)
            self.__stack.append(ele)
            leaf = ele

        return leaf

    def __addTitleAtDepth(self, depth, title, filename, linenum, colnum):
        if depth == 0:
            self.__tome.appendTitle(title)
        else:
            #Assumes depth is CHAPTER or less.
            self.__stack[depth-1].appendTitle(title)

    def addTitle(self, title, filename, linenum, colnum):
        depth = len(self.__stack)
        if depth < TomeOtlParser.__DEPTH_PART:
            self.__addTitleAtDepth(0, title, filename, linenum, colnum)
        elif depth == TomeOtlParser.__DEPTH_PART:
            self.getPart(filename, linenum, colnum)
            self.__addTitleAtDepth(TomeOtlParser.__DEPTH_PART, title, filename, linenum, colnum)
        elif depth == TomeOtlParser.__DEPTH_BOOK:
            self.getBook(filename, linenum, colnum)
            self.__addTitleAtDepth(TomeOtlParser.__DEPTH_BOOK, title, filename, linenum, colnum)
        elif depth == TomeOtlParser.__DEPTH_CHAPTER:
            self.getChapter(filename, linenum, colnum)
            self.__addTitleAtDepth(TomeOtlParser.__DEPTH_CHAPTER, title, filename, linenum, colnum)
        else:
            raise ParsingError("Cannot set title after content has been added.")
            
    def setShortMark(self, mark, filename, linenum, colnum):
        depth = len(self.__stack)
        if depth <= TomeOtlParser.__DEPTH_CHAPTER:
            self.__stack[-1].setShortMark(mark)
        else:
            raise ParsingError("Cannot set short-mark after content has been added.")


    ### PART ###

    def newPart(self, title, filename, linenum, colnum):
        if len(self.__stack) > TomeOtlParser.__DEPTH_CHAPTER:
            self.endScene()
        while len(self.__stack) >= TomeOtlParser.__DEPTH_PART:
            self.__stack.pop()

        node = Part(title)
        if self.__debug:
            node.setPosition(filename, linenum, colnum)
        self.__tome.appendPart(node)
        self.__stack.append(node)

    def getPart(self, filename, linenum, colnum):
        if len(self.__stack) < TomeOtlParser.__DEPTH_PART:
            ele = Part()
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            self.__tome.appendPart(ele)
            self.__stack.append(ele)

        return self.__stack[TomeOtlParser.__DEPTH_PART-1]
        

    ### BOOK ###

    def newBook(self, title, filename, linenum, colnum):
        if len(self.__stack) > TomeOtlParser.__DEPTH_CHAPTER:
            self.endScene()
        while len(self.__stack) >= TomeOtlParser.__DEPTH_BOOK:
            self.__stack.pop()

        node = Book(title)
        if self.__debug:
            node.setPosition(filename, linenum, colnum)
        self.getPart(filename, linenum, colnum).appendBook(node)
        self.__stack.append(node)

    def getBook(self, filename, linenum, colnum):
        part = self.getPart(filename, linenum, colnum)
        if len(self.__stack) < TomeOtlParser.__DEPTH_BOOK:
            ele = Book()
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            part.appendBook(ele)
            self.__stack.append(ele)

        return self.__stack[TomeOtlParser.__DEPTH_BOOK-1]
        

    ### CHAPTER ###

    def newChapter(self, title, filename, linenum, colnum):
        if len(self.__stack) > TomeOtlParser.__DEPTH_CHAPTER:
            self.endScene()
        while len(self.__stack) >= TomeOtlParser.__DEPTH_CHAPTER:
            self.__stack.pop()

        node = Chapter(title)
        if self.__debug:
            node.setPosition(filename, linenum, colnum)
        self.getBook(filename, linenum, colnum).appendChapter(node)
        self.__stack.append(node)

    def getChapter(self, filename, linenum, colnum):
        book = self.getBook(filename, linenum, colnum)
        if len(self.__stack) < TomeOtlParser.__DEPTH_CHAPTER:
            ele = Chapter()
            if self.__debug:
                ele.setPosition(filename, linenum, colnum)
            book.appendChapter(ele)
            self.__stack.append(ele)

        return self.__stack[TomeOtlParser.__DEPTH_CHAPTER-1]
        

    @staticmethod
    def isBlockElement(tagName):
        return tagName in TomeOtlParser.__BLOCK_MAP.values()

    def endScene(self):
        depth = len(self.__stack)
        if depth < TomeOtlParser.__DEPTH_SCENE:
            raise ParsingError("Invalid scene divider when no scene is open.")
        elif depth > TomeOtlParser.__DEPTH_PARAGRAPH:
            error = "Tags are still open at end of scene: " 
            if self.__debug:
                error += (", ".join("%s@%s" % (seg.tag(), seg.position())
                    for seg in self.__stack[TomeOtlParser.__DEPTH_SCENE:]))
            else:
                error += ", ".join(seg.tagName for seg in self.__stack[TomeOtlParser.__DEPTH_SCENE:])
            raise ParsingError(error)
        else:
            #Pop off the paragraph if there is one, and then the scene itself.
            while len(self.__stack) >= TomeOtlParser.__DEPTH_SCENE:
                self.__stack.pop()


    def endPar(self):
        if len(self.__stack) < TomeOtlParser.__DEPTH_PARAGRAPH:
            #Just a blank line or something before we opened a paragraph. Ignore it.
            pass
        else:
            #Since we're at or below the paragraph, this must be a TaggedSegment.
            leaf = self.__stack[-1]
            tag = leaf.tag()
            if TomeOtlParser.isBlockElement(tag):
                #This means we've just popped the subpar off this block element and we have another
                # blank line before we reached more content. No big deal, just ignore it.
                pass
            elif tag != "p":
                raise ParsingError("Formatting tag still open at end of paragraph.")
            else:
                #Pop the paragraph.
                self.__stack.pop()


    def appendText(self, text, filename, linenum, colnum):
        leaf = self.getLeaf(filename, linenum, colnum)
        head = False
        tail = False
        if len(text) > 0:
            if text[0].isspace():
                head = True
            if len(text) > 1 and text[-1].isspace():
                tail = True
        if head:
            leaf.append(self.createElement("sp", filename, linenum, colnum))
        leaf.append(TextSegment(text, filename, linenum, colnum))
        if tail:
            leaf.append(self.createElement("sp", filename, linenum, colnum))


    def createElement(self, tag, filename, linenum, colnum):
        node = TaggedSegment(tag)
        if self.__debug:
            node.setPosition(filename, linenum, colnum)
        return node

    def appendLeaf(self, tag, filename, linenum, colnum):
        node = self.createElement(tag, filename, linenum, colnum)
        self.getLeaf(filename, linenum, colnum).append(node)
        self.__stack.append(node)

    def endLeaf(self):
        if len(self.__stack) >= TomeOtlParser.__DEPTH_PARAGRAPH and self.__stack[-1].tag() == "pre":
            #Pop the pre off the stack.
            return self.__stack.pop().tag()
        elif len(self.__stack) <= TomeOtlParser.__DEPTH_PARAGRAPH:
            raise ParsingError("Unmatched closing tag.")
        else:
            #Pop the leaf off the stack.
            ele = self.__stack.pop()

            #If it's a paragraph this low on the stack, it should be because it's under a block element, which
            # is the thing that's really being closed.
            if ele.tag() == "p":
                if len(self.__stack) <= TomeOtlParser.__DEPTH_PARAGRAPH:
                    raise ParsingError("Internal Error: sub-paragraph closed with no parent block element.")
                ele = self.__stack.pop()
            return ele.tag()
            

    def parse(self, stream, filename="<unknown>", linenum=0, colnum=0):
        if self.__debug:
            filename = self.__tome.mapSrcFile(filename)
        try:
            #The rule for colnum is that is always points to the character to be processed.
            #Once you're done processing the current character, you can increment it.
            #If an error occurs, it always occurs at the specified colnum.

            for line in stream:
                linenum += 1

                #Remove trailing whitespace, it's never needed.
                line = line.rstrip()
                colnum = 0
                linelen = len(line)

                #Consume leading whitespace: it's not needed either, but it effects the colnum.
                while colnum < linelen and line[colnum].isspace():
                    colnum += 1

                #If previous lines were preformatted and no longer are, then close that leaf.
                if self.__preformatted and (colnum >= linelen or line[colnum] != ';'):
                    self.endLeaf()
                    self.__preformatted = False
                
                #Blank lines.
                if colnum == linelen:
                    self.endPar()
                    continue

                #Process ordinary text...
                if line[colnum] == ':':
                    colnum += 1

                    #Consume leading whitespace
                    while colnum < linelen and line[colnum].isspace():
                        colnum += 1

                    if colnum == linelen:
                        #Blank (or all white) line of ordinary text is a paragraph break
                        self.endPar()

                    else:
                        #Parse ordinary text and add to current par.
                        text = ""
                        while colnum < linelen:
                            c = line[colnum]
                            if c == '{':
                                colnum += 1
                                if colnum == linelen:
                                    raise ParsingError("Invalid opening brace at end of line.")
                                c = line[colnum]

                                if c in TomeOtlParser.__FORMATTING_MAP:
                                    if len(text) > 0:
                                        self.appendText(text, filename, linenum, colnum)
                                        text = ""
                                    self.appendLeaf(TomeOtlParser.__FORMATTING_MAP[c], filename, linenum, colnum)
                                    colnum += 1

                                    #Consume white space between command and content.
                                    while colnum < linelen and line[colnum].isspace():
                                        colnum += 1


                                elif c in TomeOtlParser.__BLOCK_MAP:
                                    if len(text) > 0:
                                        self.appendText(text, filename, linenum, colnum)
                                        text = ""
                                    self.appendLeaf(TomeOtlParser.__BLOCK_MAP[c], filename, linenum, colnum)
                                    colnum += 1

                                    #Consume white space between command and content.
                                    while colnum < linelen and line[colnum].isspace():
                                        colnum += 1

                                elif c == '{':
                                    #Escaped open brace.
                                    text += '{'
                                    colnum += 1

                                elif c == '}':
                                    #Escaped closing brace.
                                    text += '}'
                                    colnum +=1

                                else:
                                    raise ParsingError("Unknown command.")
                                
                            elif c == '}':
                                #Close tag.
                                colnum += 1
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                self.endLeaf()

                            elif c == '*' and linelen == colnum+3 and line[colnum+1] == '*' and line[colnum+2] == '*':
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                self.endScene()
                                colnum += 3

                            elif c == '.' and linelen >= colnum+3 and line[colnum+1] == '.' and line[colnum+2] == '.':
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                self.getLeaf(filename, linenum, colnum).append(self.createElement("ellips", filename, linenum, colnum))
                                colnum += 3

                            elif c == '-' and linelen >= colnum+2 and line[colnum+1] == '-':
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                if line[colnum+2] == '-':
                                    tag = "md"
                                    colnum += 3
                                else:
                                    tag = "nd"
                                    colnum += 2
                                self.getLeaf(filename, linenum, colnum).append(self.createElement(tag, filename, linenum, colnum))

                            else:
                                #Plain text
                                text += line[colnum]
                                colnum += 1
                            
                        if len(text) > 0:
                            #End of line.
                            self.appendText(text + " ", filename, linenum, colnum)

                elif line[colnum] == '-':
                    #One liners
                    colnum += 1
                    split = line[colnum:].split(':', 1)
                    if len(split) != 2:
                        raise ParsingError("Invalid one-liner, missing colon.")

                    command, value = split
                    command = command.strip().lower()
                    value = value.strip()
                    
                    if command == "title":
                        self.addTitle(value, filename, linenum, colnum)

                    elif command == "shortmark":
                        self.setShortMark(value, filename, linenum, colnum)

                    elif command == "author":
                        self.__tome.appendAuthor(value)

                    elif command == "chapter":
                        self.newChapter(value, filename, linenum, colnum)

                    elif command == "book":
                        self.newBook(value, filename, linenum, colnum)

                    elif command == "part":
                        self.newPart(value, filename, linenum, colnum)

                    else:
                        raise ParsingError("Unknown one-liner: \"%s\"" % (command))

                elif line[colnum] == '#':
                    #Arbitrary meta data.
                    colnum += 1
                    split = line[colnum:].split(':', 1)
                    if len(split) != 2:
                        raise ParsingError("Invalid meta-data, missing colon.")

                    command, value = split
                    command = command.strip().lower()
                    value = value.strip()

                    self.__tome.appendMeta(command, value)

                elif line[colnum] == '>':
                    #Unprocessed (but formatted) text.
                    colnum += 1
                    #Consume leading whitespace
                    while colnum < linelen and line[colnum].isspace():
                        colnum += 1
                    self.appendText(line[colnum:] + " ", filename, linenum, colnum)


                elif line[colnum] == ';':
                    #Preformatted text.
                    colnum += 1
                    if not self.__preformatted:
                        self.endPar()
                    self.__preformatted = True

                    #Make sure there's a pre element to append to.
                    pre = self.getPre(filename, linenum, colnum)

                    #Append the text to it.

                    #Handle leading whitespace properly.
                    while colnum < linelen and line[colnum].isspace():
                        colnum += 1
                        pre.append(self.createElement("sp", filename, linenum, colnum))

                    #Append the remaining text.
                    text = TextSegment(line[colnum:])
                    if self.__debug:
                        text.setPosition(filename, linenum, colnum)
                    pre.append(text)

                    #And append a linebreak.
                    br = self.createElement("lnbrk", filename, linenum, colnum)
                    pre.append(br)

                elif line[colnum] == '%':
                    #Comment.
                    pass

                else:
                    raise ParsingError("Unknown line type: \"%s\"" % (line[colnum]))


        except ParsingError, e:
            raise SyntaxError(e, linenum, colnum)


class TomeFlowParser(TomeOtlParser):

    __FORMATTING_MAP = {
        '*': 'b',
        '/': 'i',
        '_': 'u',
        '!': 'em',
    }

    __BLOCK_MAP = {
        "'": 'sq',
        '"': 'q',
        '|': 'bq',
        '^': 'n'
    }

    def parse(self, stream, filename="<unknown>", linenum=0, colnum=0):
        if self.debug():
            filename = self.tome().mapSrcFile(filename)
        try:
            #The rule for colnum is that is always points to the character to be processed.
            #Once you're done processing the current character, you can increment it.
            #If an error occurs, it always occurs at the specified colnum.

            preformatted = False
            for line in stream:
                linenum += 1

                #Remove trailing whitespace
                line = line.rstrip()
                colnum = 0
                linelen = len(line)

                #Consume leading whitespace: it's not needed either, but it effects the colnum.
                while colnum < linelen and line[colnum].isspace():
                    colnum += 1

                #If previous lines were preformatted and no longer are, then close that leaf.
                if preformatted and (colnum >= linelen or line[colnum] != '='):
                    self.endLeaf()
                    preformatted = False
                
                #Blank lines.
                if colnum == linelen:
                    self.endPar()
                    continue

                #Commands
                if line[colnum] == ':':
                    colnum += 1

                    split = line[colnum:].split(None, 1)
                    if len(split) != 2:
                        split = [split[0], ""]

                    command, value = split
                    command = command.strip(':').lower()
                    value = value.strip()
                    
                    if command == "title":
                        self.addTitle(value, filename, linenum, colnum)

                    elif command == "shortmark":
                        self.setShortMark(value, filename, linenum, colnum)

                    elif command == "author":
                        self.tome().appendAuthor(value)

                    elif command == "chapter":
                        self.newChapter(value, filename, linenum, colnum)

                    elif command == "book":
                        self.newBook(value, filename, linenum, colnum)

                    elif command == "part":
                        self.newPart(value, filename, linenum, colnum)

                    elif command == "meta":
                        split = value.split(None, 1)
                        if len(split) != 2:
                            raise ParsingError("Invalid meta: missing value.")
                        name, value = split
                        name = name.strip().lower()
                        value = value.strip()
                        self.tome().appendMeta(name, value)

                    else:
                        raise ParsingError("Unknown command: \"%s\"" % (command))

                elif line[colnum] == '>':
                    #Unprocessed (but formatted) text.
                    colnum += 1
                    #Consume leading whitespace
                    while colnum < linelen and line[colnum].isspace():
                        colnum += 1
                    self.appendText(line[colnum:] + " ", filename, linenum, colnum)


                elif line[colnum] == '=':
                    #Preformatted text.
                    colnum += 1
                    if not preformatted:
                        self.endPar()
                    preformatted = True

                    #Make sure there's a pre element to append to.
                    pre = self.getPre(filename, linenum, colnum)

                    #Append the text to it.

                    #Handle leading whitespace properly.
                    while colnum < linelen and line[colnum].isspace():
                        colnum += 1
                        pre.append(self.createElement("sp", filename, linenum, colnum))

                    #Append the remaining text.
                    text = TextSegment(line[colnum:])
                    if self.debug():
                        text.setPosition(filename, linenum, colnum)
                    pre.append(text)

                    #And append a linebreak.
                    br = self.createElement("lnbrk", filename, linenum, colnum)
                    pre.append(br)

                elif line[colnum] == '%':
                    #Comment.
                    pass

                #Process ordinary text...
                else:
                    #Parse ordinary text and add to current paragraph.
                    text = ""
                    prev = None
                    while colnum < linelen:
                        c = line[colnum]

                        #Markup
                        if c == '{':
                            colnum += 1

                            #The previous character will tell us what command this is.

                            if prev in TomeFlowParser.__FORMATTING_MAP:
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                self.appendLeaf(TomeFlowParser.__FORMATTING_MAP[prev], filename, linenum, colnum)
                                prev = None

                                #Consume white space between command and content.
                                while colnum < linelen and line[colnum].isspace():
                                    colnum += 1


                            elif prev in TomeFlowParser.__BLOCK_MAP:
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                self.appendLeaf(TomeFlowParser.__BLOCK_MAP[prev], filename, linenum, colnum)
                                prev = None

                                #Consume white space between command and content.
                                while colnum < linelen and line[colnum].isspace():
                                    colnum += 1

                            elif prev == '~':
                                #Escaped open brace.
                                text += '{'
                                colnum += 1
                                prev = None

                            elif prev is None or prev.isspace():
                                #Non command curly brace.
                                if prev is not None:
                                    text += prev
                                    prev = None
                                text += '{'
                                colnum += 1

                            else:
                                raise ParsingError("Unknown command: %s" % prev)

                        #Scene sep
                        elif c == '*' and linelen == colnum+2 and line[colnum+1] == '*' and prev == '*':
                            if len(text) > 0:
                                self.appendText(text, filename, linenum, colnum)
                                text = ""
                            self.endScene()
                            colnum += 2
                            prev = None

                        #Ellipsis
                        elif c == '.' and linelen >= colnum+2 and line[colnum+1] == '.' and prev == '.':
                            if len(text) > 0:
                                self.appendText(text, filename, linenum, colnum)
                                text = ""
                            self.getLeaf(filename, linenum, colnum).append(self.createElement("ellips", filename, linenum, colnum))
                            colnum += 2
                            prev = None

                        #M or Ndash.
                        elif c == '-' and prev == '-':
                            if len(text) > 0:
                                self.appendText(text, filename, linenum, colnum)
                                text = ""
                            if colnum+1 < linelen and line[colnum+1] == '-':
                                tag = "md"
                                colnum += 2
                            else:
                                tag = "nd"
                                colnum += 1
                            self.getLeaf(filename, linenum, colnum).append(self.createElement(tag, filename, linenum, colnum))
                            prev = None

                            
                        else:
                            #Nothing else needs the prev character, so it was just text
                            if prev is not None:
                                text += prev
                                prev = None

                            if c == '}':
                                #Close tag.
                                colnum += 1
                                if len(text) > 0:
                                    self.appendText(text, filename, linenum, colnum)
                                    text = ""
                                tag = self.endLeaf()
                                
                                #Check closing character.
                                if colnum < linelen:
                                    end = line[colnum]
                                    if not end.isspace():
                                        if (end in TomeFlowParser.__FORMATTING_MAP):
                                            expectedTag = TomeFlowParser.__FORMATTING_MAP[end]
                                        elif (end in TomeFlowParser.__BLOCK_MAP):
                                            expectedTag = TomeFlowParser.__BLOCK_MAP[end]
                                        else:
                                            expectedTag = None

                                        if tag != expectedTag:
                                            raise ParsingError("Unexpected closing character '%s': open tag is '%s'" % (end, tag))
                                        else:
                                            colnum += 1

                            else:
                                #Plain text
                                if prev is not None:
                                    text += prev
                                prev = c
                                colnum += 1
                        
                    if prev is not None:
                        text += prev
                    if len(text) > 0:
                        #End of line.
                        self.appendText(text + " ", filename, linenum, colnum)


        except ParsingError, e:
            raise SyntaxError(e, linenum, colnum)

