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
grampg package interface.

The `PasswordGenerator` class allows to build generators though a
fluent interface, by chaining methods to declare user specifications,
culminated to a call to `PasswordGenerator.done`. During this last
call, specs are validated, and a `PasswordSpecsError` is raised if
validation fails.
"""

from grampg import PasswordGenerator, PasswordSpecsError
from grampg import PasswordGeneratorIsDone
from grampg import PasswordSpecsNonValidatedError
