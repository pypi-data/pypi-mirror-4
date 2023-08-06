#!/usr/bin/env python

import unittest

from jmespath import ast


class TestAST(unittest.TestCase):
    def setUp(self):
        pass

    def test_field(self):
        field = ast.Field('foo')
        match = field.search({'foo': 'bar'})
        self.assertEqual(match, 'bar')

    def test_field_no_match(self):
        field = ast.Field('foo')
        match = field.search({'bar': 'bar'})
        self.assertEqual(match, None)

    def test_field_when_dict(self):
        field = ast.Field('foo')
        match = field.search({'foo': {'bar': 'baz'}})
        self.assertEqual(match, {'bar': 'baz'})

    def test_field_when_list(self):
        field = ast.Field('foo')
        match = field.search({'foo': ['bar', 'baz']})
        self.assertEqual(match, ['bar', 'baz'])

    def test_dot_syntax(self):
        child = ast.SubExpression(ast.Field('foo'), ast.Field('bar'))
        match = child.search({'foo': {'bar': 'correct', 'baz': 'wrong'}})
        self.assertEqual(match, 'correct')

    def test_multiple_nestings(self):
        child = ast.SubExpression(
            ast.Field('foo'),
            ast.SubExpression(ast.Field('bar'), ast.Field('baz')))
        match = child.search(
            {'foo': {'bar': {'baz': 'correct'}}})
        self.assertEqual(match, 'correct')

        self.assertEqual(
            child.search({'foo': {'bar': {'wrong': 'wrong'}}}), None)
        self.assertEqual(child.search({}), None)
        self.assertEqual(child.search([]), None)
        self.assertEqual(child.search(''), None)

    def test_index(self):
        child = ast.SubExpression(ast.Field('foo'), ast.Index(1))
        match = child.search(
            {'foo': ['one', 'two', 'three']})
        self.assertEqual(match, 'two')

    def test_bad_index(self):
        child = ast.SubExpression(ast.Field('foo'), ast.Index(100))
        match = child.search(
            {'foo': ['one', 'two', 'three']})
        self.assertEqual(match, None)

    def test_negative_index(self):
        child = ast.SubExpression(ast.Field('foo'), ast.Index(-1))
        match = child.search(
            {'foo': ['one', 'two', 'last']})
        self.assertEqual(match, 'last')

    def test_index_with_children(self):
        child = ast.SubExpression(
            ast.Field('foo'),
            ast.SubExpression(ast.Field('bar'), ast.Index(-1)))
        match = child.search(
            {'foo': {'bar': ['first', 'middle', 'last']}})
        self.assertEqual(match, 'last')

    def test_multiple_indices(self):
        child = ast.SubExpression(
            ast.SubExpression(
                ast.Field('foo'), ast.Index(1)),
            ast.SubExpression(
                ast.Field('bar'), ast.Index(1)))
        match = child.search(
            {'foo': ['one', {'bar': ['zero', 'one']}]})
        self.assertEqual(match, 'one')

    def test_index_with_star(self):
        child = ast.ElementsBranch(ast.Field('foo'))
        match = child.search({'foo': ['one', 'two']})
        self.assertEqual(match, ['one', 'two'])


    def test_associative(self):
        data = {'foo': {'bar': ['one']}}
        first = ast.SubExpression(
            ast.Field('foo'),
            ast.SubExpression(ast.Field('bar'), ast.Index(0)))
        second = ast.SubExpression(
            ast.SubExpression(ast.Field('foo'), ast.Field('bar')),
            ast.Index(0))
        self.assertEqual(first.search(data), 'one')
        self.assertEqual(second.search(data), 'one')

    def test_wildcard_branches_on_dict_values(self):
        data = {'foo': {'bar': {'get': 'one'}, 'baz': {'get': 'two'}}}
        # ast for "foo.*.get"
        expression = ast.SubExpression(
            ast.ValuesBranch(ast.Field('foo')),
            ast.Field('get'))
        match = expression.search(data)
        self.assertEqual(sorted(match), ['one', 'two'])
        self.assertEqual(expression.search({'foo': [{'bar': 'one'}]}), None)

    def test_wildcard_branches_with_index(self):
        # foo[*].bar
        child = ast.SubExpression(
            ast.ElementsBranch(ast.Field('foo')),
            ast.Field('bar')
        )
        match = child.search(
            {'foo': [{'bar': 'one'}, {'bar': 'two'}]})
        self.assertTrue(isinstance(match, list))
        self.assertEqual(match, ['one', 'two'])

    def test_index_with_multi_match(self):
        # foo[*].bar[0]
        child = ast.SubExpression(
            ast.ElementsBranch(ast.Field('foo')),
            ast.SubExpression(
                ast.Field('bar'),
                ast.Index(0)))
        data = {'foo': [{'bar': ['one', 'two']}, {'bar': ['three', 'four']}]}
        match = child.search(data)
        self.assertEqual(match, ['one', 'three'])

    def test_or_expression(self):
        # foo or bar
        field_foo = ast.Field('foo')
        field_bar = ast.Field('bar')
        or_expression = ast.ORExpression(field_foo, field_bar)
        self.assertEqual(or_expression.search({'foo': 'foo'}), 'foo')
        self.assertEqual(or_expression.search({'bar': 'bar'}), 'bar')
        self.assertEqual(or_expression.search(
            {'foo': 'foo', 'bar': 'bar'}), 'foo')


if __name__ == '__main__':
    unittest.main()
