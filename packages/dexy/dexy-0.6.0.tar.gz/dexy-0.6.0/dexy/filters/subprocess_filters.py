from dexy.dexy_filter import DexyFilter
from dexy.filters.process_filters import SubprocessFilter
import codecs
import dexy.commands
import dexy.utils
import os
import re
import shutil
import subprocess

class BlackWhitePdfFilter(SubprocessFilter):
    EXECUTABLE = "gs"
    ALIASES = ['bw', 'bwconv']
    INPUT_EXTENSIONS = [".pdf"]
    OUTPUT_EXTENSIONS = [".pdf"]

    def command_string(self):
        s = "%(prog)s -dSAFER -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sColorConversionStrategy=Gray -dProcessColorModel=/DeviceGray -sOutputFile=%(out)s %(in)s"
        args = {
            'prog' : self.executable(),
            'in' : self.artifact.previous_artifact_filename,
            'out' : self.artifact.filename()
        }
        return s % args

    def setup_cwd(self):
        return self.artifact.artifacts_dir

class PandocFilter(SubprocessFilter):
    EXECUTABLE = "pandoc"
    VERSION_COMMAND = "pandoc --version"
    ALIASES = ['pandoc']
    OUTPUT_EXTENSIONS = ['.html', '.txt', '.tex', '.pdf', '.rtf', '.json', '.docx']
    BINARY = None # determine binary from file extension

    def command_string(self):
        args = {
            'prog' : self.executable(),
            'args' : self.command_line_args() or "",
            'script_file' : os.path.basename(self.artifact.previous_canonical_filename),
            'output_file' : self.artifact.canonical_basename()
        }
        return "%(prog)s %(args)s %(script_file)s -o %(output_file)s" % args

class EspeakFilter(SubprocessFilter):
    EXECUTABLE = "espeak"
    INPUT_EXTENSIONS = [".txt"]
    OUTPUT_EXTENSIONS = [".wav"]
    ALIASES = ['espeak']
    BINARY = True

    def command_string(self):
        args = {
            'prog' : self.executable(),
            'args' : self.command_line_args() or "",
            'scriptargs' : self.command_line_scriptargs() or "",
            'script_file' : os.path.basename(self.artifact.previous_artifact_filename),
            'output_file' : self.artifact.canonical_basename()
        }
        return "%(prog)s %(args)s -w %(output_file)s %(script_file)s" % args

class AsciidocFilter(SubprocessFilter):
    VERSION_COMMAND = "asciidoc --version"
    EXECUTABLE = "asciidoc"
    INPUT_EXTENSIONS = [".txt"]
    OUTPUT_EXTENSIONS = [".html", ".xml"]
    ALIASES = ['asciidoc']
    BINARY = False

    def command_string(self):
        if self.args().has_key('backend'):
            backend = self.arg_value('backend')
            # TODO check file extension is valid for backend
        else:
            if self.artifact.ext == ".html":
                if self.version() >= "asciidoc 8.6.5":
                    backend = 'html5'
                else:
                    backend = 'html4'
            elif self.artifact.ext == ".xml":
                backend = "docbook45"
            elif self.artifact.ext == ".tex":
                backend = "latex"
            else:
                raise Exception("unexpected file extension in asciidoc filter %s" % self.artifact.ext)

        args = {
            'backend' : backend,
            'infile' : os.path.basename(self.artifact.previous_canonical_filename),
            'outfile' : self.artifact.canonical_basename(),
            'prog' : self.executable(),
            'args' : self.command_line_args() or ""
        }

        return "%(prog)s -b %(backend)s %(args)s -o %(outfile)s %(infile)s" % args

