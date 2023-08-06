"""preprocessors packages"""

__docformat__ = "restructuredtext en"

from apycotlib import ApycotObject

class BasePreProcessor(ApycotObject):
    """an abstract class providing some common utilities for preprocessors
    """
    __type__ = 'preprocessor'

    def run(self, test, path):
        """Run preprocessor against source in <path> in <test> context"""
        raise NotImplementedError()

from apycotlib.preprocessors import distutils
