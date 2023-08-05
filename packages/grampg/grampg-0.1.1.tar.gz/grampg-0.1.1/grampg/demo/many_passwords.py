# Copywrite 2012 Elvio Toccalino

# This file is part of grampg.
#
# grampg is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# grampg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with grampg.  If not, see <http://www.gnu.org/licenses/>.

"""
Demo program for the grampg library.

The many_passwords program generates two sets of passwords (the total number of
which is parameterized), each according to "reasonable" specs.
"""

import grampg


def many_passwords(quantity):
    password = grampg.PasswordGenerator()

    print ("Passwords of 3 lower letters and 3"
           " numbers beginning with a lower letter.")
    generator = (password.of()
                 .exactly(3, 'lower_letters')
                 .exactly(3, 'numbers')
                 .beginning_with('lower_letters')
                 .done())
    for i in xrange(quantity):
        print "\t", generator.generate()
    print ""

    print ("Passwords of between 3 and 7 lower letters and 5"
           " upper letters, with a fixed length of 10.")
    generator = (password.of()
                 .between(3, 7, 'lower_letters')
                 .exactly(5, 'upper_letters')
                 .length(10)
                 .done())
    for i in xrange(quantity):
        print "\t", generator.generate()
    print ""


if __name__ == '__main__':
    many_passwords(5)
