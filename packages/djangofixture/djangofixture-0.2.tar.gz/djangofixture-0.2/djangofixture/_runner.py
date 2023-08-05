from django.test import TestCase as DjangoTestCase

from testtools import RunTest


class DjangoRunner(RunTest):
    """Use with run_tests_with to run Django tests.

    Django's test case has a couple of hooks that it runs before and after
    tests to isolate transactions and do other fun things
    <https://docs.djangoproject.com/en/dev/topics/testing/#django.test.TestCase>.

    Use this runner to get that same effect with testtools.
    """

    class MyDjangoTestCase(DjangoTestCase):
        def test_foo(self):
            pass

    def __init__(self, case, handlers=None):
        super(DjangoRunner, self).__init__(case, handlers=handlers)
        self._django_case = self.MyDjangoTestCase('test_foo')

    def _run_core(self):
        self._run_user(self._django_case._pre_setup)
        super(DjangoRunner, self)._run_core()
        self._run_user(self._django_case._post_teardown)


