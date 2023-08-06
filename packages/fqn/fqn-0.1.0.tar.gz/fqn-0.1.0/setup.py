from setuptools import setup, find_packages

setup(
    name = 'fqn',
    version = '0.1.0',
    description = 'Functions that can retrieve objects using Fully Qualified Names',
    author = 'Brian Lauber',
    author_email = 'constructible.truth@gmail.com',
    packages = find_packages(exclude = ["tests", "tests.*"]),
    test_suite = 'tests',
    tests_require = ["mock>=1.0.0"]
)

