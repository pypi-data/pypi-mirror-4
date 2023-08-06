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
"""

.. module:: writeEpub
    :platform: Unix, Windows
    :synopsis: Generate EPUB format from Tome object.

.. moduleauthor:: Brian Mearns <bmearns@ieee.org>

The `writeEpub` module provides utilities for outputting a |Tome| object to EPUB format, which is a commonly
used open standard e-book format.

For more information on the EPUB format, see the `EPUB page from the IDPF <http://idpf.org/epub>`_.

Description
===========

Overview
--------
    
An `EpubWriter` encapsulates a |Tome| object and options for generating the EPUB output.
The EPUB is generated from a template directory, in addition to the content of the |Tome|.

.. _template_dir:

An EPUB document is actually a zip arhive containing multiple compressed files. The `EpubWriter` will
generate a directory with all of the appropriate files, and then pack the directory into an archive.
The user controls what files are placed in the EPUB archive by specifying a :dfn:`template directory`
which contains the files they want to include. Files in the template directory are of two types:
*template files*, and *verbatim files*.

:dfn:`Verbatim files` can be any type of file and these are simply copied directly from the template directory
into the EPUB archive without modification to the content of the file name.

:dfn:`Template files` are files in the template directory which will be processed through the |templ|
processor [#templ]_. Template files can contain any arbitrary content you want to include in the EPUB,
as well as |templ| code in order to dynamically generate content based on your |Tome|. Before processing the
template files, the |templ| stack will be preloaded with symbols which you can use in your template file in
order to access content from the |Tome| object.

In addition to verbatim and template files, the `EpubWriter` also needs a *chapter template* file. The
:dfn:`chapter template` is another |templ| file which will be used as the basis for generating the EPUB content
for each chapter of the |Tome|. Each chapter is written to it's own file, using the chapter template as input,
and chapter-specific information and content from the |Tome| object pre-loaded into the |templ| stack.


.. _path_filters:

Path Filters
------------

Path filters are used to specify which files in the :ref:`template directory <template_dir>` are to be included
in the EPUB. A :dfn:`file filter` is simply a `callable` object which should accept a relative filesystem path
(as a `str`) and return a boolean value: `True` to include the path in the EPUB, `False` to exclude it.
The paths which are passed to the filter will be relative to the specified template directory.

If you want to include all of the files and subdirectories that in the template directory, you don't need to specify
a path filter. However, the EPUB specification requires that every file contained in the EPUB document is accounted
for with an entry in the manifest. This can lead to problems if there are hidden or unexpected files in your
template directory. For instance, if you are using a version control system for your template directory, it may store
its own files in there. Some file editors will also store temporary or swap files if you happen to be editing
one of the template files when you generate the EPUB, and a number of different programs produce backup files
before they change a file. If any of these things are included in the EPUB but not in your manifest, you may have
problems.

The :meth:`EpubWriter.getListBasedFilter` static method is a simple way to create a fairly powerful filter
based on a *whitelist* and a *blacklist* of path patterns, where path patterns are used as with the
`fnmatch` module. Use this function to get a path filter, and then
pass the path filter to the `EpubWriter` constructor, as shown below::

    filter = EpubWriter.getListBasedFilter(exc_patterns=["*.swp"])
    EpubWriter(tome, "epub-template", "mybook.epub", filter)

This example will include any files that do not end in :file:`.swp`.



Notes
-----

.. [#templ] 
    |templ| is a simple programming language used for writing template files. The template file
    contains the desired content as well as inline code. The |templ| processor then processes the
    template file in order to generate an output file.


API
===

"""

import os
import os.path
import fnmatch
import shutil
import Tome
import time
import datetime
import zipfile
import cStringIO
import templ.templ
import templ.texec
import templ.ttypes
import templ.tstreams
import templ.texceptions
import tomeTempl
import sys
import errno
import pkg_resources


def htmlEscape(text):
    """
    Escapes a string for output as HTML.

    Substitutes certain reserved characters in HTML with appropriate HTML character entities, so that the text
    can unambiguously be included as text in HTML content.

    The characters that are replaced are ``&``, ``'``, ``<``, and ``>``.

    .. warning::

        Do not escape a string which has already been escaped; all character references begin with a ``&`` character,
        which itself will be incorrectly escaped by a second call to this function.

    :param str text: The text to escape

    :returns:   The escaped text.
    :rtype: str
    """
    return text.replace("&", "&amp;").replace("'", "&#8217;").replace("<", "&lt;").replace(">", "&gt;")

@templ.texec.function
class xHtmlEscape(templ.texec.TFunction):
    """
    {html-esc TEXT}

    Returns a string which is the given text, escaped for use in an HTML document.
    """
    __mnemonics__ = ("html-esc",)
    def execute(self, name, args, ostream, stack):
        self.checkArgCount(name, args, exact=[1,])
        xstr = self.checkArgType(name, 0, args, templ.ttypes.String).str
        return templ.ttypes.String(htmlEscape(xstr))


