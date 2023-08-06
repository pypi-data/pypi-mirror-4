from setuptools import setup, find_packages

setup(
    name='ircbot',
    version="0.1dev",
    packages=find_packages(),
    author='Stephen McQuay',
    author_email='stephen@mcquay.me',
    install_requires=['Twisted'],
    entry_points={'console_scripts': [
        'ircbot = ircbot.main:main',
    ]},
    url='https://bitbucket.org/smcquay/ircbot',
    license='WTFPL',
    description= (
        'a rather simple echo irc bot to stand as a simple example of how '
        'this could be done.'),
    long_description=open('README.rst').read(),
)
