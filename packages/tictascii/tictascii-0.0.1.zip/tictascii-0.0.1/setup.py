from distutils.core import setup

setup(
    name='tictascii',
    version='0.0.1',
    author='Free Riders',
    author_email='fred+freeriders@pyth.net',
    packages=['tictascii', 'tictascii.ticlib'],
    scripts=[],
    url='https://github.com/enginous/tictascii',
    description='Synergetically revolutionalizing mobile Tic Tac Toe in the cloud.',
    long_description=open('README').read(),
)