class HtLatexFilter(SubprocessFilter):
    """
    Generates HTML from LaTeX source.
    """
    INPUT_EXTENSIONS = [".tex", ".txt"]
    OUTPUT_EXTENSIONS = [".html"]
    EXECUTABLES = ['htlatex']
    ALIASES = ['htlatex']
    FINAL = True

    def process(self):
        cwd = self.setup_cwd()
        wf = os.path.join(cwd, os.path.basename(self.artifact.name))

        f = open(wf, "w")
        f.write(self.artifact.input_text())
        f.close()

        if self.artifact.args.has_key('htlatex'):
            htlatex_args = self.artifact.args['htlatex']
        else:
            htlatex_args = ""


        command = "%s %s %s" % (self.__class__.executable(), os.path.basename(self.artifact.name), htlatex_args)
        self.log.debug("running '%s' in '%s'" % (command, cwd))
        env = None
        proc = subprocess.Popen(command, shell=True,
                                cwd=cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                env=env)
        stdout, stderr = proc.communicate()
        self.artifact.stdout = stdout
        self.log.debug("Finished running. Output is %s" % stdout)

        html_filename = wf.replace(".tex", ".html")

        # The main HTML file generated.
        f = open(html_filename, "r")
        self.artifact.set_data(f.read())
        f.close()

        for f in os.listdir(self.artifact.temp_dir()):
            basefilepath = os.path.dirname(self.artifact.name)
            f_ext = os.path.splitext(f)[1]

            # handle text-based output
            if (f_ext in [".css", ".html"]) and f != self.artifact.name.replace(".tex", ".html"):
                f_key = os.path.join(basefilepath, f)
                new_artifact = self.artifact.add_additional_artifact(f_key, f_ext)
                with open(os.path.join(self.artifact.temp_dir(), f), "r") as generated_file:
                    new_artifact.set_data(generated_file.read())

            # handle binary output
            if f_ext in [".png"]:
                f_key = os.path.join(basefilepath, f)
                new_artifact = self.artifact.add_additional_artifact(f_key, f_ext)
                shutil.copyfile(os.path.join(self.artifact.temp_dir(), f), new_artifact.filepath())

class LatexFilter(SubprocessFilter):
    """
    Generates a PDF file from LaTeX source.
    """
    INPUT_EXTENSIONS = [".tex", ".txt"]
    OUTPUT_EXTENSIONS = [".pdf", ".png"]
    EXECUTABLES = ['pdflatex', 'latex']
    ALIASES = ['latex']
    BINARY = True
    FINAL = True

    def process(self):
        cwd = self.setup_cwd()
        env = self.setup_env()

        latex_command = "%s -interaction=batchmode %s" % (self.executable(), os.path.basename(self.artifact.previous_canonical_filename))

        bibtex_command = None
        if dexy.utils.command_exists("bibtex"):
            bibtex_command = "bibtex %s" % os.path.splitext(self.artifact.canonical_basename())[0]

        self.artifact.stdout = ""

        def run_cmd(command):
            self.log.info("running %s in %s" % (command, cwd))
            proc = subprocess.Popen(command, shell=True,
                                    cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=env)

            stdout, stderr = proc.communicate()
            self.artifact.stdout += stdout

            if proc.returncode > 2: # Set at 2 for now as this is highest I've hit, better to detect whether PDF has been generated?
                raise dexy.commands.UserFeedback("latex error, look for information in %s" % cwd)
            elif proc.returncode > 0:
                self.log.warn("""A non-critical latex error has occurred running %s,
                status code returned was %s, look for information in %s""" % (
                self.artifact.key, proc.returncode, cwd))

        if bibtex_command:
            run_cmd(latex_command) #generate aux
            run_cmd(bibtex_command) #generate bbl
        run_cmd(latex_command) #first run
        run_cmd(latex_command) #second run - fix references

        self.copy_canonical_file()

class TikzPgfFilter(LatexFilter):
    """
    Takes a snippet of Tikz code, wraps it in a LaTeX document, and renders it to PDF.
    """
    ALIASES = ['tikz']

    def process(self):
        latex_filename = self.artifact.filename().replace(self.artifact.ext, ".tex")
        # TODO allow setting tikz libraries per-document, or just include all of them?
        # TODO how to create a page size that just includes the content
        latex_header = """\documentclass[tikz]{standalone}
\usetikzlibrary{shapes.multipart}
\\begin{document}
        """
        latex_footer = "\n\end{document}"

        work_path = os.path.join(self.artifact.artifacts_dir, latex_filename)
        with codecs.open(work_path, "w", encoding="utf-8") as f:
            f.write(latex_header)
            f.write(self.artifact.input_text())
            f.write(latex_footer)

        latex_command = "%s -interaction=batchmode %s" % (self.__class__.executable(), latex_filename)

        self.artifact.stdout = ""

        def run_cmd(command):
            self.log.info("running: %s" % command)
            proc = subprocess.Popen(command, shell=True,
                                    cwd=self.artifact.artifacts_dir,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=self.setup_env())

            stdout, stderr = proc.communicate()
            self.artifact.stdout += stdout
            if proc.returncode > 2: # Set at 2 for now as this is highest I've hit, better to detect whether PDF has been generated?
                raise Exception("latex error, look for information in %s" %
                                latex_filename.replace(".tex", ".log"))
            elif proc.returncode > 0:
                self.log.warn("""A non-critical latex error has occurred running %s,
                status code returned was %s, look for information in %s""" % (
                self.artifact.key, proc.returncode,
                latex_filename.replace(".tex", ".log")))

        run_cmd(latex_command) #first run

