#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the standard library

# Import from itools
from itools.core import freeze
from itools.stl.stl import NamespaceStack, subs_expr, evaluate, evaluate_if
from itools.stl.stl import evaluate_repeat

# Import from lpod
from element import odf_element


DEFAULT, REPEAT, ENDREPEAT, IF, ENDIF = range(5)


def substitute(data, stack, repeat_stack):
    """Interprets the given data as a substitution string with the "${expr}"
    format, where the expression within the brackets is an STL expression.

    Returns the interpreted string.
    """
    segments = subs_expr.split(data)
    for i, segment in enumerate(segments):
        if i % 2:
            # if
            if segment[:3] == u"if ":
                yield evaluate_if(segment[3:], stack, repeat_stack)
            # endif
            elif segment == u"endif":
                yield ENDIF
            # repeat
            elif segment[:7] == u"repeat ":
                yield evaluate_repeat(segment[7:], stack, repeat_stack)
            # endrepeat
            elif segment == u"endrepeat":
                yield ENDREPEAT
            # Evaluate expression
            else:
                value = evaluate(segment, stack, repeat_stack)
                if isinstance(value, odf_element):
                    # Return a copy because nodes are not reusable
                    yield value.clone()
                else:
                    # Do not expect anything else that unicode for text
                    yield unicode(value)
        elif segment:
            yield segment



def process(element, stack, repeat_stack):
    state = DEFAULT
    if_state = None

    for result in element.xpath('descendant::text()'):
        parent = result.get_parent()
        is_text = result.is_text()
        text = []
        for value in substitute(result, stack, repeat_stack):
            # if
            if value is True or value is False:
                state = IF
                if_state = value
            # endif
            elif value is ENDIF:
                state = DEFAULT
                if_state = None
            # repeat
            elif type(value) is tuple:
                name, values = value
                # TODO for each value, repeat the process from this element to
                # the "endrepeat"
                raise NotImplementedError, 'repeat'
            # unicode
            elif type(value) is unicode:
                if state is IF and if_state is False:
                    continue
                text.append(value)
            # odf_element
            elif isinstance(value, odf_element):
                # Save what was substituted so far
                text = u"".join(text)
                if result.is_text():
                    parent.set_text(text)
                    parent.insert_element(value, position=0)
                else:
                    parent.set_tail(text)
                    container = parent.get_parent()
                    index = container.index(parent)
                    container.insert_element(value, position=index + 1)
                # Update the parent for next segments
                parent = value
                is_text = False
                text = []
            else:
                raise NotImplementedError, type(value)
        text = u"".join(text)
        if is_text:
            parent.set_text(text)
        else:
            parent.set_tail(text)



def stl_odf(document=None, namespace=freeze({}), element=None):
    """Apply the given namespace to the document (or element) where matching
    "${xxx}" are replaced by their value.

    Clone of itools.stl for odf_document.

    Arguments:

        document -- odf_document

        namespace -- dict

    Return: modified "document" argument
    """
    # Input
    if element is None:
        element = document.get_body()
    # Initialize the namespace stacks
    stack = NamespaceStack()
    stack.append(namespace)
    repeat_stack = NamespaceStack()
    # Process
    stream = process(element, stack, repeat_stack)
    # Return
    return stream
