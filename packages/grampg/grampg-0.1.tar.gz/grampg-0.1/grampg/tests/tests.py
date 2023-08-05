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
Unit tests for the grampg components: the PasswordGenerator class and each of
the Spec subclasses.
"""

import unittest

# Import internals for testing.
from grampg import grampg


def string_of_ints(string):
    """Whether `string` is a string of integers."""
    if not isinstance(string, str):
        return False
    for char in string:
        try:
            int(char)
        except TypeError:
            return False
    return True


def this_many_numbers(quantity, string):
    """Whether `string` is a string composed of `quantity` *number* chars."""
    if not string_of_ints(string) or len(string) != quantity:
        return False
    return True


def range_of_numbers(lbound, ubound, string):
    """Whether `string` is a string of a `quantity` *number* chars in range."""
    if not string_of_ints(string):
        return False
    if len(string) < lbound or len(string) > ubound:
        return False
    return True


class TestPasswordGenerator(unittest.TestCase):
    """
    Test creation and setup of the password generator.
    """

    def setUp(self):
        self.password = grampg.PasswordGenerator()

    def test_create_is_instance(self):
        """Creation always succeds."""
        self.assertIsInstance(self.password, grampg.PasswordGenerator)

    def test_create_has_sets_dict(self):
        """Expose a dictionary to easily handle character sets."""
        self.assertIsInstance(self.password.sets, dict)

    def test_of(self):
        """The initial generator instance always succeds."""
        gen = self.password.of()
        self.assertIsInstance(gen, grampg.PasswordGenerator)


class TestSpecsIndividually(unittest.TestCase):
    """
    Tests each spec individually, using the default character sets.
    """

    def setUp(self):
        # Extract the Generator instance from the builder.
        self.gen = grampg.PasswordGenerator().of().generator

    def test_generator_specs(self):
        """A generator exposes a `specs` dictionary."""
        self.assertIsInstance(self.gen.specs, dict)

    # Tests for the `exactly` spec method.

    def test_spec_exactly_instance(self):
        """Creation of spec."""
        self.gen.exactly(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertIsInstance(spec, grampg.CharacterExact)

    def test_spec_exactly_attrs(self):
        """`quantity` attribute is set."""
        self.gen.exactly(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertEqual(spec.low, 3)
        self.assertEqual(spec.high, 3)

    def test_spec_exactly_generate(self):
        """Generate correct number of characters."""
        self.gen.exactly(3, 'numbers')
        self.gen.done()
        res = self.gen.generate()
        self.assertTrue(this_many_numbers(3, res))

    def test_spec_exactly_generate_twice(self):
        """Calling generate twice results in correct characters."""
        self.gen.exactly(3, 'numbers')
        self.gen.done()
        res1 = self.gen.generate()
        res2 = self.gen.generate()
        self.assertTrue(res1, res2)

    # Test for the `between` spec method.

    def test_spec_between_instance(self):
        """Creation of "between" spec."""
        self.gen.between(3, 5, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertIsInstance(spec, grampg.CharacterRange)

    def test_spec_between_attrs(self):
        """`low` and `high` attributes are set in the spec."""
        self.gen.between(3, 5, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertEqual(spec.low, 3)
        self.assertEqual(spec.high, 5)

    def test_spec_between_generate(self):
        """Generate correct number of attributes."""
        self.gen.between(3, 5, 'numbers')
        self.gen.done()
        res = self.gen.generate()
        self.assertTrue(range_of_numbers(3, 5, res))

    # Test for the `at_least' spec method.

    def test_spec_at_least_instance(self):
        """Creation of the `between` spec."""
        self.gen.at_least(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertIsInstance(spec, grampg.CharacterRange)

    def test_spec_at_least_attrs(self):
        """When only lower bound is given the spec is not initialized."""
        self.gen.at_least(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertFalse(spec.initialized)

    def test_spec_at_least_generate(self):
        """Generate with no upper bound should fail."""
        self.gen.at_least(3, 'numbers')
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    def test_spec_at_least_generate_twice(self):
        """Calling generate twice results in two exceptions."""
        self.gen.at_least(3, 'numbers')
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    # Test for the `at_most` spec method.

    def test_spec_at_most_instance(self):
        """Creation of the `between` spec."""
        self.gen.at_most(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertIsInstance(spec, grampg.CharacterRange)

    def test_spec_at_most_attrs(self):
        """`high` attribute is set in the spec (disregard `low`)."""
        self.gen.at_most(3, 'numbers')
        spec = self.gen.specs['numbers']
        self.assertEqual(spec.high, 3)

    def test_spec_at_most_generate(self):
        """Generate with no lower bound should generate an empty string."""
        self.gen.at_most(3, 'numbers')
        self.gen.done()
        res = self.gen.generate()
        self.assertEqual(res, '')

    def test_spec_at_most_generate_twice(self):
        """Calling generate twice results in two empty strings."""
        self.gen.at_most(3, 'numbers')
        self.gen.done()
        res1 = self.gen.generate()
        res2 = self.gen.generate()
        self.assertEqual(res1, res2)

    # Tests for the `length` spec method.

    def test_length_type(self):
        """Length must be an int."""
        self.assertRaises(ValueError, lambda: self.gen.length('lenght'))

    def test_length_number(self):
        """Lenght must be a natural number."""
        self.assertRaises(ValueError, lambda: self.gen.length(0))
        self.assertRaises(ValueError, lambda: self.gen.length(-2))

    def test_length_empty(self):
        """Specifying only the length generates an empty string."""
        self.gen.length(2)
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    # Tests for `beginning_with` spec method.

    def test_beginning_with_empty(self):
        """Specifying only the beginning is invalid."""
        self.gen.beginning_with('numbers')
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    def test_beginning_with_nonregistered_set(self):
        """Character set must be registered."""
        self.assertRaises(grampg.PasswordSpecsError,
                          lambda: self.gen.beginning_with('nothing'))

    # Tests for `ending_with` spec method.

    def test_ending_with_single(self):
        """Specifying only ending_with is invalid."""
        self.gen.ending_with('numbers')
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    def test_ending_with_nonregistered_set(self):
        """Character set must be registered."""
        self.assertRaises(grampg.PasswordSpecsError,
                          lambda: self.gen.ending_with('nothing'))

    # Tests for `done` spec method.

    def test_just_done(self):
        """No char sets associated raises validation error."""
        self.assertRaises(grampg.PasswordSpecsError, self.gen.done)

    def test_done_idempotency(self):
        """Calling done after done in a valid generator has no effect."""
        self.gen.exactly(3, 'numbers')
        self.gen.done()
        self.gen.done()
        self.gen.done()

    def test_done_freezes_generator(self):
        """No more specs allowed after done is called."""
        self.gen.exactly(3, 'numbers')
        self.gen.done()
        self.assertRaises(grampg.PasswordSpecsError,
                          lambda: self.gen.length(3))


if __name__ == '__main__':
    unittest.main()
