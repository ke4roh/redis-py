# -*- coding: utf-8 -*-
import pytest
from redis.collections import \
    RedisSortedSet, RedisDict, RedisSet, RedisList, ObjectRedis
from redis._compat import OrderedDict


class TestRedisList(object):
    def test_list(self, sr):
        l = RedisList('foo', redis=sr)
        assert 0 == len(l)
        with pytest.raises(StopIteration):
            next(l.__iter__())
        l.append(1)
        assert 1 == len(l)
        assert 1 == l[0]
        l.append(3)
        assert 3 == l[1]
        assert 2 == len(l)
        assert 1 == l[0]
        l[1] = 2
        assert 2 == l[1]
        assert 2 == l[-1]
        assert 1 == l[-2]
        assert [1, 2] == list(l)
        assert 2 == len(l)
        with pytest.raises(IndexError):
            l[2]
        assert 3 == sum(l)

        l.insert(1, 'x')
        assert 'x', l[1] == str(list(l))
        assert [1, 'x', 2] == list(l)

        l.insert(3, 'z')
        assert l[3] == 'z'

        assert ['z', 2, 'x', 1] == list(l.__reversed__())

        assert 4 == len(l)
        assert 3 == l.index('z')
        with pytest.raises(ValueError):
            l.remove('t')
        assert 4 == len(l)
        assert 'z' in l
        l.remove('z')
        assert 3 == len(l)
        assert not ('z' in l)

        l.extend([7, 8, 9])
        assert [1, 'x', 2, 7, 8, 9] == list(l)
        assert (1 in l)

        del l[3]
        assert [1, 'x', 2, 8, 9] == list(l)

        assert 1 == l.index('x')
        with pytest.raises(ValueError):
            l.index('t')

        assert 9 == l.pop()
        assert [1, 'x', 2, 8] == list(l)

        assert 'x' == l.pop(1)
        assert [1, 2, 8] == list(l)
        with pytest.raises(IndexError):
            l.pop(3)

        l.clear()
        with pytest.raises(IndexError):
            l.pop(0)
        with pytest.raises(IndexError):
            l.pop(-1)

        assert 0 == len(l)
        l.append(1)
        with pytest.raises(IndexError):
            l.pop(1)

    def test_copy(self, sr):
        l = RedisList('l', sr)
        l.extend([1, 2, 3, 4])
        assert [1, 2, 3, 4] == list(l)

    def test_repr(self, sr):
        l = RedisList('l', sr)
        l.extend([1, 2, 3, 4])
        assert "<RedisList(name='l',[1, 2, 3, 4])>" == str(l)
        l.append('x')
        assert "<RedisList(name='l',[1, 2, 3, 4, 'x'])>" == str(l)
        l.extend(range(6, 13))
        assert "<RedisList(name='l',[1, 2, 3, 4, 'x', 6, " \
               "7, 8, 9, 10, …])>" == str(l)


class TestObjectRedis(object):
    def test_basic_dict(self, sr):
        d = ObjectRedis(sr)
        assert len(d) == 0
        with pytest.raises(KeyError):
            d[True]
        d[True] = 42.1
        assert len(d) == 1
        assert d[True] == 42.1
        d[3] = 'three'  # turns out d[1] and d[True] are equivalent
        # in the standard implementations
        assert d[3] == 'three'
        assert len(d) == 2

        assert set([True, 3]) == set(d.keys())
        assert {True: 42.1, 3: 'three'} == dict(d)

    def test_namespace(self, sr):
        d = ObjectRedis(sr, namespace="foo")
        assert len(d) == 0
        with pytest.raises(KeyError):
            d[True]
        d[True] = 42.1
        assert len(d) == 1
        assert d[True] == 42.1
        d[1] = 'one'
        assert d[1] == 'one'
        assert len(d) == 2

        d2 = ObjectRedis(sr)
        assert len(d2) == 0  # This instance won't unpickle keys from the other
        # instance, so can't see them
        d2[True] = 38
        assert len(d) == 2
        assert len(d2) == 1
        assert d2[True] == 38
        assert d[True] == 42.1

    def test_storing_collections(self, sr):
        d = ObjectRedis(sr)
        d['list'] = [1, 2, 3, 4, 5]
        assert [1, 2, 3, 4, 5] == list(d['list'])
        d['map'] = {'a': 'red', 'b': 'blue'}
        assert {'a': 'red', 'b': 'blue'} == dict(d['map'])
        od = OrderedDict()
        od[89.7] = 'WCPE'
        od[91.5] = 'WUNC'
        d['od'] = od
        assert od == dict(d['od'])
        s = set(['oats', 'peas', 'beans'])
        d['set'] = s
        assert s == set(d['set'])

    def test_repr(self, sr):
        d = ObjectRedis(sr)
        d['list'] = [1, 2, 3, 4, 5]
        d['foo'] = 'bar'
        print(str(d))
        assert "<ObjectRedis(namespace=None,{'list': " \
               "<RedisList(name=\"S'list'\\np0\\n.\",[1, 2, 3, 4, 5])>, " \
               "'foo': 'bar'})>" == str(d)


