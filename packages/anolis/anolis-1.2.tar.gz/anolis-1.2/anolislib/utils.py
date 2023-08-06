# coding=UTF-8
# Copyright (c) 2008 Geoffrey Sneddon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import unicode_literals

from copy import deepcopy
import re
import sys
from lxml import etree

from html5lib.constants import spaceCharacters

if sys.version_info[0] == 3:
    str_type = str
    unicode_type = str
else:
    str_type = basestring
    unicode_type = unicode

ids = {}

spaceCharacters = "".join(spaceCharacters)
spacesRegex = re.compile("[%s]+" % spaceCharacters)

heading_content = frozenset(["h1", "h2", "h3", "h4", "h5", "h6",
                             "hgroup"])
sectioning_content = frozenset(["section", "nav", "article", "aside"])
sectioning_root = frozenset(["body", "blockquote", "figure", "td",
                             "datagrid"])

always_interactive_content = frozenset(["a", "bb", "details", "datagrid"])
media_elements = frozenset(["audio", "video"])

non_sgml_name = re.compile("[^A-Za-z0-9_:.]+")

if sys.maxunicode == 0xFFFF:
    # UTF-16 Python
    non_ifragment = re.compile("([\u0000-\u0020\u0022\u0023\u0025\\\u002D\u003C\u003E\u005B-\u005E\u0060\u007B-\u007D\u007F-\u0099\uD800-\uF8FF\uFDD0-\uFDDF\uFFF0-\uFFFF]|\U0001FFFE|\U0001FFFF|\U0002FFFE|\U0002FFFF|\U0003FFFE|\U0003FFFF|\U0004FFFE|\U0004FFFF|\U0005FFFE|\U0005FFFF|\U0006FFFE|\U0006FFFF|\U0007FFFE|\U0007FFFF|\U0008FFFE|\U0008FFFF|\U0009FFFE|\U0009FFFF|\U000AFFFE|\U000AFFFF|\U000BFFFE|\U000BFFFF|\U000CFFFE|\U000CFFFF|\uDB3F[\uDFFE-\uDFFF]|[\uDB40-\uDB43][\uDC00-\uDFFF]|\uDB7F[\uDFFE-\uDFFF]|[\uDB80-\uDBFF][\uDC00-\uDFFF])+")
else:
    # UTF-32 Python
    non_ifragment = re.compile("[^A-Za-z0-9._~!$&'()*+,;=:@/\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF\U00010000-\U0001FFFD\U00020000-\U0002FFFD\U00030000-\U0003FFFD\U00040000-\U0004FFFD\U00050000-\U0005FFFD\U00060000-\U0006FFFD\U00070000-\U0007FFFD\U00080000-\U0008FFFD\U00090000-\U0009FFFD\U000A0000-\U000AFFFD\U000B0000-\U000BFFFD\U000C0000-\U000CFFFD\U000D0000-\U000DFFFD\U000E1000-\U000EFFFD]+")


def splitOnSpaces(string):
    return spacesRegex.split(string)


def elementHasClass(Element, class_name):
    if Element.get("class") and \
       class_name in splitOnSpaces(Element.get("class")):
        return True
    else:
        return False


def generateID(Element, force_html4_id=False, **kwargs):
    if Element.get("id") is not None:
        return Element.get("id")
    elif Element.get("title") is not None and \
         Element.get("title").strip(spaceCharacters) != "":
        source = Element.get("title")
    else:
        source = textContent(Element)

    source = source.strip(spaceCharacters).lower()

    if source == "":
        source = "generatedID"
    elif force_html4_id or Element.getroottree().docinfo.public_id in \
        ("-//W3C//DTD HTML 4.0//EN",
         "-//W3C//DTD HTML 4.0 Transitional//EN",
         "-//W3C//DTD HTML 4.0 Frameset//EN",
         "-//W3C//DTD HTML 4.01//EN",
         "-//W3C//DTD HTML 4.01 Transitional//EN",
         "-//W3C//DTD HTML 4.01 Frameset//EN",
         "ISO/IEC 15445:2000//DTD HyperText Markup Language//EN",
         "ISO/IEC 15445:2000//DTD HTML//EN",
         "-//W3C//DTD XHTML 1.0 Strict//EN",
         "-//W3C//DTD XHTML 1.0 Transitional//EN",
         "-//W3C//DTD XHTML 1.0 Frameset//EN",
         "-//W3C//DTD XHTML 1.1//EN"):
        source = non_sgml_name.sub("-", source).strip("-")
        try:
            if not source[0].isalpha():
                source = "x" + source
        except IndexError:
            source = "generatedID"
    else:
        source = non_ifragment.sub("-", source).strip("-")
        if source == "":
            source = "generatedID"

    # Initally set the id to the source
    id = source

    i = 0
    while getElementById(Element.getroottree().getroot(), id) is not None:
        id = "%s-%i" % (source, i)
        i += 1

    ids[Element.getroottree().getroot()][id] = Element

    return id


