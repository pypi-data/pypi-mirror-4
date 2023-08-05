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
Usecase tests, part of the grampg test suite.
"""

import unittest

# Import internals for testing.
from grampg import grampg


def how_many(charset, string, pgenerator):
    """Return how many of `kind` are in `string`."""
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
        self.lower_letters = 'lower_letters'
        self.numbers = 'numbers'
        self.upper_letters = 'upper_letters'

        self.generator = grampg.PasswordGenerator().of()

    def test_five_lower_letters(self):
        """Five lower letters."""
        res = self.generator.exactly(5, self.lower_letters).done().generate()
        self.assertEqual(5, len(res))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))

    def test_five_lower_letters_and_five_numbers(self):
        """Five lower letters and five numbers."""
        res = (self.generator.exactly(5, self.lower_letters)
                             .exactly(5, self.numbers).done().generate())
        self.assertEqual(10, len(res))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))
        self.assertEqual(5, how_many(self.numbers, res, self.generator))

    def test_five_lower_letters_and_five_numbers_bad_length(self):
        """Five lower letters and five numbers, with a bad length."""
        gen = (self.generator.exactly(5, self.lower_letters)
                             .exactly(5, self.numbers)
                             .length(8))
        self.assertRaises(grampg.PasswordSpecsError, gen.done)

    def test_five_lower_letters_and_two_to_five_numbers(self):
        """Five lower letters and two to five numbers."""
        res = (self.generator.exactly(5, self.lower_letters)
                             .between(2, 5, self.numbers).done().generate())
        self.assertTrue(7 <= len(res) and len(res) <= 10)
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))
        self.assertTrue(between(2, 5, self.numbers, res, self.generator))

    def test_five_lower_letters_and_two_to_five_numbers_with_length(self):
        """Five lower letters and two to five numbers with length in range."""
        res = (self.generator.exactly(5, self.lower_letters)
                             .between(2, 5, self.numbers)
                             .length(8).done().generate())
        self.assertEqual(8, len(res))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))
        self.assertEqual(3, how_many(self.numbers, res, self.generator))

    def test_five_lower_letters_two_to_five_num_with_length_and_begin(self):
        """Five lower letters and two to five numbers, beginning with a lower
        letter with length in range."""
        res = (self.generator.exactly(5, self.lower_letters)
                             .between(2, 5, self.numbers)
                             .beginning_with(self.lower_letters)
                             .length(8).done().generate())
        self.assertEqual(8, len(res))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))
        self.assertEqual(3, how_many(self.numbers, res, self.generator))
        self.assertTrue(begins_with(self.lower_letters, res, self.generator))

    def test_five_lower_letters_and_two_to_five_num_with_length_and_ends(self):
        """Five lower letters and two to five numbers, ending with a lower
        letter with length in range."""
        res = (self.generator.exactly(5, self.lower_letters)
                             .between(2, 5, self.numbers)
                             .ending_with(self.lower_letters)
                             .length(8).done().generate())
        self.assertEqual(8, len(res))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))
        self.assertEqual(3, how_many(self.numbers, res, self.generator))
        self.assertTrue(ends_with(self.lower_letters, res, self.generator))

    def test_five_lower_letters_bad_length(self):
        """Five lower letter, with bad length."""
        gen = self.generator.exactly(5, self.lower_letters).length(8)
        self.assertRaises(grampg.PasswordSpecsError, gen.done)

    def test_two_to_five_lower_letters_bad_length(self):
        """Two to five lower letter, with bad length."""
        gen = self.generator.between(2, 5, self.lower_letters).length(8)
        self.assertRaises(grampg.PasswordSpecsError, gen.done)

    def test_five_numbers_and_at_least_eight_lower_letters(self):
        """Five numbers and at least eight lower letters... but how long."""
        gen = (self.generator.exactly(5, self.numbers)
                             .at_least(8, self.lower_letters))
        # No way of saying how many characters in total.
        self.assertRaises(grampg.PasswordSpecsError, gen.done)

    def test_five_numbers_and_at_least_eight_lower_letters_with_length(self):
        """Five numbers and at least eight lower letters, with length."""
        res = (self.generator.exactly(5, self.numbers)
                             .at_least(8, self.lower_letters)
                             .length(15)
                             .done()
                             .generate())
        self.assertEqual(15, len(res))
        self.assertEqual(5, how_many(self.numbers, res, self.generator))
        self.assertEqual(10, how_many(self.lower_letters, res, self.generator))

    def test_five_numbers_and_at_most_eight_lower_letters(self):
        """Five numbers and at most eight lower letters."""
        res = (self.generator.exactly(5, self.numbers)
                             .at_most(8, self.lower_letters)
                             .done()
                             .generate())
        # Minimum password length.
        self.assertEqual(5, len(res))
        self.assertEqual(5, how_many(self.numbers, res, self.generator))
        self.assertEqual(0, how_many(self.lower_letters, res, self.generator))

    def test_five_num_and_at_most_eight_lower_letters_with_good_length(self):
        """Five numbers and at most eight lower letters, with length."""
        res = (self.generator.exactly(5, self.numbers)
                             .at_most(8, self.lower_letters)
                             .length(10)
                             .done()
                             .generate())
        # Minimum password length.
        self.assertEqual(10, len(res))
        self.assertEqual(5, how_many(self.numbers, res, self.generator))
        self.assertEqual(5, how_many(self.lower_letters, res, self.generator))

    def test_five_num_and_at_most_eight_lower_letters_with_bad_length(self):
        """Five numbers and at most eight lower letters, with bad length."""
        gen = (self.generator.exactly(5, self.numbers)
                             .at_most(8, self.lower_letters)
                             .length(14))
        # Not enough characters.
        self.assertRaises(grampg.PasswordSpecsError, gen.done)


if __name__ == '__main__':
    unittest.main()
