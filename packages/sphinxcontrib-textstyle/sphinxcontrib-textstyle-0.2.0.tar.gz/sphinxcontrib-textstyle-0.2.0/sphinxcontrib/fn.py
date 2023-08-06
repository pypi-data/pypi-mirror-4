#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docutils import nodes, utils
from sphinx.util.nodes import split_explicit_title


def fn_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Role for fn."""
    text = utils.unescape(text)
    has_explicit, label, footnotetext = split_explicit_title(text)

    if has_explicit == False:
        return [nodes.Text(label)], []

    fn = nodes.footnote()
    fn['auto'] = '1'
    fn['text'] = label
    inliner.document.set_id(fn, fn)
    _id = fn['ids'].pop()

    inliner.document.set_id(fn, fn)
    fn['refid'] = fn['ids'].pop()
    fn['ids'].append(_id)

    return [fn], []

def on_doctree_read(self, doctree):
    for i, fn in enumerate(doctree.traverse(nodes.footnote)):
        fnref = nodes.footnote_reference()
        fnref['auto'] = fn['auto']
        fnref['ids'] = fn['ids']
        fnref['refid'] = fn['refid']
        fnref += nodes.Text(str(i + 1))

        footnote = nodes.footnote()
        footnote['auto'] = fn['auto']
        footnote['backrefs'] = fn['ids']
        footnote['ids'] = [fn['refid']]
        footnote += nodes.label(text=str(i + 1))
        footnote += nodes.paragraph(text=fn['text'])

        n = fn
        while True:
            if isinstance(n.parent, (nodes.document)):
                break

            n = n.parent
            if isinstance(n, (nodes.paragraph)):
                break
            pos = n.parent.index(n)
            try:
                while isinstance(n.parent.children[pos + 1], nodes.footnote):
                    pos += 1
            except:
                pass
            n.parent.insert(pos + 1, footnote)
            fn.parent.replace(fn, fnref)

