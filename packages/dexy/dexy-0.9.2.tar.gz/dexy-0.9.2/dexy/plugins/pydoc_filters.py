from dexy.filter import DexyFilter
from idiopidae.runtime import Composer
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.formatters.latex import LatexFormatter
from pygments.lexers.agile import PythonLexer
import idiopidae.parser
import inspect
import json
import pkgutil
import sys

class PythonDocumentationFilter(DexyFilter):
    ALIASES = ["pydoc"]
    INPUT_EXTENSIONS = [".txt"]
    OUTPUT_EXTENSIONS = ['.sqlite3', '.json']
    COMPOSER = Composer()
    OUTPUT_DATA_TYPE = 'keyvalue'
    LEXER = PythonLexer()
    LATEX_FORMATTER = LatexFormatter()
    HTML_FORMATTER = HtmlFormatter(lineanchors="pydoc")

    def fetch_item_content(self, key, item):
        is_method = inspect.ismethod(item)
        is_function = inspect.isfunction(item)
        if is_method or is_function:
            # Get source code
            try:
                source = inspect.getsource(item)
            except IOError:
                source = ""
            # Process any idiopidae tags
            builder = idiopidae.parser.parse('Document', source + "\n\0")

            sections = {}
            for i, s in enumerate(builder.sections):
                sections[s] = "\n".join(l[1] for l in builder.statements[i]['lines'])

            if isinstance(sections, dict):
                if len(sections.keys()) > 1 or sections.keys()[0] != '1':
                    for section_name, section_content in sections.iteritems():
                        self.add_source_for_key("%s:%s" % (key, section_name), section_content)
                else:
                    self.add_source_for_key(key, sections['1'])
            else:
                self.add_source_for_key(key, sections)

            self.output().append("%s:doc" % key, inspect.getdoc(item))
            self.output().append("%s:comments" % key, inspect.getcomments(item))

        else: # not a function or a method
            try:
                # If this can be JSON-serialized, leave it alone...
                json.dumps(item)
                self.add_source_for_key(key, item)
            except TypeError:
                # ... if it can't, convert it to a string to avoid problems.
                self.add_source_for_key(key, str(item))

    def highlight_html(self, source):
        return highlight(source, self.LEXER, self.HTML_FORMATTER)

    def highlight_latex(self, source):
        return highlight(source, self.LEXER, self.LATEX_FORMATTER)

    def add_source_for_key(self, key, source):
        """
        Appends source code + syntax highlighted source code to persistent store.
        """
        self.output().append("%s:value" % key, source)
        if not (type(source) == str or type(source) == unicode):
            source = inspect.getsource(source)
        self.output().append("%s:source" % key, source)
        self.output().append("%s:html-source" % key, self.highlight_html(source))
        self.output().append("%s:latex-source" % key, self.highlight_latex(source))

    def process_members(self, package_name, mod):
        """
        Process all members of the package or module passed.
        """
        name = mod.__name__

        for k, m in inspect.getmembers(mod):
            self.log.debug("in %s processing element %s" % (mod.__name__, k))
            if not inspect.isclass(m) and hasattr(m, '__module__') and m.__module__ and m.__module__.startswith(package_name):
                key = "%s.%s" % (m.__module__, k)
                self.fetch_item_content(key, m)

            elif inspect.isclass(m) and m.__module__.startswith(package_name):
                key = "%s.%s" % (mod.__name__, k)
                try:
                    item_content = inspect.getsource(m)
                    self.output().append("%s:doc" % key, inspect.getdoc(m))
                    self.output().append("%s:comments" % key, inspect.getcomments(m))
                    self.add_source_for_key(key, item_content)
                except IOError:
                    self.log.debug("can't get source for %s" % key)
                    self.add_source_for_key(key, "")

                try:
                    for ck, cm in inspect.getmembers(m):
                        key = "%s.%s.%s" % (name, k, ck)
                        self.fetch_item_content(key, cm)
                except AttributeError:
                    pass

            else:
                key = "%s.%s" % (name, k)
                self.fetch_item_content(key, m)

    def process_module(self, package_name, name):
        try:
            self.log.debug("Trying to import %s" % name)
            __import__(name)
            mod = sys.modules[name]
            self.log.debug("Success importing %s" % name)

            try:
                module_source = inspect.getsource(mod)
                json.dumps(module_source)
                self.add_source_for_key(name, inspect.getsource(mod))
            except (UnicodeDecodeError, IOError, TypeError):
                self.log.debug("Unable to load module source for %s" % name)

            self.process_members(package_name, mod)

        except (ImportError, TypeError) as e:
            self.log.debug(e)

    def process(self):
        """
        input_text should be a list of installed python libraries to document.
        """
        package_names = self.input().as_text().split()
        packages = [__import__(package_name) for package_name in package_names]

        for package in packages:
            self.log.debug("processing package %s" % package)
            package_name = package.__name__
            prefix = package.__name__ + "."

            self.process_members(package_name, package)

            if hasattr(package, '__path__'):
                for module_loader, name, ispkg in pkgutil.walk_packages(package.__path__, prefix=prefix):
                    self.log.debug("in package %s processing module %s" % (package_name, name))
                    if not name.endswith("__main__"):
                        self.process_module(package_name, name)
            else:
                self.process_module(package.__name__, package.__name__)

        self.output().save()
