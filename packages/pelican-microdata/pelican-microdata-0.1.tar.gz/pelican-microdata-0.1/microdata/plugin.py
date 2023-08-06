# -*- coding: utf-8 -*-
"""
Microdata markup for reStructuredText
=====================================

Directives
----------

.. code-block:: ReST

    .. itemscope:: <Schema type>
        :tag: element type (default: div)

        Nested content


    :itemprop:`Displayed test <itemprop name>`


Examples
--------

This reStructuredText document:

.. code-block:: ReST

    .. itemscope: Person
        :tag: p

        My name is :itemprop:`Bob Smith <name>`
        but people call me :itemprop:`Smithy <nickanme>`.
        Here is my home page:
        :itemprop:`www.exemple.com <url:http://www.example.com>`
        I live in Albuquerque, NM and work as an :itemprop:`engineer <title>`
        at :itemprop:`ACME Corp <affiliation>`.


will result in:

.. code-block:: html

    <p itemscope itemtype="http://data-vocabulary.org/Person">
        My name is <span itemprop="name">Bob Smith</span>
        but people call me <span itemprop="nickname">Smithy</span>.
        Here is my home page:
        <a href="http://www.example.com" itemprop="url">www.example.com</a>
        I live in Albuquerque, NM and work as an <span itemprop="title">engineer</span>
        at <span itemprop="affiliation">ACME Corp</span>.
    </p>

"""
from __future__ import unicode_literals

import re

from docutils import nodes
from docutils.parsers.rst import directives, Directive, roles
from pelican.readers import PelicanHTMLTranslator
from types import MethodType


RE_ROLE = re.compile(r'(?P<value>.+?)\s*\<(?P<name>.+)\>')


class ItemProp(nodes.Inline, nodes.TextElement):
    pass


def itemprop_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    match = RE_ROLE.match(text)
    if not match.group('value') and match.group('name'):
        raise ValueError('%s does not match expected itemprop format: :itemprop:`value <name>`')
    value = match.group('value')
    name = match.group('name')
    if ':' in name:
        name, href = name.split(':', 1)
    else:
        href = None
    return [ItemProp(value, value, name=name, href=href)], []


class ItemScope(nodes.Element):
    def __init__(self, tagname, itemtype, itemprop=None):
        kwargs = {
            'itemscope': None,
            'itemtype': "http://data-vocabulary.org/%s" % itemtype,
        }
        if itemprop:
            kwargs['itemprop'] = itemprop
        super(ItemScope, self).__init__('', **kwargs)
        self.tagname = tagname


class ItemScopeDirective(Directive):
    required_arguments = 1
    has_content = True
    option_spec = {
        'tag': directives.unchanged,
        'itemprop': directives.unchanged,
    }

    def run(self):
        itemtype = self.arguments[0]
        tag = self.options.get('tag', 'div')
        itemprop = self.options.get('itemprop', None)
        node = ItemScope(tag, itemtype, itemprop)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def visit_ItemProp(self, node):
    if node['href']:
        self.body.append(self.starttag(node, 'a', '', itemprop=node['name'], href=node['href']))
    else:
        self.body.append(self.starttag(node, 'span', '', itemprop=node['name']))


def depart_ItemProp(self, node):
    if node['href']:
        self.body.append('</a>')
    else:
        self.body.append('</span>')


def visit_ItemScope(self, node):
    self.body.append(node.starttag())


def depart_ItemScope(self, node):
    self.body.append(node.endtag())


def register():
    directives.register_directive('itemscope', ItemScopeDirective)
    roles.register_canonical_role('itemprop', itemprop_role)

    PelicanHTMLTranslator.visit_ItemProp = MethodType(visit_ItemProp, None, PelicanHTMLTranslator)
    PelicanHTMLTranslator.depart_ItemProp = MethodType(depart_ItemProp, None, PelicanHTMLTranslator)
    PelicanHTMLTranslator.visit_ItemScope = MethodType(visit_ItemScope, None, PelicanHTMLTranslator)
    PelicanHTMLTranslator.depart_ItemScope = MethodType(depart_ItemScope, None, PelicanHTMLTranslator)