class EmbedFonts(SubprocessFilter):
    """
    Use to embed fonts and do other prepress as required for some types of printing.
    """
    INPUT_EXTENSIONS = [".pdf"]
    OUTPUT_EXTENSIONS = [".pdf"]
    EXECUTABLE = 'ps2pdf'
    ALIASES = ['embedfonts', 'prepress']

    def preprocess_command_string(self):
        pf = os.path.basename(self.artifact.previous_canonical_filename)
        af = self.artifact.filename()
        return "%s -dPDFSETTINGS=/prepress %s %s" % (self.EXECUTABLE, pf, af)

    def pdffonts_command_string(self):
        return "%s %s" % ("pdffonts", self.artifact.filename())

    def process(self):
        env = self.setup_env()

        command = self.preprocess_command_string()
        proc, stdout = self.run_command(command, env)
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)
        self.artifact.stdout = stdout

        command = self.pdffonts_command_string()
        proc, stdout = self.run_command(command, env)
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)
        self.artifact.stdout += stdout

class ROutputBatchFilter(SubprocessFilter):
    """Runs R code in batch mode. Uses the --slave flag so doesn't echo commands, just returns output."""
    ALIASES = ['rout', 'routbatch']
    EXECUTABLE = 'R CMD BATCH --vanilla --quiet --slave --no-timing'
    INPUT_EXTENSIONS = ['.txt', '.r', '.R']
    OUTPUT_EXTENSIONS = [".txt"]
    VERSION_COMMAND = "R --version"
    BINARY = False
    FINAL = False

class RBatchFilter(SubprocessFilter):
    """Runs R code in batch mode."""
    ALIASES = ['rintbatch']
    EXECUTABLE = 'R CMD BATCH --quiet --no-timing'
    INPUT_EXTENSIONS = ['.txt', '.r', '.R']
    OUTPUT_EXTENSIONS = [".Rout", '.txt']
    VERSION_COMMAND = "R --version"
    BINARY = False
    FINAL = False

class Rd2PdfFilter(SubprocessFilter):
    INPUT_EXTENSIONS = [".Rd"]
    OUTPUT_EXTENSIONS = [".pdf", ".dvi"]
    EXECUTABLE = 'R CMD Rd2pdf'
    VERSION_COMMAND = 'R CMD Rd2pdf -v'
    ALIASES = ['rd2pdf', 'Rd2pdf']

    def command_string(self):
        title = os.path.splitext(self.artifact.name)[0].replace("_", " ")
        args = {
            'prog' : self.executable(),
            'out' : self.artifact.filename(),
            'in' : self.artifact.previous_artifact_filename,
            'title' : title
        }
        return "%(prog)s --output=%(out)s --title=\"%(title)s\" %(in)s" % args

class RagelRubySubprocessFilter(SubprocessFilter):
    """
    Generates ruby source code from a ragel file.
    """
    ALIASES = ['rlrb', 'ragelruby']
    BINARY = False
    EXECUTABLE = 'ragel -R'
    FINAL = False
    INPUT_EXTENSIONS = [".rl"]
    OUTPUT_EXTENSIONS = [".rb"]
    VERSION_COMMAND = 'ragel --version'

    def command_string(self):
        wf = os.path.basename(self.artifact.previous_canonical_filename)
        of = self.artifact.canonical_basename()
        return "%s %s -o %s" % (self.executable(), wf, of)

class Ps2PdfSubprocessFilter(SubprocessFilter):
    """
    Converts a postscript file to PDF format.
    """
    ALIASES = ['ps2pdf']
    EXECUTABLE = 'ps2pdf'
    INPUT_EXTENSIONS = [".ps", ".txt"]
    OUTPUT_EXTENSIONS = [".pdf"]

