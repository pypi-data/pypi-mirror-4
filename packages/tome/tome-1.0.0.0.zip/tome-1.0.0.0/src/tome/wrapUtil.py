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

def justifyWords(line, linewidth):
    """
    Fully justifies text into a given horizontal space.

    Given a list of words (to be separated by spaces), and the number of
    columns to fit them into, figures out how to space the words in order to
    fill the exact amount of space specified by linewidth, and returns that
    string (if there are fewer than 2 words in line, then it will not, in
    general be able to fill the linewidth).

    If linewidth is smaller than what is required, returns the smallest possible
    text.

    :param line:
        The list of words to justify.
    :type line:
        A sequence of strings.

    :param int linewidth:
        The number of columns to fit the text into.
    """
    required = len("".join(line))
    leftOver = linewidth - required
    spCount = len(line) - 1
    if spCount == 0:
        #There's only one word in the line.
        return line[0]

    spacesPer = int(float(leftOver) / float(spCount))
    padd = " "*spacesPer
    leftOver = leftOver - (spacesPer*spCount)

    spaces = [spacesPer] * spCount

    while leftOver > 0:
        longestLength = None
        longestLevel = None
        longestI = None
        for i in xrange(spCount):
            length = len(line[i])
            if longestLength is None:
                #First word, have to pick it as the first.
                longestLength = length
                longestLevel = spaces[i]
                longestI = i
            elif spaces[i] < longestLevel:
                #This word has shortest space we've seen so far, so pick it.
                longestLength = length
                longestLevel = spaces[i]
                longestI = i
            elif spaces[i] == longestLevel and length > longestLength:
                #This word has the same length space as the currently picked,
                # one, but is a longer word, so pick it.
                longestLength = length
                longestLevel = spaces[i]
                longestI = i
        spaces[longestI] += 1
        leftOver -= 1

    #Assemble the line as determined.
    text = ""
    for i in xrange(spCount):
        text += (line[i] + " "*spaces[i])
    text += line[-1]
    return text

def wrapText(text, linewidth, remain=None):
    """
    Generates an array of lines, each line is an array of words, such that the word fit
    into the specified linewidth.

    :param int remain:
        Specifies how many columns remain on the current line. Default is all of them.

    """
    if linewidth < 10:
        linewidth = 10;

    if remain is None:
        remain = linewidth

    word = ""
    widx = 0
    length = len(text)
    line = []
    allLines = []

    while widx <= length:
        if widx == length or text[widx].isspace():
            #End of current word, so we can output it.
            wlength = len(word)

            #Ignore empty words.
            if wlength > 0:

                #See if it can fit on the current line.
                if wlength + 1 > remain:
                    
                    #See if it will fit on one whole line at all.
                    if wlength > linewidth:
                        #It doesn't fit on a line, so we may as well start it on this line, it will have to
                        # break either way.
                        #Output the entire thing on as many lines as it takes.
                        while wlength + 1 > linewidth:
                            line.append(word[:remain])
                            allLines.append(line)
                            line = []
                            word = word[remain:]
                            wlength = len(word)
                            remain = linewidth
                        if wlength > 0:
                            line.append(word)
                            remain = linewidth - wlength - 1
                            word = ""
                    else:
                        #Won't fit on this line, but fits on the next, so break the line, write the word
                        # and we're done.
                        allLines.append(line)
                        line = []
                        line.append(word)
                        remain = linewidth - wlength - 1
                        word = ""

                else:
                    #Fits on current line
                    line.append(word)
                    remain -= (wlength + 1)
                    word = ""
        else:
            word += text[widx]
        widx += 1

    assert(len(word) == 0), word
    if len(line) > 0:
        allLines.append(line)

    return allLines

class TextFormatter(object):
    def __init__(self, stream, linewidth=78):
        self.__stream = stream
        self.__linewidth = linewidth

        self.__justify = False

        self.__indent = "    "
        self.__indentLevel = 0
        self.__currentIndent = ""
        self.__currentIndexLength = 0
        self.__linenum = 0
        self.__colnum = 0
        self.__preformatted = False

    def setPreformatted(self, preformatted):
        self.__preformatted = preformatted

    def __write(self, text, pre=False):
        """
        Writes the given text to the output stream and updates the counters.
        """
        pre = pre or self.__preformatted
        #Write the indent.
        if not pre and self.__colnum == 0:
            self.__stream.write(self.__currentIndent)
            self.__colnum += self.__currentIndexLength 

        self.__stream.write(text)
        self.__colnum += len(text)

    def writePre(self, text):
        """
        Writes pre-formatted text to the output stream. The given text is broken into lines
        and written to the output stream with a `writeLnbrk` after each one, except for the last
        one. If you want to include a linebreak after the last line as well, just tack on an extra
        one before you pass it in.
        """
        lines = text.splitlines()
        for line in lines[:-1]:
            self.__write(line, True)
            self.writeLnbrk()
        self.__write(lines[-1], True)


    def write(self, text):
        """
        Writes the given string to the output stream, starting at where it left off.
        All whitespace in the condensced to space characters.

        TODO: A parameter to specify that it's the end of a paragraph, so we don't
        justify the last line.
        """
        if len(text) == 0:
            return

        if self.__preformatted:
            self.writePre(text)
            return

        if text[0].isspace() and self.__colnum != 0:
            if self.__colnum + 1 >= self.__linewidth:
                self.writeLnbrk()
            else:
                self.__write(" ")

        remain = self.__linewidth - self.__colnum
        lines = wrapText(text, self.__linewidth, remain)
        if len(lines) > 0:
            for line in lines[:-1]:
                self.__writeWordLine(line)
                self.writeLnbrk()
            self.__writeWordLine(lines[-1])

        if len(text.strip()) > 0 and text[-1].isspace() and self.__colnum != 0:
            if self.__colnum + 1 >= self.__linewidth:
                self.writeLnbrk()
            else:
                self.__write(" ")

    def writeLnbrk(self):
        self.__stream.write("\n")
        self.__linenum += 1
        self.__colnum = 0


    def __writeWordLine(self, line):
        """
        Writes a single line starting from where we left off, composed of the given sequence of space-separated words.
        """
        if self.__justify:
            remain = self.__linewidth - self.__colnum
            text = justifyWords(line, remain)
        else:
            text = " ".join(line)
        self.__write(text)

    def indent(self):
        self.__indentLevel += 1
        self.__currentIndent += self.__indent
        self.__currentIndexLength = len(self.__currentIndent)

    def outdent(self):
        self.__indentLevel -= 1
        self.__currentIndent = self.__indent * self.__indentLevel
        self.__currentIndexLength = len(self.__currentIndent)

