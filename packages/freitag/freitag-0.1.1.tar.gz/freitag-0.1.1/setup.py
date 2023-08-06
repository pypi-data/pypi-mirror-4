from distutils.core import setup

setup(
    name='freitag',
    version='0.1.1',
    author='G. Capizzi',
    author_email='g.capizzi@gmail.com',
    packages=['freitag'],
    scripts=['bin/freitag'],
    url='https://github.com/gcapizzi/freitag',
    license='COPYING.txt',
    description='A command-line tool for MP3 tagging and renaming.',
    install_requires=[
        "argparse >= 1.2.1",
        "mutagen >= 1.2.0",
    ],
)