class Html2PdfSubprocessFilter(SubprocessFilter):
    """
    Renders HTML to PDF using wkhtmltopdf. If the HTML relies on assets such as
    CSS or image files, these should be specified as inputs.

    If you have an older version of wkhtmltopdf, and are running on a server,
    you may get XServer errors. You can install xvfb and run Dexy as
    "xvfb-run dexy". Or upgrade to the most recent wkhtmltopdf which only needs
    X11 client libs.
    """
    ALIASES = ['html2pdf', 'wkhtmltopdf']
    EXECUTABLE = 'wkhtmltopdf'
    INPUT_EXTENSIONS = [".html", ".txt"]
    OUTPUT_EXTENSIONS = [".pdf"]
    VERSION_COMMAND = 'wkhtmltopdf --version'

    def command_string(self):
        args = {
            'prog' : self.executable(),
            'in' : os.path.basename(self.artifact.previous_canonical_filename),
            'out' : self.artifact.filename()
        }
        return "%(prog)s %(in)s %(out)s" % args

class DotFilter(SubprocessFilter):
    """
    Renders .dot files to either PNG or PDF images.
    """
    INPUT_EXTENSIONS = [".dot"]
    OUTPUT_EXTENSIONS = [".png", ".pdf"]
    EXECUTABLE = 'dot'
    VERSION_COMMAND = 'dot -V'
    ALIASES = ['dot', 'graphviz']

    def command_string(self):
        args = {
            'prog' : self.executable(),
            'format' : self.artifact.ext.replace(".",""),
            'workfile' : os.path.basename(self.artifact.previous_canonical_filename),
            'outfile' : self.artifact.canonical_basename()
        }
        return "%(prog)s -T%(format)s -o%(outfile)s %(workfile)s" % args

class Pdf2ImgSubprocessFilter(SubprocessFilter):
    """
    Converts a PDF file to a PNG image using ghostscript (subclass this to
    convert to other image types).

    Returns the image generated by page 1 of the PDF by default, the optional
    'page' parameter can be used to specify other pages.
    """
    ALIASES = ['pdf2img', 'pdf2png']
    EXECUTABLE = "gs"
    GS_DEVICE = 'png16m -r300'
    INPUT_EXTENSIONS = ['.pdf']
    OUTPUT_EXTENSIONS = ['.png']
    VERSION_COMMAND = "gs --version"

    def command_string(self):
        s = "%(prog)s -dSAFER -dNOPAUSE -dBATCH -sDEVICE=%(device)s -sOutputFile=%%d-%(out)s %(in)s"
        args = {
            'prog' : self.executable(),
            'device' : self.GS_DEVICE,
            'in' : os.path.basename(self.artifact.previous_canonical_filename),
            'out' : self.artifact.filename()
        }
        return s % args

    def process(self):
        command = self.command_string()
        proc, stdout = self.run_command(command, self.setup_env())
        self.artifact.stdout = stdout
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)

        if self.artifact.args.has_key('page'):
            page = self.artifact.args['page']
        else:
            page = 1

        page_file = os.path.join(self.artifact.temp_dir(), os.path.dirname(self.artifact.canonical_filename()), "%s-%s" % (page, self.artifact.filename()))
        print page_file
        shutil.copyfile(page_file, self.artifact.filepath())

class Pdf2JpgSubprocessFilter(Pdf2ImgSubprocessFilter):
    ALIASES = ['pdf2jpg']
    GS_DEVICE = 'jpeg'
    OUTPUT_EXTENSIONS = ['.jpg']

class FortranFilter(SubprocessFilter):
    ALIASES = ['fortran']
    EXECUTABLE = 'gfortran-4.6'
    VERSION_COMMAND = 'gfortran-4.6 --version'
    INPUT_EXTENSIONS = ['.f']
    OUTPUT_EXTENSIONS = ['.exe']
    BINARY = True

    def command_string(self):
        args = {
                'prog' : self.executable(),
                'args' : self.command_line_args() or "",
                'script_file' : self.artifact.previous_artifact_filename,
                'output_file' : self.artifact.filename()
                }
        return "%(prog)s %(args)s %(script_file)s -o %(output_file)s" % args
