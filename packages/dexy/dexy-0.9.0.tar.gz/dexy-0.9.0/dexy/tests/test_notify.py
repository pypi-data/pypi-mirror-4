from dexy.notify import Notify
from dexy.tests.utils import wrap

class Subscriber(object):
    def call_me(self, args):
        print "I received call_me with %s" % args

def test_notify():
    with wrap() as wrapper:
        notifier = Notify(wrapper)
        obj = Subscriber()
        notifier.subscribe("foo", obj.call_me)
        notifier.notify("foo", "bar")
