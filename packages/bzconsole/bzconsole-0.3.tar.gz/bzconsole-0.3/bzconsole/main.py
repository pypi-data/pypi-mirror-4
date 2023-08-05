#!/usr/bin/env python

import sys
from api import BZapi
from command import CommandParser
from StringIO import StringIO

class BZcli(BZapi):
    """command line interface front-end for the API class"""

    def unique(self, component=None):
        """display unique and duplicated components"""
        unique, dupe = self._unique_components()

        if component:
            # determine if the component is unique
            if component in unique:
                return '%s: %s' % (component, unique[component])
            if component in dupe:
                return '>>>DUPLICATE<<<'
            return 'Component "%s" not found' % component

        buffer = StringIO()
        print >> buffer, 'Unique:'
        for key in sorted(unique.keys()):
            print >> buffer, ' %s: %s' % (key, unique[key])
        print >> buffer
        print >> buffer, 'Duplicate:'
        for value in sorted(dupe):
            print >> buffer, ' %s' % value
        return buffer.getvalue()

def main(args=sys.argv[1:]):
    parser = CommandParser(BZcli)
    parser.invoke(args)

if __name__ == '__main__':
    main()
