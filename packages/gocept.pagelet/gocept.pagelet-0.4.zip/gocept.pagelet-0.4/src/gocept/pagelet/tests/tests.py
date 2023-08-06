# Copyright (c) 2007, 2013 gocept gmbh & co. kg
# See also LICENSE.txt
import doctest


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS,
        package='gocept.pagelet')
