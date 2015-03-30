import argparse
import os
import setuptools
import sys

class FunctionalTests(setuptools.Command):
    user_options = [
        ('url=', None, 'Local Discourse URL.'),
        ('apikey=', None, 'Specify the api key.')
    ]

    def run(self):
        os.system("nose2 -s functional_tests")

    def initialize_options(self):
        self.url = None
        self.apikey = None

    def finalize_options(self):
        assert self.url is not None
        assert self.apikey is not None

        os.environ['DISCOURSE_URL'] = self.url
        os.environ['DISCOURSE_API_KEY'] = self.apikey
