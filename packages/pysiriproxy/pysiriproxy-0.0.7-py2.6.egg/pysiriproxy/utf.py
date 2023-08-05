# Copyright (C) (c) 2012 Brett Ponsler, Pete Lamonica, Pete Lamonica
# This file is part of pysiriproxy.
#
# pysiriproxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysiriproxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysiriproxy.  If not, see <http://www.gnu.org/licenses/>.
'''The utf module contains a class dedicated to converting UTF strings
into ASCII strings.

'''


class Utf:
    '''The Utf class provides a dictionary of UTF strings that should be
    replaced with ASCII equivalent strings.

    '''

    Replacements = {
        "\xe2\x80\x98": "'",
        "\xe2\x80\x99": "'",
        "\xe2\x80\x9c": '"',
        "\xe2\x80\x9d": '"',
        "\xe2\x80\x93": '-',
        "\xe2\x80\x94": '--',
        "\xe2\x80\xa6": '...',
        }
    '''The Replacements property contains a dictionary mapping UTF strings
    to the ASCII equivalent strings which they will be replaced with.

    '''

    @classmethod
    def replaceUtf(cls, utfString):
        '''Replace all of the UTF strings in the :attr:`Replacements`
        property with their ASCII equivalent strings.

        * utfString -- The string containing UTF characters

        '''
        for replacement, value in Utf.Replacements.iteritems():
            utfString = utfString.replace(replacement, value)

        return utfString
