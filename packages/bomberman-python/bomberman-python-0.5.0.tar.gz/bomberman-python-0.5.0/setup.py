import os.path
from distutils.core import setup

readme = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(readme).read()

setup(
    name='bomberman-python',
    version='0.5.0',
    summary='Python client for interacting with Bomberman profanity filtering HTTP API.',
    home_page='http://bomberman.ikayzo.com',
    author='Ikayzo',
    author_email='bomberman-support@ikayzo.com',
    packages=['bomberman',],
    license='MIT',
    long_description=long_description
)
