import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

py_version = sys.version_info[:2]

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, "README.md")).read()
except IOError:
    README = ""

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name="Rockefeller",
      version="1.0",
      description="Currencies and exchange rates library.",
      long_description=README,
      author="Floqq",
      author_email="anler@floqq.com",
      url="http://github.com/Floqq/Rockefeller/",
      license="MIT",
      tests_require=["pytest"],
      cmdclass={"test": PyTest},
      keywords="money currency exchange rates",
      classifiers=[
          "Environment :: Plugins",
          "Environment :: Console",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Intended Audience :: Financial and Insurance Industry",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Office/Business :: Financial"])

