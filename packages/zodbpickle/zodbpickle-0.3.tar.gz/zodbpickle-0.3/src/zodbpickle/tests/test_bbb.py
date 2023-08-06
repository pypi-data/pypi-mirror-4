import unittest

class ClassicFoo:
    pass

class NewFoo(object):
    pass

class BBBUnpicklerTests(unittest.TestCase):

    def test_python2_classic_instance_dict_protocol_1(self):
        from zodbpickle.pickle import loads
        PICKLE = (b"(izodbpickle.tests.test_bbb"
                  b"\nClassicFoo\np1\n(dp2\nS'bar'\np3\nS'baz'\np4\nsb.")
        foo = loads(PICKLE)
        self.assertTrue(isinstance(foo, ClassicFoo))
        self.assertEqual(list(foo.__dict__), ['bar'])
        self.assertEqual(foo.bar, b'baz')

    def test_python2_newstyle_instance_dict_protocol_1(self):
        from zodbpickle.pickle import loads
        PICKLE = (b"ccopy_reg\n_reconstructor\np1\n"
                  b"(czodbpickle.tests.test_bbb\n"
                  b"NewFoo\np2\nc__builtin__\nobject\np3\nNtRp4\n"
                  b"(dp5\nS'bar'\np6\nS'baz'\np7\nsb.")
        foo = loads(PICKLE)
        self.assertTrue(isinstance(foo, NewFoo))
        self.assertEqual(list(foo.__dict__), ['bar'])
        self.assertEqual(foo.bar, b'baz')
