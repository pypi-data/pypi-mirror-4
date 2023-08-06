#!/usr/bin/env python3
"""Holy Hand Grenade: A Pure python web browser"""
__version__ = "0.1"
__author__ = "Da_Blitz"
__email__ = "code@pocketnix.org"
__url__ = "http://code.pocketnix.org/holyhandgrenade"

from argparse import ArgumentParser, FileType
import lxml.etree
import textwrap
import sys

class BlockContext:
    def __init__(self):
        self._elements = []
    
    def add_element(self, element):
        self._elements.append(element)
    
    def __str__(self):
        output = []
        for element in self._elements:
            if isinstance(element, BlockContext):
                output += [str(element), '\n']
            elif isinstance(element, InlineContext):
                output.append(str(element))
                
    def __iter__(self):
        return iter(self._elements)
        
class InlineContext:
    def __init__(self, element):
        self.element = element

    def __str__(self):
        return str(self.element)

def get_renderer(tag):
    tag_renderer = {
        'body': render_box,
        'h1': render_box,
        'h2': render_box,
        'h3': render_box,
        'h4': render_box,
        'h5': render_box,
        'a': render_inline,
        'div': render_box,
        'p': render_box,
        'code': render_inline,
        'pre': render_box,
        'article': render_box,
        'section': render_box,
        'ul': render_box,
        'li': render_li,
        'span': render_inline,
    #    'img': render_img,
        
    #    'head': render_invisible,
    #     'title': render_title,
    #    'link': render_link,
    #    'style': render_asset,
    #    'script': render_asset,
        }
        
    tag_renderer_default = render_box
    
    return tag_renderer.get(tag, tag_renderer_default)


def render_title(node, context):
    context['title'] = node.text
    return []

def render_box(node, context):
    context = BlockContext()
    if node.text:
        text = "".join(filter_whitespace(node.text))
        context.add_element(InlineContext(text))

    for node in node.iterchildren():
        render = get_renderer(node.tag)
        context.add_element(render(node, context))
    
    if node.tail:
        text = "".join(filter_whitespace(node.tail))
        context.add_element(InlineContext(text))

    return context

def render_inline(node, context):
    return InlineContext(node.text)

def render_li(node, context):
    if node.text:
        block = BlockContext()
        block.add_element(InlineContext(" * " + node.text))
    else:
        block = InlineContext('')
    
    return block

class TOC:
    def __init__(self, heading, level=0):
        self.heading = heading
        self._children = []
        self.level = level
    
    def __getitem__(self, key):
        return self._children[key]

    def __setitem__(self, key, val):
        self._children[key] = val
    
    def __delitem__(self, key):
        del self._children[key]
    
    def __iter__(self):
        return iter(self._children)
    
    def __len__(self):
        return len(self._children)
    
    def __repr__(self):
        return '<TOC: heading="{}", level={}>'.format(self.heading, self.level)
    
    @staticmethod
    def tag_to_level(tag):
        "Convert a tag (eg 'h3') to a heading depth (ie '3' in the previos example)"
        level = int(tag[1:])
        
        return level
        
    def add_heading(self, tag, heading):
        if not isinstance(tag, int):
            tag = self.tag_to_level(tag)
        
        level = tag
        
        if level > self.level:
            try:
                child_toc = self[-1]
                child_toc.add_heading(tag, heading)
            except IndexError:
                child_toc = TOC(heading, level)
                self._children.append(child_toc)
        else:
            self._children.append(TOC(heading, level))

def render_heading(node, context):
    context.setdefault('toc', TOC(None)).add_heading(node.tag, node.text)
    
    yield node.text

def filter_whitespace(stream, strip_leading=False, whitespace_char=" "):
    """Collapse consective whitespace into a single whitespace char
    
    strip_leading: strip the leading spaces
    """
    seen_space = strip_leading
    for entry in stream:
        is_space = entry.isspace()
        if is_space and seen_space:
            continue
        elif is_space:
            seen_space = True
            yield whitespace_char
        else: # is word
            seen_space = False
            yield entry        


def render(tree, width=79):
    content = ""
    for node in tree:
        if isinstance(node, InlineContext):
            content += str(node)
        else:
            block = render(node)
            content += '\n\n' + block

    return content

def main(argv=sys.argv[1:]):
    args = ArgumentParser()
    args.add_argument('file', help="The file to render", type=FileType('r'))
    args.add_argument('-w', '--width', default=79, type=int,
                      help="Specify a set width to render to")
    
    options = args.parse_args(argv)

#    string = render_box(doc, context)
#    string = "".join(string)
#    string = string.strip()
    
#    print("Titles:")
#    def print_children(toc):
#        prefix = " " * toc.level
#        print(prefix, '- '  + str(toc.heading), sep='')
#        for child in toc:
#            print_children(child)
#    print_children(context['toc'])
    
    
    html = lxml.etree.fromstring(options.file.read())
    context = {}

    tree = render_box(html, context)
    page = render(tree, options.width)
    page = page.split('\n')
    
    final = []
    for line in page:
        final += textwrap.wrap(line, options.width)
    final = '\n'.join(final)
    
    print("Context: ", context)
    print(final)
    

if __name__ == "__main__":
    main()
