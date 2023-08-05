from distutils.core import setup

setup(
    name='HNComments',
    version='0.1',
    author='Richard Delaney',
    author_email='richdel1991@gmail.com',
    packages=['hncomments', 'hncomments.test'],
    scripts=['bin/commentfromurl.py'],
    url='http://pypi.python.org/pypi/HNComments/',
    license='LICENSE.txt',
    description='A tiny python library which converts urls to hn comment url',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests == 1.0.0"
    ],
)