class TestRedisDict(object):
    def test_values(self, sr):
        d = RedisDict('foo', redis=sr)
        d['a'] = 'b'
        assert 'b' == d['a']
        assert list({'a': 'b'}.__iter__()) == list(d.__iter__())
        assert ['b'] == list(d.values())
        with pytest.raises(TypeError):
            d[['a']] = 'b'

    def test_keys(self, sr):
        d = RedisDict('foo', redis=sr)
        d['a'] = 'A'
        d['c'] = 'C'
        assert set(['a', 'c']) == set(d.keys())

    def test_copy(self, sr):
        d = RedisDict('foo', redis=sr)
        d['a'] = 'A'
        d['c'] = 'C'
        assert {'a': 'A', 'c': 'C'} == dict(d)

    def test_repr(self, sr):
        d = RedisDict('foo', redis=sr)
        refd = {'sunshine': 'rainbows', 'moon': 'eclipse'}
        d.update(refd)
        assert \
            "<RedisDict(name='foo'," \
            "{'moon': 'eclipse', 'sunshine': 'rainbows'})>" \
            == str(d) or \
            "<RedisDict(name='foo'," \
            "{'sunshine': 'rainbows', 'moon': 'eclipse'})>" == str(d)


class TestRedisSortedSet(object):
    def test_sorted(self, sr):
        s = RedisSortedSet('foo', redis=sr)
        assert 0 == len(s)
        assert not ('bar' in s)
        s['bar'] = 5
        assert ('bar' in s)
        assert 5.0 == s['bar']
        with pytest.raises(TypeError):
            s['bar'] = 'baz'
        od = OrderedDict()
        od['bar'] = 5.0
        assert od == OrderedDict(s)
        assert 1 == len(s)

        assert not ('bat' in s)
        s['bat'] = 1
        assert ('bat' in s)
        assert 1.0 == s['bat']
        od['bat'] = 1.0
        od.move_to_end('bar')
        assert od == OrderedDict(s)

    def test_iter(self, sr):
        s = RedisSortedSet('foo', redis=sr)
        s['tigers'] = 2
        s['lions'] = 1
        s['bears'] = 3
        i = s.__iter__()
        assert 'lions' == next(i)
        assert 'tigers' == next(i)
        assert 'bears' == next(i)

    def test_update(self, sr):
        s = RedisSortedSet('foo', redis=sr)
        s.update({'red': 650, 'green': 510, 'blue': 475})
        od = OrderedDict()
        od['blue'] = 475
        od['green'] = 510
        od['red'] = 650
        assert od == OrderedDict(s)

    def test_hashable_key(self, sr):
        s = RedisSortedSet('foo', redis=sr)
        with pytest.raises(TypeError):
            s[['nohash']] = 1

    def test_repr(self, sr):
        s = RedisSortedSet('foo', redis=sr)
        s.update({'H': 1, 'He': 2, 'Li': 3})
        assert "<RedisSortedSet(name='foo'," \
               "{'H': 1.0, 'He': 2.0, 'Li': 3.0})>" \
               == str(s)


class TestRedisSet(object):
    def test_set(self, sr):
        s = RedisSet('foo', redis=sr)
        s.add('grunge')
        assert ('grunge' in s)
        s.add(True)
        s.add(('graph',))
        assert set(['grunge', True, ('graph',)]) == set(s)
        assert 3 == len(s)
        assert 3 == sum(1 for _ in s)

        with pytest.raises(TypeError):
            s.add(['nohash'])

        s.clear()
        assert 0 == len(s)

    def test_zero_element(self, sr):
        s = RedisSet('foo', redis=sr)
        s.add(0)
        assert 1 == len(s)
        assert set([0]) == set(s)

        s.add(None)
        assert 2 == len(s)
        assert set([0, None]) == set(s)

    def test_update(self, sr):
        s = RedisSet('bar', redis=sr)
        ref = set(['oats', 'peas', 'beans'])
        s.update(tuple(ref))
        assert ref == set(s)

    def test_update_with_nothing(self, sr):
        s = RedisSet('bar', sr)
        s.update([])  # should have no effect
        assert set() == set(s)
        assert 0 == len(s)

        s.update()
        assert 0 == len(s)

        with pytest.raises(TypeError):
            s.update(None)

        with pytest.raises(TypeError):
            s.update(0)

    def test_bigger_set(self, sr):
        s = RedisSet('bar', sr)

        ref = set(range(0, 10000))
        s.update(ref)
        assert len(ref) == len(s)
        assert ref == set(s)
        assert ref == set(s.__iter__())
        s.clear()
        assert 0 == len(s)

    def test_repr(self, sr):
        s = RedisSet('bar', sr)
        s.update(['foo', 'bar'])
        assert "<RedisSet(name='bar',{'foo', 'bar'})>" == str(s) or \
               "<RedisSet(name='bar',{'bar', 'foo'})>" == str(s)
