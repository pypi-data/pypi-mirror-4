#!/usr/bin/env python
"""
Alternative tables for Markdown

>>> import markdown
>>> md = markdown.Markdown(extensions=['mdSTable'])
>>> h = md.convert('http://test.test.com')
>>> h

"""

import collections
import markdown

try:
    from markdown.util import etree
except ImportError:
    from markdown import etree

class STableProcessor(markdown.blockprocessors.BlockProcessor):

    def test(self, parent, block):
        print block[:6]
        if block[:6] != 'STable':
            return False

        print 'x' * 80
        print block
        print  "\n" in block
        print block[:2]

        return True

    def run(self, parent, blocks):
        """ Parse a table block and build table. """

        columns = []
        order = []
        data = collections.defaultdict(dict)

        table = etree.SubElement(parent, "table")
        title = ''
        rawdata = blocks.pop(0).split("\n")

        for i, line in enumerate(rawdata):
            line = line.strip()
            if i == 0:
                title = line[2:].strip()
                continue

            rky, vl = [x.strip() for x in line.strip()[2:].split('=', 2)]
            cat, ky = rky.split('.', 1)
            if not ky in columns:
                columns.append(ky)
            if not cat in order:
                order.append(cat)

            data[cat][ky] = vl

        tr = etree.SubElement(table, 'tr')
        th = etree.SubElement(tr, 'th')
        th.text = title
        for c in columns:
            th = etree.SubElement(tr, 'th')
            th.text = c

        for o in order:
            tr = etree.SubElement(table, 'tr')
            th = etree.SubElement(tr, 'th')
            th.text = o
            for c in columns:
                td = etree.SubElement(tr, 'td')
                td.text = "%s" % data[o].get(c, '')


class mdSTableExtensions(markdown.Extension):
    """ mdSTable Extension for Python-Markdown. """
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add(
            'graph',
            STableProcessor(md.parser),
            '<hashheader')


def makeExtension(configs=None):
    return mdSTableExtensions(configs=configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
