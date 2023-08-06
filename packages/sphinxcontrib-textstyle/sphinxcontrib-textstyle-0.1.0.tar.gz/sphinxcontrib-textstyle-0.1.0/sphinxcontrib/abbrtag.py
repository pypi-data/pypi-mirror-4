#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docutils import nodes, utils
from sphinx.util.nodes import split_explicit_title


class AbbrTag(nodes.General, nodes.Element):
    pass


def visit_abbrtag_node(self, node):
    if node.abbr is None:  # if abbr is not set, just write text.
        self.body.append(node.text)
        return

    try:
        self.body.append(self.starttag(node, 'abbr',
                                       node.text, title=node.abbr))
        self.body.append('</abbr>')
    except:
        self.builder.warn('fail to load abbrtag: %r' % node.text)
        raise nodes.SkipNode


def depart_abbrtag_node(self, node):
    pass


def abbrtag_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Role for abbrtag."""
    text = utils.unescape(text)
    has_explicit, text, abbr = split_explicit_title(text)

    abbrtag = AbbrTag()
    abbrtag.text = text
    abbrtag.abbr = abbr

    return [abbrtag], []
