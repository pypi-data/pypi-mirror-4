from dexy.doc import Doc
from dexy.plugins.process_filters import SubprocessFilter
from dexy.tests.utils import wrap
import dexy.exceptions
import os

def test_walk_working_dir():
    with wrap() as wrapper:
        doc = Doc("example.sh|sh",
                contents = "echo 'hello' > newfile.txt",
                sh = {
                    "walk-working-dir" : True,
                    },
                wrapper=wrapper)

        wrapper.run_docs(doc)

        for doc in wrapper.registered_docs():
            if doc.key_with_class() == "Doc:example.sh-sh.txt-files":
                assert doc.output().as_sectioned()['newfile.txt'] == "hello" + os.linesep

def test_add_new_files():
    with wrap() as wrapper:
        doc = Doc("example.sh|sh",
                contents = "echo 'hello' > newfile.txt",
                sh = {
                    "add-new-files" : True,
                    "additional-doc-filters" : { '.txt' : 'markdown' }
                    },
                wrapper=wrapper)

        wrapper.run_docs(doc)

        assert wrapper.registered_docs()[1].key == 'newfile.txt'
        assert wrapper.registered_docs()[1].output().data() == "hello" + os.linesep

        assert wrapper.registered_docs()[2].key == 'newfile.txt|markdown'
        assert wrapper.registered_docs()[2].output().data() == "<p>hello</p>"

def test_not_present_executable():
    assert 'notreal' in NotPresentExecutable.executables()
    assert not NotPresentExecutable.executable()

class NotPresentExecutable(SubprocessFilter):
    EXECUTABLE = 'notreal'

def test_command_line_args():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"args" : "-B"},
                wrapper=wrapper,
                contents="print 'hello'"
                )
        wrapper.run_docs(doc)

        assert doc.output().data() == "hello" + os.linesep

        command_used = doc.artifacts[-1].filter_instance.command_string()
        assert command_used == "python -B example.py  example.txt"

def test_scriptargs():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"scriptargs" : "--foo"},
                wrapper=wrapper,
                contents="import sys\nprint sys.argv[1]"
                )
        wrapper.run_docs(doc)

        assert doc.output().data() == "--foo" + os.linesep

        command_used = doc.artifacts[-1].filter_instance.command_string()
        assert command_used == "python  example.py --foo example.txt"

def test_custom_env_in_args():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                py={"env" : {"FOO" : "bar" }},
                wrapper=wrapper,
                contents="import os\nprint os.environ['FOO']"
                )
        wrapper.run_docs(doc)

        assert doc.output().data() == "bar" + os.linesep

def test_nonzero_exit():
    with wrap() as wrapper:
        doc = Doc("example.py|py",
                wrapper=wrapper,
                contents="import sys\nsys.exit(1)"
                )
        try:
            wrapper.run_docs(doc)
            assert False, "should raise NonzeroExit"
        except dexy.exceptions.NonzeroExit:
            assert True

def test_ignore_nonzero_exit():
    with wrap() as wrapper:
        wrapper.ignore_nonzero_exit = True
        doc = Doc("example.py|py",
                wrapper=wrapper,
                contents="import sys\nsys.exit(1)"
                )
        wrapper.run_docs(doc)
        assert True # no NonzeroExit was raised...
