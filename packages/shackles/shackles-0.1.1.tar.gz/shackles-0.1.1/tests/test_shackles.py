from unittest import TestCase
import shackles

from pytest import raises

class prisoner(object):
    """Dummy object to shackle to for testing"""
    def __init__(self, name=None):
        self.name = name

obj = prisoner()
obj.a = prisoner('a')
obj.a.b = prisoner('b')
obj.a.b.e = prisoner('e')

class test_shackles(TestCase):

    def test_broken_chain_str(self):
        assert shackles.broken(obj, 'e') is 'e'
        assert shackles.broken(obj, 'a.b') is None
        assert shackles.broken(obj, 'a.b.c') == 'c'

    def test_broken_chain_list(self):
        assert shackles.broken(obj, ['e']) is 'e'
        assert shackles.broken(obj, ['a','b']) is None
        assert shackles.broken(obj, ['a','b','c']) == 'c'

    def test_broken_chain_tuple(self):
        assert shackles.broken(obj, ('e')) is 'e'
        assert shackles.broken(obj, ('a','b')) is None
        assert shackles.broken(obj, ('a','b','c')) == 'c'

    def test_get_str(self):
        assert shackles.get(obj, 'a.b').name == 'b'
        assert shackles.get(obj, 'a.b.name') == 'b'

    def test_get_list(self):
        assert shackles.get(obj, ['a','b']).name == 'b'
        assert shackles.get(obj, ['a','b','name']) == 'b'

    def test_get_tuple(self):
        assert shackles.get(obj, ('a','b')).name == 'b'
        assert shackles.get(obj, ('a','b','name')) == 'b'

    def test_get_default(self):
        assert shackles.get(obj, 'e', True) == True

    def test_get_raises_attribute_error(self):
        with raises(AttributeError):
            shackles.get(obj, 'e')

    def test_get_raises_type_error(self):
        with raises(TypeError):
            shackles.get(obj, 'e', 1, 2)

        with raises(TypeError):
            shackles.get(obj, 'e', default=1)

    def test_walk_next(self):
        assert next(shackles.walk(obj, 'a')).name == 'a'

    def test_walk_iter(self):
        names=['a','b','e']
        for i, attr in enumerate(shackles.walk(obj, 'a.b.e')):
            assert names[i] == attr.name

    def test_walk_raises_type_error(self):
        with raises(AttributeError):
            assert next(shackles.walk(obj, 'e'))

    def test_has_str(self):
        assert shackles.has(obj, 'a.b') == True
        assert shackles.has(obj, 'a.b.name') == True

    def test_has_list(self):
        assert shackles.has(obj, ['a','b']) == True
        assert shackles.has(obj, ['a','b','name']) == True

    def test_has_tuple(self):
        assert shackles.has(obj, ('a','b')) == True
        assert shackles.has(obj, ('a','b','name')) == True

    def test_has_false(self):
        assert shackles.has(obj, 'e.b') == False

    def test_get_str(self):
        assert shackles.attrgetter('a.b')(obj).name == 'b'
        assert shackles.attrgetter('a.b.name')(obj) == 'b'

    def test_get_list(self):
        assert shackles.attrgetter(['a','b'])(obj).name == 'b'
        assert shackles.attrgetter(['a','b','name'])(obj) == 'b'

    def test_get_tuple(self):
        assert shackles.attrgetter(('a','b'))(obj).name == 'b'
        assert shackles.attrgetter(('a','b','name'))(obj) == 'b'

    def test_get_default(self):
        assert shackles.attrgetter('e', True)(obj) == True
