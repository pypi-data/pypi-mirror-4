from __future__ import with_statement

import collections
try:
    import abc
except ImportError:
    abc = None

from pytest import raises, skip

from typequery import GenericMethod


class a(object):
    def __repr__(self):
        return '<' + type(self).__name__ + ' object>'
class b(a): pass
class c(b): pass
class d(b): pass
class e(c, d): pass
class f(c, d): pass


if abc is not None:
    class map_(collections.Mapping):
        def __getitem__(self, x):
            raise KeyError(x)
        def __contains__(self, x):
            return False
        def __iter__(self):
            return iter([])
        def __len__(self):
            return 0


    class map_a(map_, d): pass
    class map_b(e, map_a): pass


im = GenericMethod('im')


@im.of(str)
def im(value):
    return 'str ' + value


@im.of(a)
def im(value):
    return 'a ' + repr(value)


@im.of(b)
def im(value):
    return 'b ' + repr(value)


@im.of(d)
def im(value):
    return 'd ' + repr(value)


@im.of(f)
def im(value):
    return 'f ' + repr(value)


def test_name():
    assert im.__name__ == 'im'


def test_exact_match():
    assert im('a') == 'str a'


def test_type_error():
    with raises(TypeError):
        im(123)


def test_subtype():
    assert im(a()) == 'a <a object>'
    assert im(b()) == 'b <b object>'
    assert im(c()) == 'b <c object>'
    assert im(d()) == 'd <d object>'
    assert im(e()) == 'd <e object>'
    assert im(f()) == 'f <f object>'


im2 = im.clone('im2')


if abc is not None:
    @im2.of(collections.Mapping)
    def im2(value):
        return 'mapping ' + repr(value)

    @im2.of(collections.Iterable)
    def im2(value):
        return 'iterable ' + repr(value)


def test_copy():
    assert im2.__name__ == 'im2'
    if abc is None:
        skip('This Python implementation/version does not have abc module')
    im3 = im2.clone('im3')
    assert im3({}) == 'mapping {}'
    im4 = im3.clone('im4')
    @im4.of(dict)
    def im4_dict(value):
        return 'dict ' + repr(value)
    assert im3({}) == 'mapping {}'
    assert im4({}) == 'dict {}'


im_child = im.inherit('im_child')


@im_child.of(set)
def im_child(value):
    return 'im_child:set ' + repr(value)


@im_child.of(b, with_receiver=True)
def im_child(this, value):
    return 'im_child:b ' + repr(value) + ' ' + this.__name__


def test_inherit():
    assert im_child.__name__ == 'im_child'
    assert im_child(a()) == 'a <a object>'
    assert im_child(b()) == 'im_child:b <b object> im_child'
    assert im_child(c()) == 'im_child:b <c object> im_child'
    assert im_child(d()) == 'im_child:b <d object> im_child'
    assert im_child(set()) == 'im_child:set set([])'
    assert im(a()) == 'a <a object>'
    assert im(b()) == 'b <b object>'
    with raises(TypeError):
        im(set())


def test_abc():
    if abc is None:
        skip('This Python implementation/version does not have abc module')
    assert im2(map_b()) == 'mapping <map_b object>'
    assert im2(map_b()) == 'mapping <map_b object>'  # cache
    assert im2({}) == 'mapping {}'
    assert im2([]) == 'iterable []'
    @im2.of(dict)
    def im2_dict(value):
        return 'dict ' + repr(value)
    assert im2({}) == 'dict {}'  # cache invalidation


def test_issue_2():
    """Regression test for `issue #2`__: multiple type handling with option
    raises error.

    __ https://bitbucket.org/dahlia/typequery/issue/2/multiple-type-handling-with-option-raises

    """
    amp = GenericMethod('amp')
    @amp.of(int)
    @amp.of(float)
    def amp(value, **options):
        try:
            amp_x = options['amp_x']
        except KeyError:
            amp_x = 1
        return value * amp_x
    assert amp(1, amp_x=5) == 5
    assert amp(2.0, amp_x=5) == 10.0
