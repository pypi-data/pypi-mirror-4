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
Defines the exception hierarchy, helper funtions and the main classes.

The exception hierarchy is based on :exc:`PasswordSpecsError`, extended by
:exc:`PasswordSpecsNonValidatedError` and :exc:`PasswordGeneratorIsDone` to
signal improper usage.

For details about the password generation algorithm read the grampg/docs.

Use the :class:`PasswordGenerator` as interface.
"""

import random


class PasswordSpecsError(Exception):
    """
    Root of grampg exceptions.

    Itself used to signal errors during specification or validation of a
    generator.
    """
    pass


class PasswordSpecsNonValidatedError(PasswordSpecsError):
    """
    Raised when :meth:`~Generator.generate` is called on a generator before a
    it is *done*.
    """
    pass


class PasswordGeneratorIsDone(PasswordSpecsError):
    """
    Raised when a new specification is attempted on a *done* generator.
    """
    pass


###############################################################################


def infinite_iter(character_set):
    """Transform a character set into a generator-iterator.

    Each value yielded is a :func:`random.choice` on the `character_set`."""
    if not character_set:
        return
    # yield forever.
    while True:
        yield random.choice(character_set)


def choice_of_spec(specs):
    """Return a random spec element from the sequence of `specs`.

    The probability of picking a particular spec is directly dependant on the
    `len` of its associated character set (expected at spec.set).

    Raises :exc:`~exception.ValueError` if `specs` is an empty sequence.
    """
    if not specs:
        raise ValueError('specs must not be empty.')
    sample = sum(len(spec.set) for spec in specs)
    choice = random.randint(1, sample)
    for spec in specs:
        spec_len = len(spec.set)
        if choice <= spec_len:
            return spec
        choice -= spec_len


###############################################################################


class Spec(object):
    """
    An iterator-like object which choses randomly from the character set.

    Not meant to be used, but subclassed. This class defines the internal state
    of *specs*, and the API each should provide.
    """

    def __init__(self, character_set, low=0, high=0):
        """Prepare the iteration.

        The default values of `low` and `high` are so that these can be
        accumulated over multiple specs, to produce *minimum* and *maximum*
        length, if desired.

        Positional arguments:
        character_set -- the character set to chose from.
        low -- the lower bound of the spec (default 0).
        high -- the upper bound of the spec (default 0).
        """
        self.low = low
        self.high = high
        self.set = character_set
        # Initialize the character generator-iterator.
        self.chars = infinite_iter(character_set)
        # Characters yielded so far.
        self.yielded = 0
        # Syntax sugar.
        self.another_character = self.next

    def in_range(self):
        """Whether the amount of chars yielded so far satisfy this spec."""
        return self.low <= self.yielded and self.yielded <= self.high

    def reset(self):
        """Reset internal state, the count of yielded characters."""
        self.yielded = 0

    def next(self):
        """Return next randomly chosen char in the set."""
        if self.yielded == self.high:
            raise StopIteration()
        self.yielded += 1
        return self.chars.next()

    def __iter__(self):
        return self

    def fix(self, full_length=None):
        """Fix the range of the spec."""
        raise NotImplementedError()


class CharacterExact(Spec):
    """
    Specify an exact number of characters for a particular set.
    """

    def __init__(self, character_set, quantity):
        """Initialize the spec.

        Positional arguments:
        character_set -- the character set to chose characters from.
        quantity -- the (positive integer) number of characters to chose.

        Raises :exc:`ValueError` if ``quantity`` is not a positive integer.
        """
        if type(quantity) != int or quantity < 0:
            raise ValueError("quantity must be a non-negative integer.")

        # self.low and self.high are both set to quantity.
        super(CharacterExact, self).__init__(character_set, quantity, quantity)

    def fix(self, full_length=None):
        """Exact specs are always fixed."""
        pass


class CharacterRange(Spec):
    """
    Specify a numeric range for the number of characters for a character set.

    The range may be open at lower or upper bound, but not both. Use the
    :meth:`fix` operation to turn the range into a closed one, suitable to be
    used during generation. Notice that you can only fix the upper bound of a
    range if the total length of the password has been specified (via a call to
    :meth:`length`).
    """

    def __init__(self, character_set, low=None, high=None):
        """Initialize the spec.

        Positional parameters:
        character_set -- the identifier of the charset to chose chars from.
        low -- the optional positive integer minimum number of chars to chose.
        high -- the optional positive integer maximum number of chars to chose.

        Although optional, either low or high (or both) must be provided.

        Raises :exc:`ValueError` if either ``low`` or ``high`` (which ever is
        given, or both) is not a positive integer.
        """
        # By default consider closed ranges.
        self.initialized = True

        if high is not None:
            if type(high) != int or high < 0:
                raise ValueError("high must be a positive integer.")
            if low is not None:
                if type(low) != int or low < 0:
                    raise ValueError("low must be a positive integer.")
                super(CharacterRange, self).__init__(character_set, low, high)
            else:
                super(CharacterRange, self).__init__(character_set, high=high)
        elif low is not None:
            if type(low) != int or low < 0:
                raise ValueError("low must be a positive integer.")
            # An unbound range cannot be initialize. Should be fixed.
            # Temporary storage.
            self.low = low
            self.character_set = character_set
            self.initialized = False
        else:
            raise PasswordSpecsError("Either low or high bound"
                                     " must be specified.")

    def fix(self, full_length=None):
        """Force upper bound to have a meaningful value... or error out."""
        if not self.initialized:
            # Fix the upper bound.
            high = self.low
            if full_length:
                high = full_length

            super(CharacterRange, self).__init__(self.character_set,
                                                 self.low, high)
            self.initialized = True


###############################################################################


class Generator:
    """
    The generator object.

    A generator instance undergoes three phases during its existance: create it
    with the character sets to choose from, specify it by calling its methods
    finalizing in a call to :meth:`done`, and generate passwords
    with it by calling its :meth:`generate` method.

    Character sets should not be modified once the generator is
    instantiated. If other character sets are required, a new instance should
    be used.

    During the specification, repeated calls to the same method (consecutively
    or otherwise) overrides previous calls, so it is not an error to call them
    more than once. Specification is over after a call :meth:`~Generator.done`
    succeds. Once *done*, the generator cannot be further spec'ed, and only
    calls to :meth:`generate` are valid (although it is possible to call
    :meth:`done` over and over again, it does not have effect).

    Any attempt to add new specs to a *done* generator will raise
    :exc:`PasswordGeneratorIsDone`.

    .. note::

       Generator instances should be built by means of
       :class:`PasswordGenerator`, and only the :meth:`generate` method should
       ever be directly called on instances of this class.
    """

    def __init__(self, sets):
        """Initialize the generator with the character sets to use.

        Positional parameters:
        * the character sets to be used.
        """
        self.sets = sets
        self._length = None

        self.begins_with = None
        self.ends_with = None

        # When the generator is done, no more specs will be allowed.
        self._done = False

        # Collect the spacs as they come.
        self.specs = {}

    def _validate(self, setname):
        if self._done:
            raise PasswordGeneratorIsDone()
        if setname not in self.sets:
            raise PasswordSpecsError('Unknown character set.')

    def length(self, length):
        """Set the length of generated passwords."""
        if self._done:
            raise PasswordGeneratorIsDone()

        if type(length) != int or length < 1:
            raise ValueError('Length must a natural number.')
        self._length = length

    def exactly(self, quantity, setname):
        """
        Specify an exact amount of characters for this set to be included in
        the generated passwords.
        """
        self._validate(setname)
        self.specs[setname] = CharacterExact(self.sets[setname], quantity)

    def some(self, setname):
        """Specify an inexact number of characters to include in passwords."""
        self._validate(setname)
        self.specs[setname] = CharacterRange(self.sets[setname], low=0)

    def between(self, low, high, setname):
        """
        Specify an fixed range of characters for this set to be included in
        the generated passwords.
        """
        self._validate(setname)
        self.specs[setname] = CharacterRange(self.sets[setname], low, high)

    def at_least(self, low, setname):
        """
        Specify the minimum amount of characters for this set to be included in
         the generated passwords.
         """
        self._validate(setname)
        self.specs[setname] = CharacterRange(self.sets[setname], low=low)

    def at_most(self, high, setname):
        """
        Specify the maximum amount of characters for this set to be included in
        the generated passwords.
        """
        self._validate(setname)
        self.specs[setname] = CharacterRange(self.sets[setname], high=high)

    def beginning_with(self, setname):
        """The password should begin with a character from this set."""
        self._validate(setname)
        self.begins_with = setname

    def ending_with(self, setname):
        """The password should end with a character from this set."""
        self._validate(setname)
        self.ends_with = setname

    def done(self):
        """Signals that the generator is ready to start producing passwords.

        Note that this call *freezes* or *marks* the generator object, which
        will not be able to receive further specs. A successful call to `done`
        must be made before :meth:`generate` can be called.

        This method is idempotent and irreversible.

        Raises :exc:`PasswordSpecsError` if validation of the specs fails.
        """
        if self._done:
            return

        if not self.specs:
            raise PasswordSpecsError("No character set spec is associated to"
                                     " this generator.")

        # Minimum length spec'ed, which is expected by generate().
        min_length = 0
        # Maximum length spec'ed, which is expected by generate().
        max_length = 0
        # Fix and accumulate minimum and maximum lengths
        for spec in self.specs.values():
            spec.fix(full_length=self._length)

            min_length += spec.low
            max_length += spec.high

        # Length validation of the specifications.
        if self._length and (self._length < min_length
                             or self._length > max_length):
            raise PasswordSpecsError('Length value specified is not'
                                     ' compatible with the other specs.')

        # Begin/end specifications validation.
        for spec in ['begins_with', 'ends_with']:
            setname = getattr(self, spec)
            if setname:
                if setname not in self.specs.keys():
                    raise PasswordSpecsError('beginning_with/ending_with'
                                             ' specifies bad character set'
                                             ' "%s"' % setname)
                if self.specs[setname].high < 1:
                    raise PasswordSpecsError('"%s" character set cannot '
                                             'fulfill beginning_with/'
                                             'ending_with spec.' % setname)

        # Mark generator as *done*, will not receive further specs.
        self._done = True

    def generate(self):
        """Return one generated password based on the collected specs.

        Can be called any number of times, each yielding a new, independant
        password.

        Raises :exc:`PasswordSpecsNonValidatedError` if the generator is not
        *done* (the :meth:`done` method has not yet been called).
        Raises :exc:`PasswordSpecError` if frame spec methods (``length``,
        ``beginning_with`` ``ending_with``) collide.
        """

        # Validate the specifications are done.
        if not self._done:
            raise PasswordSpecsNonValidatedError(
                "generate() called before done().")

        # Edge case: no character specs (only length, begin or end).
        if not self.specs:
            return ''

        # First, satisfy the minimum length specificated.

        # mins collects the minimum acceptable result from each spec.
        begins_with_char = ''
        ends_with_char = ''
        mins = []
        running_length = 0
        for spec_name, spec in self.specs.items():
            try:
                # Notice if this happens to be the one to begin the result.
                if self.begins_with == spec_name:
                    begins_with_char = spec.another_character()
                    running_length += 1
                # Or in case it's the one to end it.
                if self.ends_with == spec_name:
                    ends_with_char = spec.another_character()
                    running_length += 1
            except StopIteration:
                raise PasswordSpecsError("Bad spec beginning_with/ending_with"
                                         " %s character set." % spec_name)

            # Get a minimum amount of characters to satisfy this spec.
            chars = []
            while not spec.in_range():
                chars.append(spec.another_character())
                running_length += 1
            mins.append(chars)

        # Get all chars chosen so far, from all sets, into a bag.
        bag = []
        for chars in mins:
            bag.extend(chars)

        # The minimum length of all specs might not suit the specified length.

        if self._length and running_length < self._length:
            # To advance the length of the password, chose randomly
            # a specified character set and select another character.
            remaining_specs = [spec for spec in self.specs.values()
                               if spec.in_range()]
            while running_length < self._length:
                chosen_spec = choice_of_spec(remaining_specs)
                # Check the character sets, so as to remove capped ones.
                try:
                    bag.append(chosen_spec.another_character())
                    running_length += 1
                except StopIteration:
                    # Spec has reached maximum number of tolerated chars.
                    remaining_specs.remove(chosen_spec)

        # Shuffle the bag to produce the output password.
        random.shuffle(bag)
        password = ''.join(bag)

        # Add the first and/or last chars if length is not tight.
        password = begins_with_char + password + ends_with_char
        if self._length:
            # Length was specified, so check if there's an error in the specs.
            if self._length != len(password):
                raise PasswordSpecsError("Password length is incorrect (check"
                                         " beginning_with/ending_with specs)")

        # Before terminating, reset the internal state of the specs.
        for spec in self.specs.values():
            spec.reset()

        return password


class PasswordGenerator:
    """
    Build the password generator.

    Provides a fluent interface to build :class:`Generator` instances, by means
    of method chaining.

    Exposes the character sets. Default character sets are provided for upper
    and lower case letters (`upper_letters` and `lower_letters`, respectively,
    all mashed up in `letters`) and `numbers`. A conjunction of the three is
    also provided, under the name `alphanumeric`.

    A character set can be registered by keying its name to a list of eligible
    characters in the :attr:`sets` attribute, or by extending the default
    character sets during instantiation.
    """

    _lower_letters = 'abcdefghijklmnopqrstuvwxyz'
    _upper_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _numbers = '1234567890'
    _letters = _lower_letters + _upper_letters
    _alpha = _letters + _numbers

    def __init__(self, from_sets={}):
        """Allow extra character sets to be registered.

        Keyword paramenters:
        from_sets: a dict of char set name to list of chars (default is {}).
        """
        self.sets = {
            'lower_letters': list(PasswordGenerator._lower_letters),
            'upper_letters': list(PasswordGenerator._upper_letters),
            'letters': list(PasswordGenerator._letters),
            'numbers': list(PasswordGenerator._numbers),
            'alphanumeric': list(PasswordGenerator._alpha),
            }
        self.sets.update(from_sets)
        self.generator = None

    def of(self):
        """Commence a method chain building a fresh generator instance.

        The generator instanciated by this call is new, but the character sets
        fed to it are always the same (the ones configured during
        :meth:`__init__`). If a different character set is desired, a new
        instance of :class:`PasswordGenerator` is neccessary.

        The generator will be finalized by a :meth:`done` call, and
        then used by calling :meth:`~Generator.generate` on it.
        """
        self.generator = Generator(self.sets)
        return self

    def length(self, length):
        """*Spec method*: adjust the total length of passwords to generate."""
        self.generator.length(length)
        return self

    def exactly(self, quantity, setname):
        """*Spec method*: require exactly this many characters from the set."""
        self.generator.exactly(quantity, setname)
        return self

    def some(self, setname):
        """*Spec method*: use characters from the set, if they fit."""
        self.generator.some(setname)
        return self

    def between(self, low, high, setname):
        """
        *Spec method*: require no less than `low` but no more than `high`
        characters from that set. This spec defines a range of characters.
        """
        self.generator.between(low, high, setname)
        return self

    def at_least(self, low, setname):
        """
        *Spec method*: require no less than `low` but no more than `high`
        characters from that set. This spec defines a range of characters.
        """
        self.generator.at_least(low, setname)
        return self

    def at_most(self, high, setname):
        """
        *Spec method*: require no more than `high` characters from that
        set. This spec defines a range of characters.
        """
        self.generator.at_most(high, setname)
        return self

    def beginning_with(self, setname):
        """*Spec method*: passwords will start with a char from this set.

        Some other *spec method* must be called to define a number or range for
        that same set. Beginning with characters not specified is an error.
        """
        self.generator.beginning_with(setname)
        return self

    def ending_with(self, setname):
        """*Spec method*: passwords will end with a char from this set.

        Some other *spec method* must be called to define a number or range for
        that same set. Ending with characters not specified is an error.
        """
        self.generator.ending_with(setname)
        return self

    def done(self):
        """Finalize the generator and return it.

        The returned instance can receive calls to :meth:`~Generator.generate`,
        each of which will produce an independent password complying with the
        specs.
        """
        self.generator.done()
        return self.generator
