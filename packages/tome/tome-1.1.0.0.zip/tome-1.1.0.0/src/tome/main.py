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
import sys
import argparse
import errno
import os
import os.path
import pkg_resources
import shutil

import version
import Tome
import writeEpub
import writeText
import writeLatex
import writeFlow


def writeXmlSchema(args=None, prog_name="tome-xml-schema"):
    if args is None:
        args = sys.argv
    if prog_name is None:
        prog_name = args[0]

    argp = argparse.ArgumentParser(
        prog = prog_name,
        description= "Write the Tome XML schema to file, for reference."
    )
    argp.add_argument('OUTPUT',
        help="The path to the which the schema will be written.",
        nargs='?',
        default = None
    )
    argp.add_argument('-O', '--overwrite',
        help="Overwrite the output file if it already exists.",
        dest='overwrite',
        action='store_true',
        default=False
    )
    argp.add_argument('-P', '--protect',
        help="Do not overwrite the output file if it already exists.",
        dest='overwrite',
        action='store_false',
        default=False
    )


    args = argp.parse_args(args[1:])

    if args.OUTPUT in (None, "-"):
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        outStream = sys.stdout
        outClose = lambda : None

    else:
        if os.path.exists(args.OUTPUT):
            if not args.overwrite:
                sys.stderr.write("%s: Error: Output path already exists.\n" % (prog_name))
                return errno.EINVAL

        outStream = open(args.OUTPUT, "wb")
        outClose = lambda : outStream.close()

    schema = pkg_resources.resource_string(pkg_resources.Requirement.parse("tome"), "res/tome.xsd")
    outStream.write(schema)
    outStream.flush()
    outClose()

    return 0

    
def writeLatexTemplate(args=None, prog_name="tome-latex-template"):
    if args is None:
        args = sys.argv
    if prog_name is None:
        prog_name = args[0]

    argp = argparse.ArgumentParser(
        prog = prog_name,
        description= "Write the default latex template to file, for use as a starting point for creating your own."
    )
    argp.add_argument('OUTPUT',
        help="The path to the which the template will be written.",
        nargs='?',
        default = None
    )
    argp.add_argument('-O', '--overwrite',
        help="Overwrite the output file if it already exists.",
        dest='overwrite',
        action='store_true',
        default=False
    )
    argp.add_argument('-P', '--protect',
        help="Do not overwrite the output file if it already exists.",
        dest='overwrite',
        action='store_false',
        default=False
    )


    args = argp.parse_args(args[1:])

    if args.OUTPUT in (None, "-"):
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        outStream = sys.stdout
        outClose = lambda : None

    else:
        if os.path.exists(args.OUTPUT):
            if not args.overwrite:
                sys.stderr.write("%s: Error: Output path already exists.\n" % (prog_name))
                return errno.EINVAL

        outStream = open(args.OUTPUT, "wb")
        outClose = lambda : outStream.close()

    template = pkg_resources.resource_stream("tome", "res/template.latex.tmpl")
    outStream.write(template.read())
    outStream.flush()
    outClose()

    return 0

    

def writeEpubTemplate(args=None, prog_name="tome-epub-template"):
    if args is None:
        args = sys.argv
    if prog_name is None:
        prog_name = args[0]

    argp = argparse.ArgumentParser(
        prog = prog_name,
        description= "Create a new EPUB template directory for use with Tome."
    )
    argp.add_argument('OUTPUT',
        help="The path to the output directory at which to create the new template."
    )
    argp.add_argument('-E', '--erase',
        help="Erase the output directory if it already exists.",
        dest='overwrite',
        action='store_true',
        default=False
    )
    argp.add_argument('-P', '--protect',
        help="If the output directory already exists, terminate without making changes to it.",
        dest='overwrite',
        action='store_false',
        default=False
    )


    ####### PROCESS ARGUMENTS #######

    args = argp.parse_args(args[1:])

    if os.path.exists(args.OUTPUT):
        if args.overwrite:
            shutil.rmtree(args.OUTPUT)
        else:
            sys.stderr.write("%s: Error: Output path already exists.\n" % (prog_name))
            return errno.EINVAL

    templateDirectory = pkg_resources.resource_filename("tome", "res/epub-template")
    shutil.copytree(templateDirectory, args.OUTPUT)

    return 0

    

class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        license = pkg_resources.resource_string(pkg_resources.Requirement.parse("tome"), "misc/LICENSE.txt")
        sys.stdout.write(license)
        sys.exit(0)


