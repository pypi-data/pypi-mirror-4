from fresco.multidict import MultiDict
from nose.tools import assert_equal, assert_raises


class CheckedMultiDict(MultiDict):

    def check_consistency(self):
        "Verify that the MultiDict has internal consistency"
        dictallitems = sorted((k, v)
                              for k, vs in self._dict.items()
                              for v in vs)
        orderallitems = sorted(self._order)
        assert_equal(list(sorted(dictallitems)), list(sorted(orderallitems)))

MultiDict = CheckedMultiDict


class TestMultDict(object):

    def test_getitem_returns_only_first(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        assert_equal(m['a'], 1)

    def test_getitem_throws_keyerror(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        assert_raises(KeyError, lambda: m['c'])

    def test_get_returns_only_first(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        assert_equal(m.get('a'), 1)

    def test_get_returns_default(self):
        m = MultiDict()
        assert_equal(m.get('a'), None)
        assert_equal(m.get('a', 'foo'), 'foo')

    def test_getlist_returns_list(self):
        m = MultiDict([('a', 1), ('a', 2)])
        assert_equal(m.getlist('a'), [1, 2])
        assert_equal(m.getlist('b'), [])

    def test_copy_is_equal(self):
        m = MultiDict([('a', 1), ('a', 2)])
        assert_equal(list(m.allitems()),
                     list(m.copy().allitems()))

    def test_copy_is_independent(self):
        m = MultiDict([('a', 1), ('a', 2)])
        n = m.copy()
        n['b'] = 'foo'
        assert_equal(list(m.allitems()), [('a', 1), ('a', 2)])
        assert_equal(list(n.allitems()), [('a', 1), ('a', 2), ('b', 'foo')])

    def test_fromkeys(self):
        m = MultiDict.fromkeys(['a', 'b'])
        assert_equal(list(m.allitems()), [('a', None), ('b', None)])

    def test_fromkeys_with_value(self):
        m = MultiDict.fromkeys(['a', 'b'], 42)
        assert_equal(list(m.allitems()), [('a', 42), ('b', 42)])

    def test_items_only_returns_first_of_each(self):
        m = MultiDict([('a', 1), ('a', 2)])
        assert_equal(list(m.items()), [('a', 1)])

    def test_listitems_returns_lists(self):
        m = MultiDict([('a', 1), ('a', 2)])
        assert_equal(list(m.listitems()), [('a', [1, 2])])

    def test_allitems_returns_all(self):
        m = MultiDict([('a', 1), ('a', 2)])
        assert_equal(list(m.allitems()), [('a', 1), ('a', 2)])

    def test_allitems_returns_iterator(self):
        m = MultiDict([('a', 1), ('a', 2)])
        i = m.allitems()
        assert_equal(next(i), ('a', 1))
        assert_equal(next(i), ('a', 2))
        assert_raises(StopIteration, lambda: next(i))

    def test_keys(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        i = m.keys()
        assert_equal(next(i), 'a')
        assert_equal(next(i), 'b')
        assert_raises(StopIteration, lambda: next(i))

    def test_values(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        i = m.values()
        assert_equal(next(i), 1)
        assert_equal(next(i), 3)
        assert_raises(StopIteration, lambda: next(i))

    def test_listvalues(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        assert_equal(list(m.listvalues()), [[1, 2], [3]])

    def test_setitem(self):
        m = MultiDict()
        m['a'] = 1
        assert_equal(m['a'], 1)
        assert_equal(m.getlist('a'), [1])
        m.check_consistency()

    def test_setitem_replaces_existing(self):
        m = MultiDict()
        m['a'] = 1
        m['a'] = 2
        assert_equal(m.getlist('a'), [2])
        m.check_consistency()

    def test_delitem(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])

        del m['a']
        assert_equal(
            list(m.allitems()),
            [('b', 3)]
        )
        m.check_consistency()

        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        del m['b']
        assert_equal(
            list(m.allitems()),
            [('a', 1), ('a', 2)]
        )
        m.check_consistency()

    def test_iterable(self):
        m = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        assert_equal(list(iter(m)), ['a', 'b'])

    def test_update_with_list(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.update([('a', 2), ('x', 2)])
        assert_equal(
            list(m.allitems()),
            [('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_update_with_dict(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.update({'a': 2, 'x': 2})
        assert_equal(
            list(m.allitems()),
            [('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_update_with_multidict(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.update(MultiDict([('a', 2), ('x', 2)]))
        assert_equal(
            list(m.allitems()),
            [('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_update_with_kwargs(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.update(a=2, x=2)
        assert_equal(
            sorted(list(m.allitems())),
            [('a', 2), ('b', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_extend_with_list(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.extend([('a', 2), ('x', 2)])
        assert_equal(
            list(m.allitems()),
            [('a', 1), ('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_extend_with_dict(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.extend({'a': 2, 'x': 2})
        assert_equal(
            list(m.allitems()),
            [('a', 1), ('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_extend_with_multidict(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.extend(MultiDict([('a', 2), ('x', 2)]))
        assert_equal(
            list(m.allitems()),
            [('a', 1), ('b', 2), ('a', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_extend_with_kwargs(self):
        m = MultiDict([('a', 1), ('b', 2)])
        m.extend(a=2, x=2)
        assert_equal(
            sorted(list(m.allitems())),
            [('a', 1), ('a', 2), ('b', 2), ('x', 2)]
        )
        m.check_consistency()

    def test_pop(self):
        m = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        assert_equal(m.pop('b'), 2)
        assert_equal(list(m.allitems()), [('a', 1), ('a', 3)])
        m.check_consistency()

    def test_pop_returns_first_item(self):
        m = MultiDict([('a', 1), ('b', 2), ('a', 3)])
        assert_equal(m.pop('a'), 1)
        assert_equal(list(m.allitems()), [('b', 2), ('a', 3)])
        m.check_consistency()

    def test_pop_with_default(self):
        m = MultiDict([])
        assert_equal(m.pop('c', 'foo'), 'foo')
        m.check_consistency()

    def test_popitem(self):
        m = MultiDict([('a', 1), ('b', 2), ('b', 3)])

        assert_equal(m.popitem(), ('b', 2)); m.check_consistency()
        assert_equal(m.popitem(), ('b', 3)); m.check_consistency()
        assert_equal(m.popitem(), ('a', 1)); m.check_consistency()

        try:
            m.popitem()
        except KeyError:
            pass
        else:
            assert False, "Expected KeyError in popitem from empty MultiDict"

    def test_len(self):
        m = MultiDict([('a', 1), ('b', 2), ('b', 3)])
        assert_equal(len(m), 2)