class EpubWriter(object):
    """
    This is the main functional class of this module, used for producing an EPUB document from a
    |Tome| object and the files in the specified :ref:`template directory <template_dir>`.
    """
    def __init__(
        self, tome, ofile, templateDirectory=None,
        tdFilter=None, tmplFilter=None, chapterTemplatePath=None,
        uid=None, lang=None,
        bookTitleTemplatePath=None, partTitleTemplatePath=None,
        frontPage=None, backPage=None
    ):
        """
        :param tome: The Tome object for which to generate an EPUB document.
        :type tome: |Tome|

        :param str ofile:
            The filesystem path to the output EPUB file to be generated.

        :param str templateDirectory:
            The filesystem path to the templateDirectory (for an overview of
            the template directory, see :ref:`here <template_dir>`).

        :param tdFilter:
            A callable object which is used to decide whether or not a path in the `templateDirectory`
            should be included in the EPUB. If not given or `None`, then no filtering is performed, all
            files and subdirectories found in the given template directory will be included in the EPUB.
            See :ref:`Path Filters <path_filters>` for details.
        :type tdFilter: :ref:`path filter <path_filters>`

        :param tmplFilter:
            A path filter to determine which of the src files are *template files*. All the rest are
            *verbatim files*. See :ref:`template directory <template_dir>` for details. If not given, or `None`,
            then a default filter is used which will match any paths that end in ".templ" or ".tmpl".
        :type tmplFilter: :ref:`path filter <path_filters>`

        :param str chapterTemplatePath:
            The filesystem path to the |templ| template file which will be used for generating each of the chapter
            files. This path will automatically be excluded from the source files if it's in the template directory.
            If not given or `None`, the default filename :file:`chapter.xhtml.tmpl` will be appended to
            the path of the template directory and used. 

        :param str uid:
            A unique identifier for the book, which will be used for the 
            `dc:identifier <http://idpf.org/epub/30/spec/epub30-publications.html#elemdef-opf-dcidentifier>`_
            element of the EPUB document. If this is not given or is `None`, we will attempt to get it
            from the "uid" :meth:`meta item <Tome.Tome.getMeta>` in the |Tome|. If no such meta item is
            found, an Exception is raised.

        :param str lang:
            A string specifying the language of the work, which will be used for the 
            `dc:language <http://idpf.org/epub/30/spec/epub30-publications.html#elemdef-opf-dclanguage>`_
            element of the EPUB document. The value must conform to :rfc:`5646` (e.g., "en-US").
            If this is not given or is `None`, we will attempt to get it
            from the "lang" :meth:`meta item <Tome.Tome.getMeta>` in the |Tome|. If no such meta item is
            found, an Exception is raised.

        :param str bookTitleTemplatePath:
            Simmilar to `chapterTemplatePath`, but for the title page at the start of explicit books sections

        :param str partTitleTemplatePath:
            Simmilar to `chapterTemplatePath`, but for the title page at the start of explicit part sections.

        :param str frontPage:
            A string giving the EPUB-relative path of the page the immediately precedes the generated content
            pages, or None.

        :param str backPage:
            A string giving the EPUB-relative path of the page the immediately follows the generated content
            pages, or None.
        """
        self.__tome = tome
        self.__ofile = ofile

        self.__frontPage = frontPage
        self.__backPage = backPage

        if templateDirectory is None:
            templateDirectory = pkg_resources.resource_filename("tome", "res/epub-template")
        self.__templateDir = templateDirectory

        if tdFilter is None:
            self.__tdFilter = lambda path: True
        else:
            self.__tdFilter = tdFilter

        if tmplFilter is None:
            self.__tmplFilter = EpubWriter.getListBasedFilter(inc_patterns=["*.tmpl", "*.templ"])
        else:
            self.__tmplFilter = tmplFilter

        if chapterTemplatePath is None:
            self.__chapterTemplatePath = os.path.join(templateDirectory, "chapter.xhtml.tmpl")
        else:
            self.__chapterTemplatePath = chapterTemplatePath
            
        if bookTitleTemplatePath is None:
            self.__bookTitleTemplatePath = os.path.join(templateDirectory, "bookTitle.xhtml.tmpl")
        else:
            self.__bookTitleTemplatePath = bookTitleTemplatePath
            
        if partTitleTemplatePath is None:
            self.__partTitleTemplatePath = os.path.join(templateDirectory, "partTitle.xhtml.tmpl")
        else:
            self.__partTitleTemplatePath = partTitleTemplatePath
            

        if uid is not None:
            self.__uid = uid
        else:
            self.__uid = tome.getMeta("uid")
            if len(self.__uid) == 0:
                raise Exception("No UID specified.")
            elif len(self.__uid) > 1:
                raise Exception("Invalid UID: Only one UID allowed.")
            else:
                self.__uid = self.__uid[0]

        if lang is not None:
            self.__lang = lang
        else:
            self.__lang = tome.getMeta("lang")
            if len(self.__lang) == 0:
                raise Exception("No Lang specified.")
            elif len(self.__lang) > 1:
                raise Exception("Invalid Lang: Only one Lang allowed.")
            else:
                self.__lang = self.__lang[0]


        #List of notes, grouped by chapter.
        self.__enList = []

        #List of XML encoded short-marks for each chapter
        self.__chHtmlShortMarks = []

        #Current positions and things...
        self.__prtNum = 0
        self.__bkNum = 0
        self.__chNum = 0

        self.__tocHtmlStr = ""
        self.__ncxXmlStr = ""
        self.__navXmlStr = ""
        self.__manfXmlStr = ""
        self.__spneXmlStr = ""


    def __chUid(self, num):
        """
        Formats a numerical chapter number into a string suitable for use as a chUid.
        """
        return "%04d" % num

    def writeBlockSegment(self, ostream, begin, end, segment, dropCap=False, prefix="", suffix=""):
        """
        Writes a block-style segment and all of it's children to the given output stream.

        Block segments are things like :file:`q` and :file:`n` segments which contain
        paragraph child segments (as opposed to inline segments like
        :file:`b` and :file:`i` which cannot).

        :param ostream:
            The output stream to which the segment will be written.
        :type ostream:  `file`
        :param str begin:
            A string to prepend to the beginning of the segment, i.e., the opening tag.
        :param str end:
            A string to append to the end of the segment, i.e., the closing tag.
        :param segment:
            The block segment to write.
        :type segment: :class:`Tome.TaggedSegment`
        :param boolean dropCap:
            Whether or not to generate a drop-cap for the first character. This is typically only
            used for the first segment of a chapter.
        :param str prefix:
            A string that will be output at the start of each paragraph in the block segment, *except for
            the first paragraph*. For instance, this is useful for quotes (:file:`q` tags) where an opening
            quotation mark is typically placed in front of each paragraph.
        :param str suffix:
            A string that will be output at the end of *ever* paragraph child in the block segment. Not sure
            if this is ever actually useful.
        """
        ostream.write(begin)
        notFirst = False
        multiple = len(segment) > 1
        parCount = len(segment)
        for parNum in xrange(parCount):
            par = segment[parNum]
            #There could be some empty text nodes that show up here, depending on how it's parsed.
            if isinstance(par, Tome.TextSegment) and len(par.text().strip()) == 0:
                continue
            if not isinstance(par, Tome.TaggedSegment) or par.tag() != "p":
                raise Exception("Block node may only contain \"p\" elements: found \"%s\"" % par.tag())

            #Don't actually put a par-break in front of the first paragraph in a block element (like a quoted string).
            if notFirst:
                ostream.write("\n<p>" + prefix)
            notFirst = True

            for cseg in par:
                self.writeSegment(ostream, cseg, dropCap)
                dropCap = False

            ostream.write(suffix)
            if multiple and parNum != (parCount-1):
                ostream.write("\n</p>\n")

        ostream.write(end)

    def writeSegment(self, ostream, segment, dropCap=False):
        """
        Writes a segment (and all of it's children) to the given output stream.

        This handles both inline and block segments, although block segments are
        mostly delegated to :meth:`writeBlockSegment`.
        """
        if isinstance(segment, Tome.TaggedSegment):
            tag = segment.tag()

            ### Formatting segments.
            if tag == "b":
                ostream.write("<b>")
                close = "</b>"
            elif tag == "i":
                ostream.write("<i>")
                close = "</i>"
            elif tag == "em":
                ostream.write("<em>")
                close = "</em>"
            elif tag == "u":
                ostream.write("<u>")
                close = "</u>"

            ### Text Objects.
            elif tag == "ellips":
                ostream.write("&#x2026;")
                return
            elif tag == "md":
                ostream.write("&#8212;")
                return
            elif tag == "nd":
                ostream.write("&#8211;")
                return
            elif tag == "sp":
                ostream.write(" ")
                return
            elif tag == "lnbrk":
                ostream.write("\n")
                return

            ### Block Objects.
            elif tag == "q":
                return self.writeBlockSegment(ostream, "&#8220;", "&#8221;", segment, dropCap, prefix="&#8220;")
            elif tag == "sq":
                return self.writeBlockSegment(ostream, "&#8216;", "&#8217;", segment, dropCap, prefix="&#8216;")
            elif tag == "bq":
                return self.writeBlockSegment(ostream, "\n</p>\n<blockquote>\n<p>", "\n</p>\n</blockquote>\n<p>\n", segment, dropCap)

            ### End notes
            elif tag == "n":
                chEndNotes = self.__enList[self.__chNum-1]
                enIdx = len(chEndNotes)
                chEndNotes.append(None)
                enNum = str(enIdx+1)
                chNum = str(self.__chNum)

                #Add a reference for the endnote to the content.
                ostream.write("<a class='noteref' rel='footnote' id='ch{chNum}N{enNum}Ref' href='{path}#ch{chNum}N{enNum}'>{enNum}</a>".format(
                    path = self.chapterFileName(self.__chNum),
                    chNum = chNum,
                    enNum = enNum
                ))

                #Now generate the content for the footnote.
                enStream = cStringIO.StringIO()
                self.writeBlockSegment(enStream, "<p>", "</p>", segment)
                chEndNotes[enIdx] = enStream.getvalue()
                enStream.close()

                return

            else:
                raise Exception("Unhandled tag: %s" % tag)

            for cseg in segment:
                self.writeSegment(ostream, cseg, dropCap)
                dropCap = False
                
            ostream.write(close)

        elif isinstance(segment, Tome.TextSegment):
            #Plain text
            content = segment.text()
            if dropCap and len(content) > 0:
                content = "<span class='dropcap'>%s</span>%s" % (htmlEscape(content[0]), htmlEscape(content[1:]))
            else:
                content = htmlEscape(content)
            ostream.write(content)
            return

        else:
            raise TypeError("Unexpected type for segment.")

    @staticmethod
    def listBasedFilter(path, inc_patterns=None, exc_patterns=None, excludeFirst=True):
        """
        A helper function which can be included in :ref:`path filters <path_filters>` in order to filter
        paths based on a whitelist and a blacklist of file patterns.

        The given path is added to the whitelist and/or the blacklist by comparing it to the two sets of
        patterns, which are tested using `fnmatch`. If the path matches any of the patterns in `inc_patterns`, then it
        is whitelisted. if it matches any patterns in `exc_patterns`, then it is blacklisted.

        There are two ways to handles files which end up in both lists. The first is the default, called :dfn:`excludeFirst`.
        In *excludeFirst* mode, any path that is blacklisted is immediately rejected (the function returns `False`). If a path
        makes it past the blacklist, it is only kept if it is in the whitelist, otherwise it is rejected. In other words,
        the path is kept if and only if it is *in* the whitelist *and not in* the blacklist.

        The second mode is :dfn:`includeFirst`, in which case any path which is whitelisted is kept, regardless of whether or not
        it is blacklisted. If a path is *not* in the whitelist, then it is still kept *unless* it is in the blacklist. In other
        words, the path is kept if it is in the whitelist *or* it is *not in* the blacklist (alternatively, it is rejected if and only
        if it is *in* the blacklist *and not in* the whitelist).

        The two pattern sets have default values which are used if they are unspecified or are `None`. The default values are intended
        to be unobstructive. For the `exc_patterns`, the default in all cases is any empty set of patterns, so no paths will end up on
        the black list. For the `inc_patterns`, the default depends on the handling mode: for *excludeFirst* mode, the default is
        a single ``*`` pattern which matches all paths so that any files which are not blacklisted will be pass; in *includeFirst*
        mode, the default is an empty set of patterns so that no paths will match and files will only make it through if they aren't
        blacklisted.

        .. seealso::
            
            :meth:`getListBasedFilter`
                A function which returns an actual :ref:`path filter <path_filters>` object based on this function.

        :param inc_patterns:
            The list of path patterns to match against for the whitelist. A path is whitelisted if it matches
            any of the given patterns.
        :type inc_patterns: List of str

        :param exc_patterns:
            The list of path patterns to match against for the blacklist. A path is blacklisted if it matches
            any of the given patterns.
        :type exc_patterns: List of str

        :param boolean excludeFirst:
            Specifies how to handle paths that end up on both the whitelist and the blacklist. See description above for more details.
            The default is `True`, putting the filter in *excludeFirst* mode. A value of `False` puts the filter in *includeFirst*
            mode.

        :returns:
            Returns `True` if the given path passed the filter, `False` if it was rejected by the filter.
        :rtype: boolean

        """
        if inc_patterns is None:
            if excludeFirst:
                inc_patterns = ["*"]
            else:
                inc_patterns = []
        if exc_patterns is None:
            exc_patterns = []
                
        whiteListed = any(fnmatch.fnmatch(path, pattern) for pattern in inc_patterns)
        blackListed = any(fnmatch.fnmatch(path, pattern) for pattern in exc_patterns)
        if excludeFirst:
            #If it's black listed, get rid of it.
            #Otherwise, only take it if it's white listed.
            return (not blackListed) and whiteListed
        else:
            #If it's white listed, definitely keep it.
            #Otherwise, keep it unless it's been black listed.
            return (whiteListed) or (not blackListed)

    @staticmethod
    def getListBasedFilter(inc_patterns=["*",], exc_patterns=[".*",], excludeFirst=True):
        """
        Returns a :ref:`path filter <path_filters>` object based on whitelisting and blacklisting
        paths using `fnmatch` path patterns.
        """
        return lambda path : EpubWriter.listBasedFilter(path, inc_patterns, exc_patterns, excludeFirst)
        

    @staticmethod
    def findSrcFiles(templateDir, path_filter=None):
        """
        Scans recursively through the given directory and finds the relative paths for all files in the directory
        according to the given :ref:`path filter <path_filters>`. This is typically used to scan an EPUB 
        :ref:`template directory <template_dir>` for the files it contains, which will be included (copied or
        processed as |templ| files) in the final EPUB.

        :param str templateDir: The filesystem path to the directory to scan for files.
        :param path_filter: The filter used to determine whether or not each path should be included in the output.
        :type path_filter: :ref:`path filter <path_filters>`

        :returns:
            Returns a pair of sequences: the first is a list of directory paths, the second is a list of file paths.
            The elements of each list are strings giving the path of the item *relative* to the given `templateDir`.
        """
        srcDirs = []
        srcFiles = []
        rootLength = None

        if path_filter is None:
            path_filter = lambda path : True

        for root, dirs, files in os.walk(templateDir):
            #We want to strip the template directory path off the beginning of every path, to only get
            # the relative path. But we want to make sure we get it the way os.walk will use it,
            # which is the first root it returns.
            if rootLength is None:
                rootLength = len(root)
                root = ""
            else:
                #Already have the template directory path, so strip that off to get the relative path for
                # this directory.
                root = root[rootLength:]
                if root.startswith("\\") or root.startswith("/"):
                    root = root[1:]


            for d in dirs:
                path = os.path.join(root, d)
                if path_filter(path):
                    srcDirs.append(path)

            for f in files:
                f = os.path.join(root, f)
                if path_filter(f):
                    srcFiles.append(f)

        return srcDirs, srcFiles
        

    def writeEpub(self):
        """
        Actually generates and outputs all of the EPUB content and the final EPUB document.
        """

        self.__zipfile = zipfile.ZipFile(self.__ofile, "w")
        self.__zipfile.writestr("mimetype", "application/epub+zip")

        #Find all of our source files. Save a list of templ files we need to process, and add
        # verbatim files directly to the zipfile.
        srcDirs, srcFiles = EpubWriter.findSrcFiles(self.__templateDir, self.__tdFilter)
        templFiles = []
        for f in srcFiles:
            if os.path.join(self.__templateDir, f) == self.__chapterTemplatePath:
                continue
            if os.path.join(self.__templateDir, f) == self.__bookTitleTemplatePath:
                continue
            if os.path.join(self.__templateDir, f) == self.__partTitleTemplatePath:
                continue
            elif self.__tmplFilter(f):
                templFiles.append(f)
            else:
                src = os.path.join(self.__templateDir, f)
                arcname = f
                self.__zipfile.write(src, arcname)


        ##### Start generating content

        #This is the templ scope into which we will put all of our generated content.
        globs = templ.texec.getGlobalScope()
        templStack = templ.stack.Stack(globs)
        topScope = templStack.push()

        ### Generate title stuff.
        allTitles = self.__tome.allTitles()
        topScope["TITLE-LIST"] = templ.ttypes.List(allTitles)
        topScope["TITLE-COUNT"] = templ.ttypes.String(len(allTitles))
        topScope["TITLE"] = templ.ttypes.String(self.generate_TITLE())
        topScope["SUBTITLES-DC-XML"] = templ.ttypes.String(self.generate_SUBTITLES_DC_XML())
        topScope["SUBTITLES-HTML"] = templ.ttypes.String(self.generate_SUBTITLES_HTML())

        ### Generate author stuff.
        allAuthors = self.__tome.authors()
        firstAuthor = self.generate_AUTHOR()
        topScope["AUTHOR-LIST"] = templ.ttypes.List(allAuthors)
        topScope["AUTHOR-COUNT"] = templ.ttypes.String(len(allAuthors))
        topScope["AUTHOR"] = templ.ttypes.String(firstAuthor)
        topScope["AUTHORS-DC-XML"] = templ.ttypes.String(self.generate_AUTHORS_DC_XML())
        topScope["AUTHORS-HTML"] = templ.ttypes.String(self.generate_AUTHORS_HTML())

        ### Some additional top-level contnet
        now = time.gmtime()
        topScope["UID"] = templ.ttypes.String(self.__uid)
        topScope["LANG"] = templ.ttypes.String(self.__lang)
        topScope["MODIFIED"] = templ.ttypes.String(time.strftime("%Y-%m-%dT%H:%M:%SZ", now))
        topScope["COPYRIGHT-YEAR"] = templ.ttypes.String(time.strftime("%Y", now))
        topScope["COPYRIGHT-HOLDER"] = templ.ttypes.String(firstAuthor)

        topScope["LICENSE-HTML"] = templ.ttypes.String("")
        if self.__tome.hasMeta("license-html"):
            topScope["LICENSE-HTML"] = templ.ttypes.String(
                "\n".join(self.__tome.getMeta("license-html"))
            )
        elif self.__tome.hasMeta("license"):
            license = self.__tome.getMeta("license")
            if len(license) == 1:
                pretext = "Licensed under "
                license = license[0]
                urls = self.__tome.getMeta("license-url")
                if len(urls) == 1:
                    licenseHtml = """<a rel="license" href="{url}">{license}</a>""".format(
                        url = htmlEscape(urls[0]), license = htmlEscape(license)
                    )
                else:
                    licenseHtml = htmlEscape(license)
                licenseHtml = pretext + licenseHtml
                topScope["LICENSE-HTML"] = templ.ttypes.String(licenseHtml)

        topScope["LICENSE-LINK-HTML"] = templ.ttypes.String("")
        if self.__tome.hasMeta("license-url"):
            topScope["LICENSE-LINK-HTML"] = templ.ttypes.String(
                "".join(("""
        <link rel="license" href="{url}" />""".format(
                        url = htmlEscape(url)
                    )) for url in self.__tome.getMeta("license-url")
            )
        )

        #Generate a complete list of files to be generated.
        prtFiles = []
        bkFiles = []
        chFiles = []
        genFiles = []
        prtNum = bkNum = chNum = 0
        for prtIdx in xrange(len(self.__tome)):
            prtNum += 1
            part = self.__tome[prtIdx]
            if part.title() is not None:
                prtFile = self.partFileName(prtNum)
                prtFiles.append(prtFile)
                genFiles.append(prtFile)
            for bkIdx in xrange(len(part)):
                bkNum += 1
                book = part[bkIdx]
                if book.title() is not None:
                    bkFile = self.bookFileName(bkNum)
                    bkFiles.append(bkFile)
                    genFiles.append(bkFile)
                for chIdx in xrange(len(book)):
                    chNum += 1
                    chFile = self.chapterFileName(chNum)
                    chFiles.append(chFile)
                    genFiles.append(chFile)

        self.__fileList = []
        if self.__frontPage is not None:
            self.__fileList.append(self.__frontPage)
        self.__fileIdx = len(self.__fileList)
        self.__fileList += genFiles
        if self.__backPage is not None:
            self.__fileList.append(self.__backPage)


        for prtIdx in xrange(len(self.__tome)):
            self.__prtNum += 1
            self.generatePart(templStack, self.__tome[prtIdx], prtIdx, len(self.__tome))


        #Now that we've processed everything, we can add the rest of the symbols to the scope.

        topScope["PART-COUNT"] = templ.ttypes.String(self.__prtNum)
        topScope["BOOK-COUNT"] = templ.ttypes.String(self.__bkNum)
        topScope["CHAP-COUNT"] = templ.ttypes.String(self.__chNum)

        topScope["PART-FILE-LIST"] = templ.ttypes.List(prtFiles)
        topScope["BOOK-FILE-LIST"] = templ.ttypes.List(bkFiles)
        topScope["CHAP-FILE-LIST"] = templ.ttypes.List(chFiles)
        topScope["GEN-FILE-LIST"] = templ.ttypes.List(genFiles)

        topScope["LAST-GEN-FILE-HTML"] = topScope["LAST-CHAP-FILE-HTML"] = templ.ttypes.String(htmlEscape(self.chapterFileName(self.__chNum)))

        hasEndnotes = False
        for notes in self.__enList:
            if len(notes) > 0:
                hasEndnotes = True
                break
        topScope["HAS-ENDNOTES"] = templ.ttypes.String("0")
        if hasEndnotes:
            topScope["HAS-ENDNOTES"] = templ.ttypes.String("1")

        topScope["ENDNOTES-LIST"] = templ.ttypes.List(self.__enList)
        topScope["ENDNOTES-HTML"] = templ.ttypes.String(self.generate_ENDNOTES_HTML())

        topScope["MANIFEST-XML"] = templ.ttypes.String(self.generate_MANIFEST_XML())
        topScope["SPINE-XML"] = templ.ttypes.String(self.generate_SPINE_XML())
        topScope["NAV-HTML"] = templ.ttypes.String(self.generate_NAV_HTML())
        topScope["NCX-XML"] = templ.ttypes.String(self.generate_NCX_XML())
        topScope["TOC-HTML"] = templ.ttypes.String(self.generate_TOC_HTML())


        #Now we can process all the other template files in the template dir.
        for path in templFiles:
            src = os.path.join(self.__templateDir, path)
            destname = os.path.splitext(path)[0]

            istream = open(src, "r")
            obuffer = cStringIO.StringIO()
            ostream = templ.tstreams.TemplateStreamOutputStream(obuffer)
            templ.templ.processWithStack(istream, ostream, templStack, src, debug=False)
            content = obuffer.getvalue()
            ostream.close()
            istream.close()
            self.__writeGenFile(destname, content)

        self.__zipfile.close()

            
    def preloadTitledScope(self, scope, key, titled, idx, total, number, isFirst, isLast):
        """
        Prepopualtes a scope for a titled object. This is done before
        we know if it's explicit or not.

        :param scope: The scope to populate
        :type scope: :py:class:`templ.stack.Scope`

        :param str key: The key for the scope symbols: "PART", "BOOK", or "CHAP"

        :param int idx: The index of the object within it's parent, starting at 0.

        :param int total: The total number of elements in the parent object.

        :param int number: The overall number of this element counting (this type of
        element) continuously through the entire document, starting at 1.

        :param bool isFirst: Indicates whether or not this is the first section
            of its kind in the entire document.
        :param bool isLast: Indicats whether or not this is the last section of
            its kind in the entire document.
        """
        scope[key + "-NUM"] = templ.ttypes.String(number)
        scope[key + "-IDX"] = templ.ttypes.String(idx)
        scope[key + "-LEN"] = templ.ttypes.String(len(titled))

        scope[key + "-IS-FIRST"] = templ.ttypes.String("0")
        scope[key + "-IS-LAST"] = templ.ttypes.String("0")
        if isFirst:
            scope[key + "-IS-FIRST"] = templ.ttypes.String("1")
        if isLast:
            scope[key + "-IS-LAST"] = templ.ttypes.String("1")

        #Defaults
        scope[key + "-TITLE"] = templ.ttypes.String("")
        scope[key + "-EXP"] = templ.ttypes.String("0")


    def loadTitledScope(self, scope, key, titled, idx, total, number):
        """
        Populates explicitely titled sections.

        :param scope: The scope to populate
        :type scope: :py:class:`templ.stack.Scope`

        :param str key: The key for the scope symbols: "PART", "BOOK", or "CHAP"

        :param titled: The titled section.
        :type titled: :py:class:`~Tome.TitledDivision`

        :param int idx: The index of the object within it's parent, starting at 0.

        :param int total: The total number of elements in the parent object.

        :param int number: The overall number of this element counting (this type of
        element) continuously through the entire document, starting at 1.
        """
        scope[key + "-TITLE"] = templ.ttypes.String(titled.title())
        scope[key + "-EXP"] = templ.ttypes.String("1")

        scope[key + "-TITLE-LIST"] = templ.ttypes.List(titled.allTitles())
        scope[key + "-TITLE"] = templ.ttypes.String(self.generate_any_TITLE(titled))
        scope[key + "-TITLE-SEP-HTML"] = templ.ttypes.String(self.generate_any_TITLE_SEP_HTML(titled))
        scope[key + "-TITLES-HTML"] = templ.ttypes.String(self.generate_any_TITLES_HTML(titled))
        scope[key + "-SUBTITLES-HTML"] = templ.ttypes.String(self.generate_any_SUBTITLES_HTML(titled))
        scope[key + "-SHORTMARK"] = templ.ttypes.String(self.generate_any_SHORTMARK(titled))
        scope[key + "-HAS-SHORTMARK"] = templ.ttypes.String(self.generate_any_HAS_SHORTMARK(titled))
        scope[key + "-SHORTMARK-SEP-HTML"] = templ.ttypes.String(self.generate_any_SHORTMARK_SEP_HTML(titled))

        scope["REL-PREV-HTML"] = templ.ttypes.String(self.generate_REL_PREV_HTML())
        scope["HAS-PREV"] = templ.ttypes.String("0")
        scope["PREV-FILE"] = templ.ttypes.String("")
        if self.__fileIdx > 0:
            scope["HAS-PREV"] = templ.ttypes.String("1")
            scope["PREV-FILE"] = templ.ttypes.String(self.__fileList[self.__fileIdx-1])

        scope["REL-NEXT-HTML"] = templ.ttypes.String(self.generate_REL_NEXT_HTML())
        scope["HAS-NEXT"] = templ.ttypes.String("0")
        scope["NEXT-FILE"] = templ.ttypes.String("")
        if self.__fileIdx+1 < len(self.__fileList):
            scope["HAS-NEXT"] = templ.ttypes.String("1")
            scope["NEXT-FILE"] = templ.ttypes.String(self.__fileList[self.__fileIdx+1])


    def generatePart(self, templStack, part, prtIdx, parentLength):
        """
        :param templStack: The templ stack to use.
        :type templStack: :py:class:`templ.stack.Stack`

        :param part: The part object to generate.
        :type part: `~Tome.Part`

        :param int prtIdx: The index into the tome of the part, starting at 0.

        :param int parentLength: The number of parts in the tome.

        `__prtNum` is the number of the part through the whole tome, starting at 1.
        """
        prtScope = templStack.push()

        isFirst = prtIdx == 0
        isLast = (prtIdx+1) == parentLength
        self.preloadTitledScope(prtScope, "PART", part, prtIdx, parentLength, self.__prtNum, isFirst, isLast)

        prtTitle = part.title()
        if prtTitle is not None:
            #Explicit, so create the title page.
            self.loadTitledScope(prtScope, "PART", part, prtIdx, parentLength, self.__prtNum)

            self.__fileIdx += 1

            #Open the template file.
            try:
                #TODO: Buffer this once, instead of reading it every time.
                istream = open(self.__partTitleTemplatePath, "r")
            except Exception, e:
                raise Exception("Error opening part template file for reading:", e)

            prtOstream = cStringIO.StringIO()
            ostream = templ.tstreams.TemplateStreamOutputStream(prtOstream)
            templ.templ.processWithStack(istream, ostream, templStack, self.__partTitleTemplatePath, debug=False)
            istream.close()
            prtFileContent = prtOstream.getvalue()
            prtOstream.close()

            #Output the part file.
            self.writePartFile(self.__prtNum, prtFileContent)

        #Process all the books in this part.
        for bkIdx in xrange(len(part)):
            self.__bkNum += 1
            self.generateBook(templStack, part[bkIdx], bkIdx, len(part), isFirst, isLast)

        #Pop the part scope.
        templStack.pop()


    def writePartFile(self, number, contents):
        self.__writeGenFile(self.partFileName(number), contents)

    def writeBookFile(self, number, contents):
        self.__writeGenFile(self.bookFileName(number), contents)

    def writeChapterFile(self, number, contents):
        self.__writeGenFile(self.chapterFileName(number), contents)

    def __writeGenFile(self, relPath, contents):
        #Add the generated book file to the zipfile.
        self.__zipfile.writestr(relPath, contents)


    def generateBook(self, templStack, book, bkIdx, parentLength, parentIsFirst, parentIsLast):
        """
        :param templStack: The templ stack to use.
        :type templStack: :py:class:`templ.stack.Stack`

        :param book: The book object to generate.
        :type book: `~Tome.Book`

        :param int bkIdx: The index into the part of the book, starting at 0.

        :param int parentLength: The number of books in the part.

        `__bkNum` is the number of the book through the whole tome, starting at 1.
        """
        bkScope = templStack.push()

        isFirst = parentIsFirst and (bkIdx == 0)
        isLast = parentIsLast and (bkIdx+1 == parentLength)
        self.preloadTitledScope(bkScope, "BOOK", book, bkIdx, parentLength, self.__bkNum, isFirst, isLast)

        bkTitle = book.title()
        if bkTitle is not None:
            #Explicit, so create the title page.
            self.loadTitledScope(bkScope, "BOOK", book, bkIdx, parentLength, self.__bkNum)

            self.__fileIdx += 1

            #Open the template file.
            try:
                #TODO: Buffer this once, instead of reading it every time.
                istream = open(self.__bookTitleTemplatePath, "r")
            except Exception, e:
                raise Exception("Error opening book template file for reading:", e)

            bkOstream = cStringIO.StringIO()
            ostream = templ.tstreams.TemplateStreamOutputStream(bkOstream)
            templ.templ.processWithStack(istream, ostream, templStack, self.__bookTitleTemplatePath, debug=False)
            istream.close()
            bkFileContent = bkOstream.getvalue()
            bkOstream.close()

            #Output the book file.
            self.writeBookFile(self.__bkNum, bkFileContent)


        #Process all the chapters in this book.
        for chIdx in xrange(len(book)):
            self.__chNum += 1
            self.generateChapter(templStack, book[chIdx], chIdx, len(book), isFirst, isLast)

        #Pop the book scope.
        templStack.pop()



    def generateChapter(self, templStack, chapter, chIdx, parentLength, parentIsFirst, parentIsLast):
        """
        :param templStack: The templ stack to use.
        :type templStack: :py:class:`templ.stack.Stack`

        :param chapter: The chapter object to generate.
        :type chapter: `~Tome.Chapter`

        :param int chIdx: The index into the book of the chapter, starting at 0.

        :param int parentLength: The number of chapters in the book.

        `__chNum` is the number of the chapter through the whole tome, starting at 1.
        """
        chScope = templStack.push()

        isFirst = parentIsFirst and (chIdx == 0)
        isLast = parentIsLast and ((chIdx+1) == parentLength)
        self.preloadTitledScope(chScope, "CHAP", chapter, chIdx, parentLength, self.__chNum, isFirst, isLast)
        self.loadTitledScope(chScope, "CHAP", chapter, chIdx, parentLength, self.__chNum)

        #Legacy symbols:
        chScope["CHAP-REL-PREV-HTML"] = templ.ttypes.String(self.generate_REL_PREV_HTML())
        chScope["CHAP-REL-NEXT-HTML"] = templ.ttypes.String(self.generate_REL_NEXT_HTML())

        #Open the template file.
        try:
            #TODO: Buffer this once, instead of reading it every time.
            istream = open(self.__chapterTemplatePath, "r")
        except Exception, e:
            raise Exception("Error opening chapter template file for reading:", e)

        self.generateChapterContent(chScope, chapter)

        self.__fileIdx += 1

        chOstream = cStringIO.StringIO()
        ostream = templ.tstreams.TemplateStreamOutputStream(chOstream)
        templ.templ.processWithStack(istream, ostream, templStack, self.__chapterTemplatePath, debug=False)
        istream.close()
        chFileContent = chOstream.getvalue()
        chOstream.close()

        #Output the book file.
        self.writeChapterFile(self.__chNum, chFileContent)


        #Pop the chap scope.
        templStack.pop()


    def generateChapterContent(self, chScope, chapter):
        """
        Writes all the content files.
        """

        #Legacy symbol:
        chScope["CHAP-SCENE-COUNT"] = templ.ttypes.String(len(chapter))


        #### Generate chapter content.

        #Add a new set of endnotes for this chapter.
        self.__enList.append([])

        #Open a buffer to write out content to. After we generate the content,
        # we'll stick it into the templ scope.
        chContentBuffer = cStringIO.StringIO()

        ### Iterate over scenes.
        scCount = len(chapter)
        scLastScene = scCount - 1
        for scIdx in xrange(scCount):
            scene = chapter[scIdx]

            ### Generate the content for the scene.

            #Write an anchor for the scene.
            chContentBuffer.write("        <a id='ch{chNum}Scene{scIdx}' />\n".format(
                chNum = self.__chNum,
                scIdx = scIdx+1
            ))

            #Iterate over each paragraph in the scene.
            parCount = len(scene)
            for j in xrange(parCount):
                paragraph = scene[j]
                if len(paragraph) == 0:
                    continue

                tag = paragraph.tag()
                if tag not in ("p", "pre"):
                    raise Exception("Invalid toplevel element in scene: %s" % tag)

                classes = []
                if j == 0:
                    classes.append("firstPar")
                if scIdx == 0:
                    classes.append("firstScene")

                classHtml = ""
                if len(classes) > 0:
                    classHtml = " ".join(classes)
                    classHtml = " class='%s'" % classHtml
                chContentBuffer.write("        <%s%s>\n" % (tag, classHtml))

                #Iterate over each toplevel segment in the paragraph.
                for k in xrange(len(paragraph)):
                    self.writeSegment(chContentBuffer, paragraph[k], dropCap = (scIdx==0 and j==0 and k==0))

                chContentBuffer.write("\n</%s>\n\n" % tag)

            #Scene separator
            lastScene = ""
            firstScene = ""
            if scIdx == scLastScene:
                lastScene = "lastScene"
            if scIdx == 0:
                firstScene = "firstScene"
            chContentBuffer.write("        <hr class='sceneSep %s %s' />\n\n" % (firstScene, lastScene))

        chScope["CHAP-CONTENT"] = templ.ttypes.String(chContentBuffer.getvalue())
        chContentBuffer.close()


        ### Process end notes for the chapter.
        chEndNotes = self.__enList[-1]
        chScope["CHAP-ENDNOTES-LIST"] = templ.ttypes.List(chEndNotes)

        #Now if there really are end notes, overwrite with those.
        if len(chEndNotes) > 0:
            chScope["CHAP-HAS-ENDNOTES"] = templ.ttypes.String("1")
            chScope["CHAP-ENDNOTES-TITLE-HTML"] = templ.ttypes.String(self.generate_CHAP_ENDNOTES_TITLE_HTML(chapter, self.__chNum))
            chScope["CHAP-ENDNOTES-HTML"] = templ.ttypes.String(self.generate_CHAP_ENDNOTES_HTML(chapter, chEndNotes, self.__chNum))
        else:
            chScope["CHAP-HAS-ENDNOTES"] = templ.ttypes.String("0")
            chScope["CHAP-ENDNOTES-TITLE-HTML"] = templ.ttypes.String("")
            chScope["CHAP-ENDNOTES-HTML"] = templ.ttypes.String("")


    def chapterFileName(self, chNum):
        return "chapter%s.xhtml" % self.__chUid(chNum)

    def bookFileName(self, bkNum):
        return "book%s.xhtml" % self.__chUid(bkNum)

    def partFileName(self, prtNum):
        return "part%s.xhtml" % self.__chUid(prtNum)


    def generate_AUTHORS_HTML(self):
        authorsHtml = "<ol>\n"
        for author in self.__tome.authors():
            authorsHtml += "    <li class='author'>%s</li>\n" % htmlEscape(author)
        authorsHtml += "</ol>"
        return authorsHtml

    def generate_AUTHORS_DC_XML(self):
        authorDcXml = ""
        cid = 0
        for author in self.__tome.authors():
            cid += 1
            authorAs = author.split()
            if len(authorAs) > 1:
                authorAs = authorAs[-1] + ", " + " ".join(authorAs[:-1])
            else:
                authorAs = author
            authorDcXml += """
        <dc:creator id='creator{cid}'>{author}</dc:creator>
            <meta refines='#creator{cid}' property='role' scheme='marc:relators'>aut</meta>
            <meta refines='#creator{cid}' property='file-as'>{authorAs}</meta>
    """.format(
                cid=str(cid),
                author=htmlEscape(author),
                authorAs=htmlEscape(authorAs),
            )
        return authorDcXml



    def generate_CHAP_TITLE(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_TITLE> instead.
        """
        return generate_any_TITLE(chapter)

    def generate_any_TITLE(self, titled):
        title = titled.title()
        if title is None:
            return ""
        else:
            return title

    def generate_TITLE(self):
        return self.generate_any_TITLE(self.__tome)

    def generate_AUTHOR(self):
        authors = self.__tome.authors()
        if len(authors) == 0:
            return ""
        else:
            return authors[0]

    def generate_CHAP_SHORTMARK(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_SHORTMARK> instead.
        """
        return generate_any_SHORTMARK(chapter)

    def generate_any_SHORTMARK(self, titled):
        """
        Returns a short title for the given titled section. If the section has a short mark, then it is the shortmark.
        If it doesn't, then it is the first title. If it doesn't have a title either, then it's an empty string.
        """
        smark = titled.shortMark()
        if smark is None:
            return self.generate_any_TITLE(titled)
        else:
            return smark

    def hasChapShortMark(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <hasShortMark> instead.
        """
        return hasShortMark(chapter)

    def hasShortMark(self, titled):
        """
        Determines whether or not the given section has a short mark, as specified by <generate_any_SHORTMARK>, which
        really just means it has anything it can use for a shortmark.
        """
        smark = titled.shortMark()
        if smark is None:
            if len(titled.allTitles()) == 0:
                return False
            else:
                return True
        else:
            return False

    def generate_CHAP_HAS_SHORTMARK(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_HAS_SHORTMARK> instead.
        """
        return generate_any_HAS_SHORTMARK(chapter)

    def generate_any_HAS_SHORTMARK(self, titled):
        if self.hasShortMark(titled):
            return "1"
        else:
            return "0"

    def generate_CHAP_SHORTMARK_SEP_HTML(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_SHORTMARK_SEP_HTML> instead.
        """
        return generate_any_SHORTMARK_SEP_HTML(chapter)

    def generate_any_SHORTMARK_SEP_HTML(self, titled):
        """
        Returns an HTML string which can be used to separate the section's shortmark from other text, for instance the section number.
        If there is no short mark (as determined by :meth:`hasShortMark`), returns an empty string, so you can safely include this
        regardless of whether there is or isn't a short mark.
        """
        if self.hasShortMark(titled):
            return " &#8211; "
        else:
            return ""

    def generate_CHAP_TITLE_SEP_HTML(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_TITLE_SEP_HTML> instead.
        """
        return generate_any_TITLE_SEP_HTML(chapter)

    def generate_any_TITLE_SEP_HTML(self, titled):
        if len(titled.allTitles()) == 0:
            return ""
        else:
            return " &#8211; "

    def generate_CHAP_TITLES_HTML(self, chapter):
        """
        .. deprecated:: 1.1.0.0
        Use <generate_any_TITLES_HTML> instead.
        """
        return generate_any_TITLES_HTML(chapter)

    def generate_any_TITLES_HTML(self, titled):
        #Build the HTML for the chatper titles.
        titleLevel = 2
        titleIdx = 0
        htmlAllTitles = ""
        allTitles = titled.allTitles()
        titleCount = len(allTitles)
        for title in allTitles:
            titleIdx += 1

            lastTitle = ""
            subtitleClasses = ""

            if titleIdx == titleCount:
                lastTitle = "lastTitle"
            if titleIdx > 1:
                subtitleClasses = "subtitle subtitle%d" % (titleIdx)

            htmlAllTitles += "<h%d class='title %s %s'>%s</h%d>\n" % (titleLevel, subtitleClasses, lastTitle, htmlEscape(title), titleLevel)
            if titleLevel < 6:
                titleLevel += 1
        return htmlAllTitles

    def generate_ENDNOTES_HTML(self):
        endNotesHtml = """
            <div class='rearnotes'>"""


        chIdx = 0
        for part in self.__tome:
            for book in part:
                for chapter in book:
                    chEndNotes = self.__enList[chIdx]
                    chIdx += 1
                    if len(chEndNotes) > 0:
                        chNum = str(chIdx)
                        chUid = self.__chUid(chIdx)
                        shortMark = self.generate_any_SHORTMARK_SEP_HTML(chapter) + self.generate_any_SHORTMARK(chapter)

                        #Open the chapter section.
                        endNotesHtml += """
                <a id='endnotesCh{chNum}' />
                <h3>Notes for Ch. {chNum}{shortMark}</h3>
                <dl>
    """.format(chNum = chNum, shortMark=shortMark)

                        #Write all the endnotes for this chapter.
                        for e in xrange(len(chEndNotes)):
                            enNum = str(e+1)

                            endNotesHtml += ("""
                    <dt class='note'>
                        <a id='endnotesCh{chNum}N{enNum}' />
                        <a href='chapter{chUid}.xhtml#ch{chNum}N{enNum}Ref'>[{enNum}]</a>
                    </dt>
                    <dd class='note'>{enContent}</dd>
                """.format(
                                chUid = chUid,
                                chNum = chNum,
                                enNum = enNum,
                                enContent = chEndNotes[e]
                            ))

                        #Close the chapter end-notes.
                        endNotesHtml += ("""
                </dl>
""")

        endNotesHtml += """
            </div>
"""

        return endNotesHtml


    def generate_CHAP_ENDNOTES_HTML(self, chap, chEndNotes, chIdx):
        chUid = self.__chUid(chIdx)
        chNum = str(chIdx)

        chEndNotesHtml = ""

        chEndNotesHtml += ("""
            <dl>
""")

        ### Generate the remaining content for the chapter endnotes section.
        for e in xrange(len(chEndNotes)):
            enNum = str(e+1)
            chEndNotesHtml += ("""
                <dt class='note'>
                    <a id='ch{chNum}N{enNum}' />
                    <a href='chapter{chUid}.xhtml#ch{chNum}N{enNum}Ref'>[{enNum}]</a>
                </dt>
                <dd class='note'>{enContent}</dd>
""".format(
                chNum = chNum,
                enNum = enNum,
                chUid = chUid,
                enContent = chEndNotes[e]
            ))

        #Close the chapter-end notes.
        chEndNotesHtml += ("""
            </dl>
""")

        return chEndNotesHtml


    def generate_CHAP_ENDNOTES_TITLE_HTML(self, chap, chIdx):
        """
        Assumed that there are endnotes for the chapter.
        """

        return """
            <a id='ch{chNum}Notes' />
            <h2 class='title'>Chapter Notes</h2>""".format(chNum = str(chIdx))

            
    def generate_SUBTITLES_HTML(self):
        """
        .. deprecated:: 1.1.0.0
        Use `generate_any_SUBTITLES_HTML`, passing in `__tome`.
        """
        return self.generate_any_SUBTITLES_HTML(self.__tome)


    def generate_any_SUBTITLES_HTML(self, titled):
        ### Build some HTML for the sub titles.
        titleLevel = 2
        subtitleHtml = ""
        allSubTitles = titled.allTitles()[1:]
        stitleCount = len(allSubTitles)
        for titleIdx in xrange(stitleCount):
            lastTitle = ""
            if titleIdx+1 == stitleCount:
                lastTitle = "lastTitle"
            title = allSubTitles[titleIdx]
            subtitleHtml += "<h%d class='title subtitle subtitle%d %s'>%s</h%d>\n" % (titleLevel, titleIdx, lastTitle, htmlEscape(title), titleLevel)
            subtitleHtml += "<hr class='titleSep subtitle subtitle%d %s'/>\n" % (titleIdx, lastTitle)
            if titleLevel < 5:
                titleLevel += 1

        return subtitleHtml

    def generate_SUBTITLES_DC_XML(self):
        dcTitleSubTitles = ""
        titleSeq = 2
        for subtitle in self.__tome.allTitles()[1:]:
            dcTitleSubTitles += """
        <dc:title id='subtitle{titleSeq}'>{subtitle}</dc:title>
            <meta refines="#subtitle{titleSeq}" property="title-type">subtitle</meta>
            <meta refines="#subtitle{titleSeq}" property="display-seq">{titleSeq:d}</meta>
""".format(
                subtitle = htmlEscape(subtitle),
                titleSeq = titleSeq
            )
            titleSeq += 1
        return dcTitleSubTitles

        

    def generate_MANIFEST_XML(self, chapterFiles=None):
        """
        :param chapterFiles: **deprecated** No longer used.
        """
        manifestXml = ""
        chNum = 0
        bkNum = 0
        prtNum = 0
        for part in self.__tome:
            prtNum += 1

            #Title page files for explicit parts.
            if part.title() is not None:
                manifestXml += """
            <item id="part{idx}" href="{path}" media-type="application/xhtml+xml" />""".format(
                    idx = str(prtNum),
                    path = self.partFileName(prtNum)
                )

            for book in part:
                bkNum += 1

                #Title page files for explicit books.
                if book.title() is not None:
                    manifestXml += """
                <item id="book{idx}" href="{path}" media-type="application/xhtml+xml" />""".format(
                        idx = str(bkNum),
                        path = self.bookFileName(bkNum)
                    )

                for chapter in book:
                    chNum += 1
                    manifestXml += """
                <item id="chapter{idx}" href="{path}" media-type="application/xhtml+xml" />""".format(
                        idx = str(chNum),
                        path = self.chapterFileName(chNum)
                    )

        return manifestXml

    def generate_SPINE_XML(self):
        spineXml = ""
        chNum = 0
        bkNum = 0
        prtNum = 0
        #TODO: FIXME: Only include part and book if explicitely titled.
        for part in self.__tome:
            prtNum += 1

            #Title page files for explicit parts.
            if part.title() is not None:
                spineXml += """
            <itemref idref="part{idx}" />""".format(
                    idx = str(prtNum)
                )

            for book in part:
                bkNum += 1

                #Title page files for explicit books.
                if book.title() is not None:
                    spineXml += """
                <itemref idref="book{idx}" />""".format(
                        idx = str(bkNum)
                    )

                for chapter in book:
                    chNum += 1
                    spineXml += """
                <itemref idref="chapter{idx}" />""".format(
                        idx = str(chNum)
                    )

        return spineXml


    def generate_TOC_HTML(self):
        tocHtml = ""
        prtNum = 0
        bkNum = 0
        chNum = 0
        for part in self.__tome:
            prtNum += 1
            if part.title() is not None:
                title = self.generate_any_TITLE_SEP_HTML(part) + htmlEscape(self.generate_any_TITLE(part))
                tocHtml += """
                <li class='bodymatter part' id='tocPart{idx}'>
                    <a href="{path}">
                        Part {idx}{title}
                    </a>
                </li>""".format(
                    idx = str(prtNum),
                    path = self.partFileName(prtNum),
                    title = title
                )
                
            for book in part:
                bkNum += 1
                if book.title() is not None:
                    title = self.generate_any_TITLE_SEP_HTML(book) + htmlEscape(self.generate_any_TITLE(book))
                    tocHtml += """
                    <li class='bodymatter book' id='tocBook{idx}'>
                        <a href="{path}">
                            Book {idx}{title}
                        </a>
                    </li>""".format(
                        idx = str(bkNum),
                        path = self.bookFileName(bkNum),
                        title = title
                    )

                for chapter in book:
                    chNum += 1
                    title = self.generate_any_TITLE_SEP_HTML(chapter) + htmlEscape(self.generate_any_TITLE(chapter))

                    tocHtml += """
                        <li class='bodymatter chapter' id='tocChapter{idx}'>
                            <a href="{path}">
                                Chapter {idx}{title}
                            </a>
                        </li>""".format(
                        idx = str(chNum),
                        path = self.chapterFileName(chNum),
                        title = title
                    )

        return tocHtml
        


    def generate_NCX_XML(self):
        ncxXml = ""
        chNum = 0
        bkNum = 0
        prtNum = 0
        for part in self.__tome:
            prtNum += 1
            prtOpened = False

            #Title page files for explicit parts.
            if part.title() is not None:
                prtOpened = True

                title = self.generate_any_SHORTMARK_SEP_HTML(part) + self.generate_any_SHORTMARK(part)

                ### Add an entry for the part.
                ncxXml += """
    <navPoint id="part{num}">
        <navLabel>
            <text>Part {num}{title}</text>
        </navLabel>
        <content src="{path}"/>""".format(
                    num = str(prtNum),
                    title = title,
                    path = self.partFileName(prtNum)
                )


            for book in part:
                bkNum += 1
                bkOpened = False


                #Title page files for explicit books.
                if book.title() is not None:
                    bkOpened = True

                    title = self.generate_any_SHORTMARK_SEP_HTML(book) + self.generate_any_SHORTMARK(book)

                    ### Add an entry for the book.
                    ncxXml += """
            <navPoint id="book{num}">
                <navLabel>
                    <text>Book {num}{title}</text>
                </navLabel>
                <content src="{path}"/>""".format(
                        num = str(bkNum),
                        title = title,
                        path = self.bookFileName(bkNum)
                    )

                for chapter in book:
                    chNum += 1

                    title = self.generate_any_SHORTMARK_SEP_HTML(chapter) + self.generate_any_SHORTMARK(chapter)

                    ### Add an entry for the chapter.
                    ncxXml += """
                <navPoint id="chapter{num}">
                    <navLabel>
                        <text>Chapter {num}{title}</text>
                    </navLabel>
                    <content src="{path}"/>""".format(
                        num = str(chNum),
                        title = title,
                        path = self.chapterFileName(chNum)
                    )


                    ### Add an entry for each scene in the chapter.
                    sceneCount = len(chapter)
                    for scNum in xrange(sceneCount):
                        ncxXml += """
                    <navPoint id="ch{chNum}Scene{scNum}">
                        <navLabel>
                            <text>Scene {scNum}</text>
                        </navLabel>
                        <content src="{path}#ch{chNum}Scene{scNum}" />
                    </navPoint>""".format(
                            chNum = str(chNum),
                            scNum = str(scNum+1),
                            path = self.chapterFileName(chNum)
                        )

                    ### Add an entry for the chapter end-notes, if there are any.
                    if len(self.__enList[chNum-1]) > 0:
                        ncxXml += """
                    <navPoint id="ch{num}Notes">
                        <navLabel>
                            <text>Ch. {num} Notes</text>
                        </navLabel>
                        <content src="{path}#ch{num}Notes" />
                    </navPoint>""".format(
                            num = str(chNum),
                            path = self.chapterFileName(chNum)
                        )

                    #Close the chapter item.
                    ncxXml += """
                </navPoint>"""

                if bkOpened:
                    ncxXml += """
            </navPoint>"""

            if prtOpened:
                ncxXml += """
        </navPoint>"""
        
        return ncxXml + "\n"


    def generate_CHAP_REL_PREV_HTML(self):
        """
        .. deprecated:: 1.1.0.0
        Use `generate_REL_PREV_HTML` instead.
        """
        return self.generate_REL_PREV_HTML()

    def generate_REL_PREV_HTML(self):
        """
        Returns an HTML ``link`` element with ``rel="prev"`` attribute to point to the previous
        file, or an empty string if there is no previous file. This uses `__fileList`, and assumes that
        `__fileIdx` is the index of the current file.
        """
        if self.__fileIdx > 0:
            return """<link rel="prev" href="{path}" />""".format(path = htmlEscape(self.__fileList[self.__fileIdx-1]))
        else:
            return ""

    def generate_CHAP_REL_NEXT_HTML(self):
        """
        .. deprecated:: 1.1.0.0
        Use `generate_REL_NEXT_HTML` instead.
        """
        return self.generate_REL_NEXT_HTML()

    def generate_REL_NEXT_HTML(self):
        """
        Returns an HTML ``link`` element with ``rel="next"`` attribute to point to the next
        file, or an empty string if there is no next file. This uses `__fileList`, and assumes that
        `__fileIdx` is the index of the current file.
        """
        if self.__fileIdx+1 < len(self.__fileList):
            return """<link rel="next" href="{path}" />""".format(path = htmlEscape(self.__fileList[self.__fileIdx+1]))
        else:
            return ""



    def generate_NAV_HTML(self):
        navHtml = ""
        chIdx = 0
        for part in self.__tome:
            for book in part:
                for chapter in book:
                    chIdx += 1
                    chUid = self.__chUid(chIdx)
                    chNum = str(chIdx)

                    title = self.generate_any_SHORTMARK_SEP_HTML(chapter) + self.generate_any_SHORTMARK(chapter)

                    ### Add an entry for the chapter.
                    navHtml += """
                <li class='chapter' id='tocDetailedChapter{chNum}'>
                    <a epub:type="division" href="chapter{chUid}.xhtml">
                        Chapter {chNum}{title}
                    </a>
                    <ol>
""".format(
                        chUid = chUid, chNum = chNum, title = title
                    )

                    ### Add an entry for each scene in the chapter.
                    sceneCount = len(chapter)
                    for scIdx in xrange(sceneCount):
                        scNum = str(scIdx + 1)
                        firstScene = ""
                        lastScene = ""
                        if scIdx+1 == sceneCount:
                            lastScene = "lastScene"
                        if scIdx == 0:
                            firstScene = "firstScene"

                        navHtml += """
                        <li class='scene {lastScene} {firstScene}'>
                            <a epub:type="subchapter" href="chapter{chUid}.xhtml#ch{chNum}Scene{scNum}">
                                Scene {scNum}
                            </a>
                        </li>
""".format(
                            lastScene = lastScene,
                            firstScene = firstScene,
                            chNum = chNum,
                            chUid = chUid,
                            scNum = scNum
                        )

                    ### Add an entry for the chapter end-notes, if there are any.
                    if len(self.__enList[chIdx-1]) > 0:
                        navHtml += """
                        <li class='rearnotes'>
                            <a epub:type="rearnotes" href="chapter{chUid}.xhtml#ch{chNum}Notes">
                                Ch. {chNum} Notes
                            </a>
                        </li>
""".format(
                            chUid = chUid,
                            chNum = chNum
                        )

                    #Close the chapter item.
                    navHtml += """
                    </ol>
                </li>
                <!-- (end chapter {chNum}) -->
""".format(chNum = chNum)
        
        return navHtml


if __name__ == "__main__":

    parser = Tome.TomeOtlParser(sys.stdin, filename="<stdin>", debug=True)
    #parser = Tome.TomeXmlParser.parseStream(sys.stdin)
    tome = parser.tome()
    tdFilter = EpubWriter.getListBasedFilter(
        exc_patterns = [".*.swp", ".*.swo"], excludeFirst = True
    )
    writer = EpubWriter(tome, "ant.epub", "epub-template", tdFilter=tdFilter)
    writer.writeEpub()