def main(args=None, prog_name="tome"):
    if args is None:
        args = sys.argv
    if prog_name is None:
        prog_name = args[0]


    ###### DEFINE ARGUMENTS #########

    argp = argparse.ArgumentParser(
        prog = prog_name,
        description= "General purpose front end to the Tome markup language and tool suite.",
    )
    argp.add_argument('INPUT',
        help="The input file, or '-' to use STDIN.",
        nargs='?'
    )
    argp.add_argument('OUTPUT',
        help="The output file, or '-' to use STDOUT.",
        nargs='?'
    )

    argp.add_argument('--version',
        action='version',
        version = "%(prog)s " + ("%s -- %s" % (version.string(), version.datestr())),
    )
    argp.add_argument('--license',
        help="Print the complete license to STDOUT and exit.",
        action=LicenseAction,
        nargs=0,
    )

    argp.add_argument('-s', '--syntax',
        help="Specifies the syntax of the input file.",
        choices=("otl", "flow", "xml"),
        dest='syntax',
        default=None
    )
    argp.add_argument('-f', '--fmt', '--format',
        help="Specifies the format for the generated output.",
        choices=("xml", "epub", "txt", "latex", "flow"),
        dest='format',
        default=None
    )
    argp.add_argument('--debug',
        help="Include debug information when parsing input. Is not included in all output formats.",
        dest='debug',
        action='store_true',
        default=False
    )
    argp.add_argument('--xml-compact',
        help="For xml output format, generates compact XML, with no formatting.",
        dest='xml_compact',
        action='store_true',
        default=False,
    )
    argp.add_argument('-X', '--exclude',
        help="For epub output format, add a glob pattern for template directory paths to exclude from the EPUB.",
        dest='epub_exclude',
        action='append',
    )
    argp.add_argument('-I', '--include',
        help="For epub output format, add a glob pattern for template directory paths to include in the EPUB.",
        dest='epub_include',
        action='append',
    )
    argp.add_argument('--exc-first',
        help="For epub output format, choose how the --exclude and --include lists overlap.",
        dest='epub_exclude_first',
        action='store_true',
        default=True,
    )
    argp.add_argument('--inc-first',
        help="For epub output format, choose how the --exclude and --include lists overlap.",
        dest='epub_exclude_first',
        action='store_false',
        default=True,
    )
    argp.add_argument('-T', '--template-dir',
        help="For epub output format, specify the path to the template directory.",
        dest='template_dir',
        default=None
    )
    argp.add_argument('-L', '--line-width',
        help="For txt output format, specifies the width of the line.",
        dest='line_width',
        default=78,
        type=int
    )
    argp.add_argument('-t', '--template-file',
        help="For latex output format, specify the path to the template file.",
        dest='template_file',
        default=None
    )
    argp.add_argument('-d', '--draft',
        help="For latex output format, specify that draft output should be generated.",
        dest='draft',
        action='store_true',
        default=False
    )



    ####### PROCESS ARGUMENTS #######

    args = argp.parse_args(args[1:])

    ### INPUT ###
    if args.INPUT in (None, "-"):
        inFilePath = None
        inFileName = "<stdin>"
    else:
        inFilePath = args.INPUT
        inFileName = args.INPUT

    ### OUTPUT ###
    if args.OUTPUT in (None, "-"):
        outFilePath = None
        outFileName = "<stdout>"
    else:
        outFilePath = args.OUTPUT
        outFileName = args.OUTPUT


    ### SYNTAX ###
    if args.syntax is None:
        if inFilePath is None:
            sys.stderr.write("%s: Error: The --syntax option is required when input file is implicit.\n" % (prog_name))
            return errno.EINVAL

        root, ext = os.path.splitext(inFileName)
        if ext == ".xml":
            args.syntax = "xml"
        elif ext == ".otl":
            args.syntax = "otl"
        elif ext == ".tome":
            args.syntax = "flow"
        else:
            sys.stderr.write("%s: Error: Unable to determine syntax from input file path. Try using the --syntax option.\n" % (prog_name))
            return errno.EINVAL

    ### FORMAT ###
    if args.format is None:
        if outFilePath is None:
            sys.stderr.write("%s: Error: The --format option is required when output file is implicit.\n" % (prog_name))
            return errno.EINVAL

        root, ext = os.path.splitext(outFileName)
        if ext == ".xml":
            args.format = "xml"
        elif ext == ".epub":
            args.format = "epub"
        elif ext == ".txt":
            args.format = "txt"
        elif ext in (".tex", ".latex"):
            args.format = "latex"
        elif ext == ".tome":
            args.format = "flow"
        else:
            sys.stderr.write("%s: Error: Unable to determine format from output file path. Try using the --format option.\n" % (prog_name))
            return errno.EINVAL



    ############# OPEN FILES #############

    if inFilePath is None:
        inStream = sys.stdin
        inClose = lambda : None
    else:
        try:
            inStream = open(inFilePath, "r")
            inClose = lambda : inStream.close()
        except Exception, e:
            sys.stderr.write("%s: Error: An error occurred attempting to open the input stream:\n" % (prog_name))
            sys.stderr.write(str(e) + "\n")
            return errno.EIO

    if outFilePath is None:
        outStream = sys.stdout
        outClose = lambda : None
    else:
        try:
            outStream = open(outFilePath, "w")
            outClose = lambda : outStream.close()
        except Exception, e:
            sys.stderr.write("%s: Error: An error occurred attempting to open the output stream:\n" % (prog_name))
            sys.stderr.write(str(e) + "\n")
            inClose()
            return errno.EIO

    try:

        ########## PARSE THE INPUT ###############
    
        try:
            if args.syntax == "xml":
                parser = Tome.TomeXmlParser.parseStream(inStream)
            elif args.syntax == "otl":
                parser = Tome.TomeOtlParser(inStream, debug=args.debug, filename=inFileName)
            elif args.syntax == "flow":
                parser = Tome.TomeFlowParser(inStream, debug=args.debug, filename=inFileName)
            else:
                sys.stderr.write("%s: Internal Error: Sorry, unhandled syntax \"%s\".\n" % (prog_name, args.syntax))
                return -1
            tome = parser.tome()

        except Tome.SyntaxError, e:
            sys.stderr.write("%s: Syntax Error: %s\n" % (prog_name, str(e)))
            inClose()
            outClose()
            return errno.EINVAL

        #Done with input file
        inClose()
        inClose = lambda : None


        ############ GENERATE OUTPUT ###########

        if args.format == "xml":
            doc = tome.serializeToDom()
            addindent = "    "
            newl = "\n"
            if args.xml_compact:
                addindent = ""
                newl = ""
            doc.writexml(outStream, indent="", addindent=addindent, newl=newl, encoding="UTF-8")

        elif args.format == "txt":
            writer = writeText.TextWriter(args.line_width)
            writer.writeText(tome, outStream)

        elif args.format == "flow":
            writer = writeFlow.FlowWriter(outStream, args.line_width)
            writer.writeFlow(tome)

        elif args.format == "latex":
            writeLatex.writeLatex(tome, outStream, templateFile=args.template_file, draft=args.draft)

        elif args.format == "epub":

            outClose()
            outClose = lambda : None

            if outFilePath is None:
                sys.stderr.write("%s: Error: Cannot write EPUB to stdout, must explicitely give the OUTPUT argument.\n" % (prog_name))
                return errno.EINVAL

            tdFilter = writeEpub.EpubWriter.getListBasedFilter(
                inc_patterns = args.epub_include,
                exc_patterns = args.epub_exclude,
                excludeFirst = args.epub_exclude_first
            )
            writer = writeEpub.EpubWriter(tome, outFilePath, templateDirectory=args.template_dir, tdFilter=tdFilter)
            writer.writeEpub()

        else:
            sys.stderr.write("%s: Internal Error: Sorry, unhandled format \"%s\".\n" % (prog_name, args.format))
            outClose()
            return -1
            
        outClose()

        return 0

    except Exception, e:
        sys.stderr.write("%s: Error: %s\n" % (prog_name, str(e)))
        inClose()
        outClose()
        if args.debug:
            raise
        return -1



def main_writeTemplateDir(args=sys.argv):
    prog_name = args[0]
    if len(args) < 2:
        sys.stderr.write("%s: Error: Missing required argument, the output path.\n" % prog_name)
        return errno.EINVAL
    opath = args[1]
    writeTemplateDir(opath)

def writeTemplateDir(opath):
    src = pkg_resources.resource_filename("tome", "res/epub-template")
    shutil.copytree(src, opath)


if __name__ == "__main__":
    ret = main()
    if ret is None:
        ret = 0
    sys.exit(ret)
