from dexy.exceptions import UnexpectedState, InvalidStateTransition, CircularDependency
from dexy.tests.utils import divert_stdout
from dexy.tests.utils import wrap
from nose.tools import raises
import dexy.task

def test_init():
    task = dexy.task.Task("key")
    assert isinstance(task.args, dict)
    assert isinstance(task.children, list)
    assert task.key == "key"

    assert hasattr(task, 'pre')
    assert hasattr(task, 'post')
    assert hasattr(task.pre, "__call__")
    assert hasattr(task.post, "__call__")

def test_kwargs():
    task = dexy.task.Task("key", foo="bar", abc="def")
    assert task.args['foo'] == 'bar'
    assert task.args['abc'] == 'def'

@raises(UnexpectedState)
def test_invalid_state():
    task = dexy.task.Task("key")
    task.state = "invalid"
    for t in task:
        t()

@raises(InvalidStateTransition)
def test_invalid_transition():
    task = dexy.task.Task('key')
    task.transition('complete')

def test_set_log():
    task = dexy.task.Task("key")
    assert not hasattr(task, 'log')
    task.set_log()
    assert hasattr(task, 'log')
    assert hasattr(task, 'logstream')
    task.log.debug("please write me to log")
    assert "please write me to log" in task.logstream.getvalue()

def test_circular():
    with wrap() as wrapper:
        wrapper.setup_batch()

        d1 = dexy.task.Task("1",wrapper=wrapper)
        d2 = dexy.task.Task("2",wrapper=wrapper)

        d1.children.append(d2)
        d2.children.append(d1)

        try:
            for t in d1:
                t()
            assert False
        except CircularDependency:
            assert True

@raises(CircularDependency)
def test_circular_4_docs():
    with wrap() as wrapper:
        wrapper.setup_batch()

        d1 = dexy.task.Task("1", wrapper=wrapper)
        d2 = dexy.task.Task("2", wrapper=wrapper)
        d3 = dexy.task.Task("3", wrapper=wrapper)
        d4 = dexy.task.Task("4", wrapper=wrapper)

        d1.children.append(d2)
        d2.children.append(d3)
        d3.children.append(d4)
        d4.children.append(d1)

        for t in d1:
            t()

class SubclassTask(dexy.task.Task):
    """
    for testing
    """
    def pre(self, *args, **kw):
        print "pre '%s'" % self.key,

    def run(self, *args, **kw):
        print "run '%s'" % self.key,

    def post(self, *args, **kw):
        print "post '%s'" % self.key,

def test_run_demo_single():
    with divert_stdout() as stdout:
        with wrap() as wrapper:
            doc = SubclassTask("demo", wrapper=wrapper)

            wrapper.run_docs(doc)

            assert "pre 'demo' run 'demo' post 'demo'" == stdout.getvalue()

def test_run_demo_parent_child():
    with divert_stdout() as stdout:
        with wrap() as wrapper:
            doc = SubclassTask(
                        "parent",
                        SubclassTask("child", wrapper=wrapper),
                        wrapper=wrapper
                    )

            wrapper.run_docs(doc)

        assert "pre 'parent' pre 'child' run 'child' post 'child' run 'parent' post 'parent'" == stdout.getvalue()

def test_dependencies_only_run_once():
    with divert_stdout() as stdout:
        with wrap() as wrapper:
            t1 = SubclassTask("1", wrapper=wrapper)
            t2 = SubclassTask("2", t1, wrapper=wrapper)
            t3 = SubclassTask("3", t1, wrapper=wrapper)

            wrapper.run_docs(t1, t2, t3)

            assert stdout.getvalue() == "pre '1' run '1' post '1' pre '2' run '2' post '2' pre '3' run '3' post '3'"

            assert len(t1.deps) == 0
            assert t1 in t2.deps.values()
            assert t1 in t3.deps.values()

def test_completed_children():
    with wrap() as wrapper:
        with divert_stdout() as stdout:
            grandchild_task = SubclassTask("grandchild", wrapper=wrapper)
            child_task = SubclassTask("child", grandchild_task, wrapper=wrapper)
            parent_task = SubclassTask("parent", child_task, wrapper=wrapper)

            wrapper.run_docs(parent_task)

            assert stdout.getvalue() == "pre 'parent' pre 'child' pre 'grandchild' run 'grandchild' post 'grandchild' run 'child' post 'child' run 'parent' post 'parent'"

    assert "SubclassTask:grandchild" in parent_task.deps.keys()
    assert "SubclassTask:child" in parent_task.deps.keys()

    assert "SubclassTask:grandchild" in child_task.deps.keys()

    assert len(grandchild_task.deps) == 0