def textContent(Element):
    # Copy the element and get ready for removals
    Element = deepcopy(Element)
    to_remove = set()
    
    # Replace img with its alt attribute
    for child in Element.iter(tag="img"):
        # Add alt in its place
        if child.get("alt") is not None:
            if child.getprevious() is not None:
                if child.getprevious().tail is None:
                    child.getprevious().tail = child.get("alt")
                else:
                    child.getprevious().tail += child.get("alt")
            else:
                if child.getparent().text is None:
                    child.getparent().text = child.get("alt")
                else:
                    child.getparent().text += child.get("alt")
        # Preserve the element tail
        if child.tail is not None:
            if child.getprevious() is not None:
                if child.getprevious().tail is None:
                    child.getprevious().tail = child.tail
                else:
                    child.getprevious().tail += child.tail
            else:
                if child.getparent().text is None:
                    child.getparent().text = child.tail
                else:
                    child.getparent().text += child.tail
        # Get ready to remove the element
        to_remove.add(child)
        
    # Remove to_remove nodes
    for node in to_remove:
        node.getparent().remove(node)
    
    # Then just use tostring
    return etree.tostring(Element, encoding=unicode_type, method='text',
                          with_tail=False)


def getElementById(base, id):
    if base in ids:
        try:
            return ids[base][id]
        except KeyError:
            return None
    else:
        ids[base] = {}
        for element in base.iter(tag=etree.Element):
            if element.get("id"):
                ids[base][element.get("id")] = element
        return getElementById(base, id)


def escapeXPathString(string):
    return "concat('', '%s')" % string.replace("'", "', \"'\", '")


def removeInteractiveContentChildren(element):
    # Iter over list of decendants of element
    for child in element.findall(".//*"):
        if isInteractiveContent(child):
            # Copy content, to prepare for the node being removed
            copyContentForRemoval(child)
            # Remove element
            child.getparent().remove(child)


def isInteractiveContent(element):
    if element.tag in always_interactive_content \
    or element.tag in media_elements and element.get("controls") is not None \
    or element.tag == "menu" and element.get("type") is not None and \
       element.get("type").lower() == "toolbar":
        return True
    else:
        return False


def copyContentForRemoval(node, text=True, children=True, tail=True):
    # Preserve the text, if it is an element
    if isinstance(node.tag, str_type) and node.text is not None and text:
        if node.getprevious() is not None:
            if node.getprevious().tail is None:
                node.getprevious().tail = node.text
            else:
                node.getprevious().tail += node.text
        else:
            if node.getparent().text is None:
                node.getparent().text = node.text
            else:
                node.getparent().text += node.text
    # Re-parent all the children of the element we're removing
    if children:
        for child in node:
            node.addprevious(child)
    # Preserve the element tail
    if node.tail is not None and tail:
        if node.getprevious() is not None:
            if node.getprevious().tail is None:
                node.getprevious().tail = node.tail
            else:
                node.getprevious().tail += node.tail
        else:
            if node.getparent().text is None:
                node.getparent().text = node.tail
            else:
                node.getparent().text += node.tail

def replaceComment(ElementTree, comment, sub, **kwargs):
    begin_sub = "begin-%s" % comment
    end_sub = "end-%s" % comment
    sub_parent = None
    to_remove = set()
    for node in ElementTree.iter():
        if sub_parent is not None:
            if node.tag is etree.Comment and \
               node.text.strip(spaceCharacters) == end_sub:
                if node.getparent() is not sub_parent:
                    raise DifferentParentException("%s and %s have different parents" % begin_sub, end_sub)
                sub_parent = None
            else:
                to_remove.add(node)
        elif node.tag is etree.Comment:
            if node.text.strip(spaceCharacters) == begin_sub:
                sub_parent = node.getparent()
                node.tail = None
                node.addnext(deepcopy(sub))
                indentNode(node.getnext(), 0, **kwargs)
            elif node.text.strip(spaceCharacters) == comment:
                node.addprevious(etree.Comment(begin_sub))
                indentNode(node.getprevious(), 0, **kwargs)
                node.addprevious(deepcopy(sub))
                indentNode(node.getprevious(), 0, **kwargs)
                node.addprevious(etree.Comment(end_sub))
                indentNode(node.getprevious(), 0, **kwargs)
                node.getprevious().tail = node.tail
                to_remove.add(node)

    for node in to_remove:
        node.getparent().remove(node)

def indentNode(node, indent=0, newline_char="\n", indent_char=" ", **kwargs):
    whitespace = newline_char + indent_char * indent
    if node.getprevious() is not None:
        if node.getprevious().tail is None:
            node.getprevious().tail = whitespace
        else:
            node.getprevious().tail += whitespace
    else:
        if node.getparent().text is None:
            node.getparent().text = whitespace
        else:
            node.getparent().text += whitespace

global reversed
try:
    reversed
except NameError:
    def reversed(x):
        if hasattr(x, 'keys'):
            raise ValueError("mappings do not support reverse iteration")
        i = len(x)
        while i > 0:
            i -= 1
            yield x[i]


class AnolisException(Exception):
    """Generic anolis error."""
    pass

class DifferentParentException(AnolisException):
    """begin-link and end-link do not have the same parent."""
    pass
