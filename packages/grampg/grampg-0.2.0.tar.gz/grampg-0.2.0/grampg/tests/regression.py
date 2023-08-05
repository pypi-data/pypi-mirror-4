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
Regression tests, from debuggin the grampg to its test suite.
"""

import unittest

# Import internals for testing.
from grampg import grampg


def how_many(charset, string, pgenerator):
    """Return how many of `charset` are in `string`."""
    if charset not in pgenerator.sets.keys():
        raise ValueError('Character set %s is not known.' % charset)
    counter = 0
    for char in string:
        if char in pgenerator.sets[charset]:
            counter += 1
    return counter


def between(lbound, rbound, charset, string, pgenerator):
    """If there's `charset` between [`lbound`, `rbound`] chars in `string`."""
    num = how_many(charset, string, pgenerator)
    return num >= lbound and num <= rbound


def begins_with(charset, string, pgenerator):
    """Whether `string` begins with a `charset` character."""
    if charset not in pgenerator.sets.keys():
        raise ValueError('Character set %s is not known.' % charset)
    if not string:
        return False
    return string[0] in pgenerator.sets[charset]


def ends_with(charset, string, pgenerator):
    """Whether `string` ends with a `charset` character."""
    if charset not in pgenerator.sets.keys():
        raise ValueError('Character set %s is not known.' % charset)
    if not string:
        return False
    return string[-1:] in pgenerator.sets[charset]


class TestUseCase(unittest.TestCase):
    """
    Test for several schemes, both valid and faulty.
    """

    def setUp(self):
        self.numbers = 'numbers'
        self.letters = 'letters'

        self.generator = grampg.PasswordGenerator().of()

    def test_at_least_at_most_with_length(self):
        """At least four numbers, at most 10 letters, with a total of 10."""
        gen = (self.generator.length(10)
                             .at_least(4, self.numbers)
                             .at_most(10, self.letters)
                             .done())
        pass1, pass2, pass3 = gen.generate(), gen.generate(), gen.generate()

        # Test the length.
        self.assertEqual(10, len(pass1))
        self.assertEqual(10, len(pass2))
        self.assertEqual(10, len(pass3))
        # Test the numbers.
        numbers_in_range = lambda p: between(4, 10, self.numbers, p, gen)
        self.assertTrue(numbers_in_range(pass1))
        self.assertTrue(numbers_in_range(pass2))
        self.assertTrue(numbers_in_range(pass3))
        # Test the letters.
        letters_in_range = lambda p: between(0, 10, self.letters, p, gen)
        self.assertTrue(letters_in_range(pass1))
        self.assertTrue(letters_in_range(pass2))
        self.assertTrue(letters_in_range(pass3))

    def test_beginning_with_with_tight_length(self):
        """10 numbers with letters, beginning with letters, but totaling 10."""
        gen = (self.generator.exactly(10, 'numbers')
                             .at_most(10, 'letters')
                             .beginning_with('letters')
                             .length(10).done())
        self.assertRaises(grampg.PasswordSpecsError, gen.generate)

    def test_ending_with_with_tight_length(self):
        """10 numbers with letters, ending with letters, but totaling 10."""
        gen = (self.generator.exactly(10, 'numbers')
                             .at_most(10, 'letters')
                             .ending_with('letters')
                             .length(10).done())
        self.assertRaises(grampg.PasswordSpecsError, gen.generate)

    def test_begin_end_tight_length(self):
        """10 numbers with letters, beginning and ending with letters."""
        gen = (self.generator.exactly(10, 'numbers')
                             .at_most(10, 'letters')
                             .ending_with('letters')
                             .beginning_with('letters')
                             .length(10).done())
        self.assertRaises(grampg.PasswordSpecsError, gen.generate)


if __name__ == '__main__':
    unittest.main()
