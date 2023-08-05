from dexy.filters.process_filters import SubprocessFilter
from dexy.filters.process_filters import SubprocessStdoutFilter
from ordereddict import OrderedDict
import json
import os
import re
import shutil

class CasperJsSvg2PdfFilter(SubprocessFilter):
    """
    Converts an SVG file to PDF by running it through casper js.
    # TODO convert this to phantomjs, no benefit to using casper here (js is not user facing) and more restrictive
    """
    ALIASES = ['svg2pdf']
    EXECUTABLE = 'casperjs'
    INPUT_EXTENSIONS = ['.svg']
    OUTPUT_EXTENSIONS = ['.pdf']
    VERSION_COMMAND = 'casperjs --version'

    def script_js(self, width, height):
        svgfile = os.path.basename(self.artifact.previous_canonical_filename)
        pdffile = self.artifact.canonical_basename()
        return """
        var casper = require('casper').create({
             viewportSize : {width : %(width)s, height : %(height)s}
        });
        casper.start('%(svgfile)s', function() {
            this.capture('%(pdffile)s');
        });

        casper.run();
        """ % locals()

    def process(self):
        width = self.args().get('width', 200)
        height = self.args().get('height', 200)
        js = self.script_js(width, height)

        script_name = "script.js"
        workfile_path = os.path.join(self.setup_cwd(), script_name)
        with open(workfile_path, "w") as f:
            f.write(js)

        command = "%s %s" % (self.executable(), script_name)
        proc, stdout = self.run_command(command, self.setup_env())
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)
        self.copy_canonical_file()

class CasperJsStdoutFilter(SubprocessStdoutFilter):
    """
    Runs scripts using casper js. Saves cookies.
    """
    ALIASES = ['casperjs']
    EXECUTABLE = 'casperjs'
    INPUT_EXTENSIONS = ['.js', '.txt']
    OUTPUT_EXTENSIONS = ['.txt']
    VERSION_COMMAND = 'casperjs --version'

    def command_string_stdout(self, cookies):
        args = {
            'cookie_file' : cookies.filename(),
            'prog' : self.executable(),
            'args' : self.command_line_args() or "",
            'scriptargs' : self.command_line_scriptargs() or "",
            'script_file' : os.path.basename(self.artifact.previous_canonical_filename)
        }
        return "%(prog)s --cookies-file=%(cookie_file)s %(args)s %(script_file)s %(scriptargs)s" % args

    def process(self):
        dirname = os.path.dirname(self.artifact.canonical_filename())
        cookies = self.artifact.add_additional_artifact(os.path.join(dirname, "cookies.txt"))

        command = self.command_string_stdout(cookies)
        proc, stdout = self.run_command(command, self.setup_env())
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)
        self.artifact.set_data(stdout)

        cookie_generated_file = os.path.join(self.setup_cwd(), cookies.filename())
        if not os.path.exists(cookie_generated_file):
            self.log.debug("No cookie file created, making a blank one.")
            self.log.debug(cookie_generated_file)
            with open(cookie_generated_file, "wb") as f:
                pass

        self.copy_additional_inputs()

class PhantomJsStdoutFilter(SubprocessStdoutFilter):
    """
    Runs scripts using phantom js.
    """
    ALIASES = ['phantomjs']
    EXECUTABLE = 'phantomjs'
    INPUT_EXTENSIONS = ['.js', '.txt']
    OUTPUT_EXTENSIONS = ['.txt']
    VERSION_COMMAND = 'phantomjs --version'
    # TODO ensure phantom.exit() is called in script?

class PhantomJsRenderSubprocessFilter(SubprocessFilter):
    """
    Renders HTML to PNG/PDF using phantom.js. If the HTML relies on local
    assets such as CSS or image files, these should be specified as inputs.
    """
    ALIASES = ['phrender']
    EXECUTABLE = 'phantomjs'
    INPUT_EXTENSIONS = [".html", ".txt"]
    OUTPUT_EXTENSIONS = [".png", ".pdf"]
    VERSION_COMMAND = 'phantomjs --version'
    DEFAULT_WIDTH = 1024
    DEFAULT_HEIGHT = 768

    def setup_cwd(self):
        return os.path.join(self.artifact.artifacts_dir, self.artifact.hashstring)

    def process(self):
        self.artifact.create_temp_dir(populate=True)
        width = self.arg_value('width', self.DEFAULT_WIDTH)
        height = self.arg_value('height', self.DEFAULT_HEIGHT)

        timeout = self.setup_timeout()
        if not timeout:
            timeout = 200

        args = {
                'address' : self.artifact.previous_canonical_filename,
                'output' : os.path.join("..", self.artifact.filename()),
                'width' : width,
                'height' : height,
                'timeout' : timeout
                }

        js = """
        address = '%(address)s'
        output = '%(output)s'
        var page = new WebPage(),
            address, output, size;

        page.viewportSize = { width: %(width)s, height: %(height)s };
        page.open(address, function (status) {
            if (status !== 'success') {
                console.log('Unable to load the address!');
            } else {
                window.setTimeout(function () {
                page.render(output);
                phantom.exit();
                }, %(timeout)s);
            }
        });
        """ % args

        scriptfile = os.path.join(self.artifact.artifacts_dir, self.artifact.hashstring, "phantomscript.js")
        self.log.debug("scriptfile: %s" % scriptfile)
        with open(scriptfile, "w") as f:
            f.write(js)

        command = "phantomjs phantomscript.js"
        self.log.debug(js)
        proc, stdout = self.run_command(command, self.setup_env())
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)
        self.artifact.stdout = stdout

