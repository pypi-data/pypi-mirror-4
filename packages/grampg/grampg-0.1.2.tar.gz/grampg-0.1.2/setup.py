from setuptools import setup

setup(
    name="grampg",
    version="0.1.2",
    packages=['grampg', 'grampg.tests', 'grampg.demo'],

    description="Simple and flexible password generation library.",
    long_description=open('README.txt').read(),

    license="GNU Affero General Public License (LICENSE.txt)",

    test_suite='tests',

    # Metadata for upload to PyPI.
    author="Elvio Toccalino",
    author_email="elvio.toccalino@gmail.com",
    keywords="grumpy admin password generator",
    url="https://bitbucket.org/etoccalino/grampg",
)