class PhantomJsRenderJavascriptInteractiveFilter(SubprocessFilter):
    """
    Filter which runs javascript on a web page and screenshots the result.
    """
    ALIASES = ['phsecshot']
    DEFAULT_IMAGE_EXT = '.png'
    EXECUTABLE = 'phantomjs'
    INPUT_EXTENSIONS = ['.js', '.txt']
    OUTPUT_EXTENSIONS = ['.json']
    VERSION_COMMAND = 'phantomjs --version'
    BINARY = False
    DEFAULT_WIDTH = 1024
    DEFAULT_HEIGHT = 768

    def setup_cwd(self):
        adir = self.artifact.artifacts_dir
        wdir = self.artifact.hashstring
        relpath = os.path.dirname(self.artifact.name)
        return os.path.join(adir, wdir, relpath)

    def image_ext(self):
        """
        What format screenshot? Defaults to DEFAULT_IMAGE_EXT, can be overridden.
        """
        if self.arg_value('image-ext'):
            ext = self.arg_value('image-ext')
            if not ext.startswith('.'):
                raise Exception("Please start your file extension with a .")
            return ext
        else:
            return self.DEFAULT_IMAGE_EXT

    def new_image_artifact_key(self, section_name):
        file_prefix = os.path.splitext(self.artifact.name)[0]
        ext = self.image_ext()
        key = "%s--%s-screenshot%s" % (file_prefix, section_name, ext)
        return key

    def new_image_artifact(self, section_name):
        key = self.new_image_artifact_key(section_name)
        ext = self.image_ext()
        self.log.debug("Creating new artifact with key %s and ext %s" % (key, ext))
        return self.artifact.add_additional_artifact(key, ext)

    def script_js(self, url, data_dict):
        """
        Construct the javascript which will actually be run by phantomjs.
        """
        page_screenshot_artifact = self.new_image_artifact('initial')

        width = self.arg_value('width', self.DEFAULT_WIDTH)
        height = self.arg_value('height', self.DEFAULT_HEIGHT)

        page_fn = page_screenshot_artifact.filename()
        js = """
        var fs = require('fs');
        var page = new WebPage();

        var consoleObject = {};

        page.onConsoleMessage = function (msg) {
           consoleObject[sectionName] += ("" + msg + "\\n");
        };

        page.viewportSize = { width: %(width)s, height: %(height)s };
        page.open("%(url)s", function (status) {
                page.render("%(page_fn)s");
        """ % {'url' : url, 'page_fn' : page_fn, 'width' : width, 'height' : height }

        for section_name, code in data_dict.iteritems():
            if code and not re.match("^\s*$", code):
                page_screenshot_artifact = self.new_image_artifact(section_name)
                page_fn = page_screenshot_artifact.filename()
                js += """
                sectionName = "%(section_name)s";
                consoleObject[sectionName] = "";

                page.evaluate(function () {
                    %(code)s
                });
                page.render("%(page_fn)s");
                """ % locals()

        js += """
            var info_file = fs.open("%s", "w");
            info_file.write(JSON.stringify(consoleObject));
            info_file.close();

            phantom.exit();
        });
        """ % self.artifact.canonical_basename()

        return js

    def process(self):
        self.artifact.create_temp_dir(populate=True)

        if self.arg_value('url'):
            js = self.script_js(self.arg_value('url'), self.artifact.input_data_dict)
        elif self.arg_value('filename'):
            js = self.script_js(self.arg_value('filename'), self.artifact.input_data_dict)
        elif False:
            # TODO if there is only 1 input with HTML extension, use that.
            pass
        else:
            raise Exception("You must specify either the url of a web page or local filename of an input file.")

        script_name = "script.js"
        workfile_path = os.path.join(self.setup_cwd(), script_name)
        with open(workfile_path, "w") as f:
            f.write(js)

        command = "phantomjs %s" % script_name
        proc, stdout = self.run_command(command, self.setup_env())
        self.handle_subprocess_proc_return(command, proc.returncode, stdout)

        # Collect any artifacts which were generated in the tempdir, that need
        # to be moved to their final locations.
        for i in self.artifact.inputs().values():
            src = os.path.join(self.setup_cwd(), i.filename())
            if (i.virtual or i.additional) and os.path.exists(src):
                self.log.debug("Copying %s to %s (%s)" % (src, i.filepath(), i.key))
                shutil.copy(src, i.filepath())

        self.copy_canonical_file()
